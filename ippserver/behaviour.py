import logging
import os
import os.path
import random
import json
import subprocess
import time
import uuid
import datetime
import threading
import io
import socket
import tempfile
import gzip
import zlib
import re
from collections import defaultdict

from .parsers import Integer, Enum, Boolean, DateTime, Resolution, RangeOfInteger
from .constants import (
    JobStateEnum, OperationEnum, StatusCodeEnum, SectionEnum, TagEnum,
    PrinterStateEnum, PrinterStateReasonsEnum, IppVersionEnum,
    PrintQualityEnum, PrintColorModeEnum, ColorSupportedEnum
)
from .ppd import BasicPdfPPD
from .request import IppRequest
from .pdf_converter import convert_to_pdf

# 导入翻译函数 - Import translation function
try:
    from .translations import t
except ImportError:
    # 如果翻译模块不存在，创建一个简单的替代函数 - If translation module doesn't exist, create a simple fallback
    def t(key, **kwargs):
        return key


def get_job_id(req):
    return Integer.from_bytes(
        req.only(
            SectionEnum.operation,
            b'job-id',
            TagEnum.integer
        )
    ).integer


def prepare_environment(ipp_request):
    env = os.environ.copy()
    env["IPP_JOB_ATTRIBUTES"] = json.dumps(
        ipp_request.attributes_to_multilevel(SectionEnum.job)
    )
    return env


def create_ipp_datetime(timestamp=None):
    """Create IPP DateTime format from timestamp - 从时间戳创建IPP DateTime格式"""
    if timestamp is None:
        timestamp = time.time()
    dt = DateTime(timestamp)
    return dt.bytes()


def validate_ipp_version(version_major, version_minor):
    """Validate IPP version - 验证IPP版本"""
    version_code = (version_major << 8) | version_minor
    supported_versions = [IppVersionEnum.v1_1, IppVersionEnum.v2_0, IppVersionEnum.v2_1, IppVersionEnum.v2_2]
    return version_code in [v.value for v in supported_versions]


def decompress_data(data, compression_type):
    """解压缩数据 - Decompress data"""
    try:
        if compression_type == 'gzip':
            logging.info(t('decompressing_gzip'))
            return gzip.decompress(data)
        elif compression_type == 'deflate':
            logging.info(t('decompressing_deflate'))
            # 尝试zlib解压缩（带头部）- Try zlib decompression (with header)
            try:
                return zlib.decompress(data)
            except zlib.error:
                # 尝试不带头部的解压缩 - Try decompression without header
                return zlib.decompress(data, -15)
        elif compression_type == 'zip':
            logging.info(t('decompressing_zip'))
            import zipfile
            with zipfile.ZipFile(io.BytesIO(data)) as zip_file:
                # 获取第一个文件 - Get first file
                file_list = zip_file.namelist()
                if file_list:
                    return zip_file.read(file_list[0])
                else:
                    raise ValueError(t('zip_file_empty'))
        elif compression_type == 'none' or not compression_type:
            logging.info(t('no_compression_applied'))
            return data
        else:
            logging.warning(t('unsupported_compression_type', type=compression_type))
            return data
    except Exception as e:
        logging.error(t('error_decompressing_data', type=compression_type, error=str(e)))
        raise


# 从 __init__.py 导入打印机配置 - Import printer configuration from __init__.py
from . import (
    DEFAULT_PRINTER_UUID, DEFAULT_PRINTER_NAME, DEFAULT_PRINTER_DESCRIPTION,
    DEFAULT_PRINTER_LOCATION, DEFAULT_PRINTER_URI
)


class JobManager:
    """Manage print jobs with proper state transitions - 使用正确的状态转换管理打印作业"""
    
    def __init__(self):
        self.jobs = {}  # job_id -> job_info
        self.next_job_id = 1
        self.job_lock = threading.RLock()
    
    def create_job(self, job_name=None, user_name=None):
        with self.job_lock:
            job_id = self.next_job_id
            self.next_job_id += 1
            
            job_info = {
                'job_id': job_id,
                'state': JobStateEnum.pending,
                'state_reasons': [b'job-incoming'],
                'creation_time': time.time(),
                'processing_time': None,
                'completion_time': None,
                'job_name': job_name or f'Job {job_id}',
                'user_name': user_name or 'unknown',
                'attributes': {},
                'document_data': None,
                'document_size': 0,
                'document_format': None,
                'compression_type': None
            }
            
            self.jobs[job_id] = job_info
            return job_id, job_info
    
    def update_job_state(self, job_id, new_state, state_reasons=None):
        with self.job_lock:
            if job_id not in self.jobs:
                return False
            
            job = self.jobs[job_id]
            old_state = job['state']
            
            # Validate state transition - 验证状态转换
            valid_transitions = {
                JobStateEnum.pending: [JobStateEnum.pending_held, JobStateEnum.processing, JobStateEnum.canceled],
                JobStateEnum.pending_held: [JobStateEnum.pending, JobStateEnum.processing, JobStateEnum.canceled],
                JobStateEnum.processing: [JobStateEnum.processing_stopped, JobStateEnum.completed, 
                                         JobStateEnum.canceled, JobStateEnum.aborted],
                JobStateEnum.processing_stopped: [JobStateEnum.processing, JobStateEnum.canceled, JobStateEnum.aborted],
                JobStateEnum.completed: [],  # terminal state - 终止状态
                JobStateEnum.canceled: [],   # terminal state - 终止状态
                JobStateEnum.aborted: []     # terminal state - 终止状态
            }
            
            if new_state not in valid_transitions.get(old_state, []):
                logging.warning(t('invalid_state_transition', old=old_state, new=new_state))
                return False
            
            job['state'] = new_state
            
            if state_reasons:
                job['state_reasons'] = state_reasons
            
            # Update timestamps - 更新时间戳
            current_time = time.time()
            if new_state == JobStateEnum.processing and old_state in [JobStateEnum.pending, JobStateEnum.pending_held]:
                job['processing_time'] = current_time
            elif new_state in [JobStateEnum.completed, JobStateEnum.canceled, JobStateEnum.aborted]:
                job['completion_time'] = current_time
            
            return True
    
    def get_job(self, job_id):
        with self.job_lock:
            return self.jobs.get(job_id)
    
    def delete_job(self, job_id):
        with self.job_lock:
            if job_id in self.jobs:
                del self.jobs[job_id]
                return True
            return False
    
    def list_jobs(self, which_jobs='completed', my_jobs=False, limit=None):
        with self.job_lock:
            jobs = list(self.jobs.values())
            
            # Filter by state - 按状态过滤
            if which_jobs == 'completed':
                jobs = [j for j in jobs if j['state'] == JobStateEnum.completed]
            elif which_jobs == 'not-completed':
                jobs = [j for j in jobs if j['state'] != JobStateEnum.completed]
            
            # Sort by creation time (newest first) - 按创建时间排序（最新的在前）
            jobs.sort(key=lambda x: x['creation_time'], reverse=True)
            
            # Apply limit - 应用限制
            if limit:
                jobs = jobs[:limit]
            
            return jobs


class Behaviour(object):
    """Do anything in response to IPP requests - 响应IPP请求执行任何操作"""
    supported_versions = [(1, 1)]  # Default to IPP 1.1 - 默认为IPP 1.1
    
    def __init__(self, ppd=BasicPdfPPD(), uri=DEFAULT_PRINTER_URI, 
                 name=DEFAULT_PRINTER_NAME, description=DEFAULT_PRINTER_DESCRIPTION,
                 location=DEFAULT_PRINTER_LOCATION, printer_uuid=DEFAULT_PRINTER_UUID):
        self.ppd = ppd
        if not uri.endswith('/'): 
            uri += '/'
        self.base_uri = uri.encode('ascii')
        self.printer_uri = (uri + 'ipp/print').encode('ascii')
        
        # 使用DEFAULT_PRINTER_NAME作为打印机名称（支持中文）- Use DEFAULT_PRINTER_NAME as printer name (supports Chinese)
        self.printer_name = name.encode('utf-8')
        self.printer_description = description.encode('utf-8')
        self.printer_location = location.encode('utf-8')
        self.printer_uuid = ('urn:uuid:' + printer_uuid).encode('ascii')
        
        self.job_manager = JobManager()
        self.printer_state = PrinterStateEnum.idle
        self.printer_state_reasons = [b'none']
        self.printer_uptime_start = time.time()
        self.queued_job_count = 0
        self.currently_processing_jobs = set()
        
        # IPP 1.1 required operations - IPP 1.1 必需的操作
        self.operations_supported = [
            OperationEnum.print_job,
            OperationEnum.validate_job,
            OperationEnum.cancel_job,
            OperationEnum.get_job_attributes,
            OperationEnum.get_jobs,
            OperationEnum.get_printer_attributes,
        ]
        
        # 扩展支持的文档格式，专门为Windows照片打印优化 - Extended supported document formats, optimized for Windows photo printing
        self.document_formats_supported = [
            b'application/pdf',
            b'application/postscript',
            b'image/jpeg',
            b'image/png',
            b'image/tiff',
            b'image/bmp',
            b'image/gif',
            b'image/svg+xml',
            b'text/plain',
            b'application/octet-stream'  # 通用格式支持 - Generic format support
        ]
        
        # 支持的所有纸张大小 - 扩展列表 - All supported paper sizes - extended list
        self.media_supported = self._get_supported_media_sizes()
        
        # 支持的分辨率列表 - List of supported resolutions
        self.resolutions_supported = self._get_supported_resolutions()
        
        # 支持的打印质量 - Supported print quality
        self.print_qualities_supported = [
            PrintQualityEnum.draft,
            PrintQualityEnum.normal,
            PrintQualityEnum.high
        ]

    def _get_supported_media_sizes(self):
        """返回支持的纸张大小列表 - Return list of supported paper sizes"""
        return [
            # ISO A 系列 - ISO A series
            b'iso_a0_841x1189mm',
            b'iso_a1_594x841mm',
            b'iso_a2_420x594mm',
            b'iso_a3_297x420mm',
            b'iso_a4_210x297mm',
            b'iso_a5_148x210mm',
            b'iso_a6_105x148mm',
            b'iso_a7_74x105mm',
            b'iso_a8_52x74mm',
            b'iso_a9_37x52mm',
            b'iso_a10_26x37mm',
            
            # ISO B 系列 - ISO B series
            b'iso_b0_1000x1414mm',
            b'iso_b1_707x1000mm',
            b'iso_b2_500x707mm',
            b'iso_b3_353x500mm',
            b'iso_b4_250x353mm',
            b'iso_b5_176x250mm',
            b'iso_b6_125x176mm',
            b'iso_b7_88x125mm',
            b'iso_b8_62x88mm',
            b'iso_b9_44x62mm',
            b'iso_b10_31x44mm',
            
            # ISO C 系列 (信封) - ISO C series (envelopes)
            b'iso_c0_917x1297mm',
            b'iso_c1_648x917mm',
            b'iso_c2_458x648mm',
            b'iso_c3_324x458mm',
            b'iso_c4_229x324mm',
            b'iso_c5_162x229mm',
            b'iso_c6_114x162mm',
            b'iso_c7_81x114mm',
            b'iso_c8_57x81mm',
            b'iso_c9_40x57mm',
            b'iso_c10_28x40mm',
            
            # North American 纸张 - North American paper
            b'na_letter_8.5x11in',
            b'na_legal_8.5x14in',
            b'na_ledger_11x17in',
            b'na_tabloid_11x17in',
            b'na_executive_7.25x10.5in',
            b'na_government-letter_8x10in',
            b'na_government-legal_8.5x13in',
            b'na_junior-legal_8x5in',
            b'na_5x7_5x7in',
            b'na_8x10_8x10in',
            
            # 日本纸张 - Japanese paper
            b'jis_b0_1030x1456mm',
            b'jis_b1_728x1030mm',
            b'jis_b2_515x728mm',
            b'jis_b3_364x515mm',
            b'jis_b4_257x364mm',
            b'jis_b5_182x257mm',
            b'jis_b6_128x182mm',
            b'jis_b7_91x128mm',
            b'jis_b8_64x91mm',
            b'jis_b9_45x64mm',
            b'jis_b10_32x45mm',
            
            # 照片打印专用纸张 (Windows照片打印需要这些) - Special paper for photo printing (required by Windows photo printing)
            b'photo_2x3_2x3in',
            b'photo_3x5_3x5in',
            b'photo_4x6_4x6in',
            b'photo_5x7_5x7in',
            b'photo_8x10_8x10in',
            b'photo_10x15_10x15cm',
            b'photo_13x18_13x18cm',
            b'photo_15x20_15x20cm',
            b'photo_20x25_20x25cm',
            b'photo_30x40_30x40cm',
            
            # 其他常用纸张 - Other common paper
            b'custom_min_10x10mm',
            b'custom_max_1000x1400mm',
            b'env_dl_110x220mm',
            b'env_c5_162x229mm',
            b'env_c6_114x162mm',
            b'env_monarch_3.875x7.5in',
            b'env_number-10_4.125x9.5in',
            
            # 标签和卡片 - Labels and cards
            b'business-card_2x3.5in',
            b'business-card_jp_2.165x3.583in',
            b'business-card_eu_2.125x3.37in',
            b'index-card_3x5in',
            b'index-card_4x6in',
            b'index-card_5x8in',
        ]

    def _get_supported_resolutions(self):
        """返回支持的分辨率列表，为照片打印优化 - Return list of supported resolutions, optimized for photo printing"""
        return [
            Resolution(72, 72, 3),    # 72 dpi
            Resolution(100, 100, 3),  # 100 dpi
            Resolution(150, 150, 3),  # 150 dpi
            Resolution(200, 200, 3),  # 200 dpi
            Resolution(300, 300, 3),  # 300 dpi (标准打印 - Standard printing)
            Resolution(400, 400, 3),  # 400 dpi
            Resolution(600, 600, 3),  # 600 dpi (高质量打印 - High quality printing)
            Resolution(800, 800, 3),  # 800 dpi
            Resolution(1200, 1200, 3), # 1200 dpi (照片打印 - Photo printing)
            Resolution(1600, 1600, 3), # 1600 dpi (高质量照片 - High quality photo)
            Resolution(2400, 2400, 3), # 2400 dpi (专业照片 - Professional photo)
            Resolution(3200, 3200, 3), # 3200 dpi
            Resolution(4800, 4800, 3), # 4800 dpi (最高质量 - Highest quality)
            Resolution(300, 300, 4),  # 300 dpcm
            Resolution(600, 600, 4),  # 600 dpcm
        ]

    def expect_page_data_follows(self, ipp_request):
        return ipp_request.opid_or_status == OperationEnum.print_job

    def handle_ipp(self, ipp_request, postscript_file):
        # Validate IPP version - 验证IPP版本
        if not validate_ipp_version(ipp_request.version[0], ipp_request.version[1]):
            return self.version_not_supported_response(ipp_request)
        
        command_function = self.get_handle_command_function(
            ipp_request.opid_or_status
        )
        logging.debug(
            'IPP %r -> %s.%s', ipp_request.opid_or_status, type(self).__name__,
            command_function.__name__
        )
        return command_function(ipp_request, postscript_file)

    def get_handle_command_function(self, opid_or_status):
        commands = {
            OperationEnum.get_printer_attributes: self.operation_printer_attributes_response,
            OperationEnum.cups_list_all_printers: self.operation_printer_list_response,
            OperationEnum.cups_get_default: self.operation_printer_list_response,
            OperationEnum.validate_job: self.operation_validate_job_response,
            OperationEnum.get_jobs: self.operation_get_jobs_response,
            OperationEnum.get_job_attributes: self.operation_get_job_attributes_response,
            OperationEnum.print_job: self.operation_print_job_response,
            OperationEnum.cancel_job: self.operation_cancel_job_response,
            OperationEnum.pause_printer: self.operation_pause_printer_response,
            OperationEnum.resume_printer: self.operation_resume_printer_response,
            OperationEnum.purge_jobs: self.operation_purge_jobs_response,
            0x0d0a: self.operation_misidentified_as_http,
        }

        try:
            command_function = commands[opid_or_status]
        except KeyError:
            logging.warning(t('operation_not_supported', code=hex(opid_or_status)))
            command_function = self.operation_not_implemented_response
        return command_function

    def version_not_supported_response(self, req):
        attributes = self.minimal_attributes()
        return IppRequest(
            (1, 1),  # Respond with supported version - 使用支持的版本响应
            StatusCodeEnum.server_error_version_not_supported,
            req.request_id,
            attributes)

    def operation_not_implemented_response(self, req, _psfile):
        attributes = self.minimal_attributes()
        return IppRequest(
            (1, 1),
            StatusCodeEnum.server_error_operation_not_supported,
            req.request_id,
            attributes)

    def operation_printer_list_response(self, req, _psfile):
        attributes = self.printer_list_attributes()
        return IppRequest(
            (1, 1),
            StatusCodeEnum.ok,
            req.request_id,
            attributes)

    def operation_printer_attributes_response(self, req, _psfile):
        # Get requested attribute groups - 获取请求的属性组
        requested_attributes = req.lookup(SectionEnum.operation, b'requested-attributes', TagEnum.keyword)
        
        if requested_attributes:
            # Return only requested attributes - 仅返回请求的属性
            all_attributes = self.printer_list_attributes()
            filtered_attributes = {}
            
            for attr_name in requested_attributes:
                attr_name_str = attr_name.decode('ascii', errors='ignore')
                # Find attributes matching this name - 查找匹配此名称的属性
                for key, value in all_attributes.items():
                    if key[1] == attr_name:
                        filtered_attributes[key] = value
        else:
            # Return all attributes - 返回所有属性
            filtered_attributes = self.printer_list_attributes()
        
        return IppRequest(
            (1, 1),
            StatusCodeEnum.ok,
            req.request_id,
            filtered_attributes)

    def operation_validate_job_response(self, req, _psfile):
        # Validate job attributes - 验证作业属性
        try:
            # Check document format - 检查文档格式
            document_format = req.lookup(SectionEnum.operation, b'document-format', TagEnum.mime_media_type)
            if document_format and document_format[0] not in self.document_formats_supported:
                return IppRequest(
                    (1, 1),
                    StatusCodeEnum.client_error_document_format_not_supported,
                    req.request_id,
                    self.minimal_attributes())
            
            # Check media size - 检查介质大小
            media = req.lookup(SectionEnum.operation, b'media', TagEnum.keyword)
            if media and media[0] not in self.media_supported:
                return IppRequest(
                    (1, 1),
                    StatusCodeEnum.client_error_attributes_or_values_not_supported,
                    req.request_id,
                    self.minimal_attributes())
            
            attributes = self.minimal_attributes()
            return IppRequest(
                (1, 1),
                StatusCodeEnum.ok,
                req.request_id,
                attributes)
        except Exception as e:
            logging.error(t('error_validating_job', error=str(e)))
            return IppRequest(
                (1, 1),
                StatusCodeEnum.client_error_bad_request,
                req.request_id,
                self.minimal_attributes())

    def operation_get_jobs_response(self, req, _psfile):
        try:
            # Get request parameters - 获取请求参数
            which_jobs = req.lookup(SectionEnum.operation, b'which-jobs', TagEnum.keyword)
            which_jobs = which_jobs[0].decode('ascii') if which_jobs else 'completed'
            
            my_jobs = req.lookup(SectionEnum.operation, b'my-jobs', TagEnum.boolean)
            my_jobs = Boolean.from_bytes(my_jobs[0]).boolean if my_jobs else False
            
            limit = req.lookup(SectionEnum.operation, b'limit', TagEnum.integer)
            limit = Integer.from_bytes(limit[0]).integer if limit else None
            
            # Get jobs - 获取作业
            jobs = self.job_manager.list_jobs(which_jobs, my_jobs, limit)
            
            attributes = self.minimal_attributes()
            
            # Add job attributes for each job - 为每个作业添加作业属性
            for job in jobs:
                job_attrs = self.get_job_attributes_dict(job['job_id'])
                attributes.update(job_attrs)
            
            return IppRequest(
                (1, 1),
                StatusCodeEnum.ok,
                req.request_id,
                attributes)
        except Exception as e:
            logging.error(t('error_getting_jobs', error=str(e)))
            return IppRequest(
                (1, 1),
                StatusCodeEnum.server_error_internal_error,
                req.request_id,
                self.minimal_attributes())

    def operation_print_job_response(self, req, psfile):
        try:
            # 检查压缩类型 - Check compression type
            compression = req.lookup(SectionEnum.operation, b'compression', TagEnum.keyword)
            compression_type = None
            if compression:
                compression_type = compression[0].decode('ascii', errors='ignore')
                logging.info(t('request_specifies_compression', type=compression_type))
            
            # Get job attributes - 获取作业属性
            job_name = req.lookup(SectionEnum.operation, b'job-name', TagEnum.name_without_language)
            job_name = job_name[0].decode('utf-8', errors='ignore') if job_name else None  # 改为UTF-8解码 - Changed to UTF-8 decoding
            
            user_name = req.lookup(SectionEnum.operation, b'job-originating-user-name', TagEnum.name_without_language)
            user_name = user_name[0].decode('utf-8', errors='ignore') if user_name else 'unknown'  # 改为UTF-8解码 - Changed to UTF-8 decoding
            
            # 获取文档格式 - Get document format
            document_format = req.lookup(SectionEnum.operation, b'document-format', TagEnum.mime_media_type)
            if document_format:
                document_format = document_format[0].decode('ascii', errors='ignore')
            else:
                # 自动检测格式 - Auto-detect format
                document_format = 'application/octet-stream'
            
            # 获取打印参数 - Get printing parameters
            media = req.lookup(SectionEnum.operation, b'media', TagEnum.keyword)
            media = media[0].decode('ascii', errors='ignore') if media else 'iso_a4_210x297mm'
            
            copies = req.lookup(SectionEnum.operation, b'copies', TagEnum.integer)
            copies = Integer.from_bytes(copies[0]).integer if copies else 1
            
            print_quality = req.lookup(SectionEnum.operation, b'print-quality', TagEnum.enum)
            print_quality = Enum.from_bytes(print_quality[0]).integer if print_quality else PrintQualityEnum.normal
            
            print_color_mode = req.lookup(SectionEnum.operation, b'print-color-mode', TagEnum.keyword)
            print_color_mode = print_color_mode[0].decode('ascii', errors='ignore') if print_color_mode else 'auto'
            
            # 检查是否是图像文件 - Windows照片打印的关键 - Check if it's an image file - key for Windows photo printing
            is_image_document = document_format.startswith('image/')
            
            # Windows照片打印特殊处理 - 强制使用彩色模式 - Windows photo printing special handling - force color mode
            if is_image_document:
                logging.info(t('image_document_detected', format=document_format))
                logging.info(t('original_color_mode', mode=print_color_mode))
                
                # Windows照片查看器使用特殊的颜色处理逻辑 - Windows Photo Viewer uses special color handling logic
                # 对于图片文件，无论用户选择什么，都强制使用彩色模式 - For image files, force color mode regardless of user selection
                if print_color_mode in ['monochrome', 'bi-level', 'auto-monochrome', 'process-monochrome', 'gray']:
                    logging.info(t('forcing_color_mode_for_image'))
                    print_color_mode = 'color'
                elif print_color_mode == 'auto':
                    # 自动模式也设为color - Auto mode also set to color
                    print_color_mode = 'color'
                    logging.info(t('setting_color_mode_to_color_for_image'))
                else:
                    # 已经是彩色模式，保持 - Already in color mode, keep
                    logging.info(t('image_document_using_color_mode', mode=print_color_mode))
                
                # 对于照片，建议使用高质量设置 - For photos, recommend high quality settings
                if print_quality == PrintQualityEnum.normal:
                    print_quality = PrintQualityEnum.high
                    logging.info(t('setting_print_quality_to_high_for_image'))
            
            # 在响应发送前读取并保存文档数据 - Read and save document data before sending response
            document_data = b''
            if psfile:
                try:
                    # 立即读取所有数据 - Read all data immediately
                    document_data = psfile.read()
                    logging.debug(t('raw_data_received', size=len(document_data)))
                    
                    # 如果指定了压缩类型，解压缩数据 - If compression type specified, decompress data
                    if compression_type and compression_type != 'none':
                        try:
                            original_size = len(document_data)
                            document_data = decompress_data(document_data, compression_type)
                            logging.info(t('decompression_complete', original=original_size, final=len(document_data), type=compression_type))
                        except Exception as e:
                            logging.error(t('failed_to_decompress_data', type=compression_type, error=str(e)))
                            # 如果解压缩失败，返回错误 - If decompression fails, return error
                            return IppRequest(
                                (1, 1),
                                StatusCodeEnum.client_error_compression_error,
                                req.request_id,
                                self.minimal_attributes())
                    
                    logging.debug(t('document_format_info', format=document_format, is_image=is_image_document, color_mode=print_color_mode))
                    
                except (ValueError, OSError) as e:
                    logging.warning(t('error_reading_document_data', error=str(e)))
                    document_data = b''
            
            # Create job - 创建作业
            job_id, job_info = self.job_manager.create_job(job_name, user_name)
            job_info['document_format'] = document_format
            job_info['is_image'] = is_image_document
            job_info['compression_type'] = compression_type
            job_info['job_attributes'] = {
                'media': media,
                'copies': copies,
                'print_quality': print_quality,
                'print_color_mode': print_color_mode
            }
            
            # 保存文档数据到job info中 - Save document data to job info
            job_info['document_data'] = document_data
            job_info['document_size'] = len(document_data)
            
            # Update printer state if needed - 如果需要，更新打印机状态
            if self.printer_state == PrinterStateEnum.idle:
                self.printer_state = PrinterStateEnum.processing
                self.printer_state_reasons = [b'none']
            
            # Update queued job count - 更新排队作业计数
            self.queued_job_count = len([j for j in self.job_manager.jobs.values() 
                                        if j['state'] in [JobStateEnum.pending, JobStateEnum.pending_held]])
            
            # 立即开始处理，但使用已保存的数据 - Start processing immediately, but use saved data
            self.job_manager.update_job_state(job_id, JobStateEnum.processing, [b'none'])
            
            # Get attributes for response - 获取响应属性
            attributes = self.get_job_attributes_dict(job_id)
            
            # 使用已保存的数据进行处理，而不是原始文件流 - Process using saved data, not original file stream
            # 创建内存文件对象 - Create memory file object
            if document_data:
                mem_file = io.BytesIO(document_data)
                # 处理在后台线程中进行 - Process in background thread
                threading.Thread(
                    target=self.process_job,
                    args=(job_id, req, mem_file, document_format, job_info['job_attributes'], is_image_document),
                    daemon=True
                ).start()
            else:
                # 如果没有数据，直接标记为完成 - If no data, mark as completed directly
                self.job_manager.update_job_state(job_id, JobStateEnum.completed, [b'none'])
                # 更新打印机状态 - Update printer state
                active_jobs = [j for j in self.job_manager.jobs.values() 
                              if j['state'] in [JobStateEnum.processing, JobStateEnum.pending]]
                if not active_jobs and self.printer_state == PrinterStateEnum.processing:
                    self.printer_state = PrinterStateEnum.idle
            
            return IppRequest(
                (1, 1),
                StatusCodeEnum.ok,
                req.request_id,
                attributes)
        except Exception as e:
            logging.error(t('error_creating_print_job', error=str(e)))
            return IppRequest(
                (1, 1),
                StatusCodeEnum.server_error_internal_error,
                req.request_id,
                self.minimal_attributes())

    def operation_get_job_attributes_response(self, req, _psfile):
        try:
            job_id = get_job_id(req)
            job = self.job_manager.get_job(job_id)
            
            if not job:
                return IppRequest(
                    (1, 1),
                    StatusCodeEnum.client_error_not_found,
                    req.request_id,
                    self.minimal_attributes())
            
            attributes = self.get_job_attributes_dict(job_id)
            return IppRequest(
                (1, 1),
                StatusCodeEnum.ok,
                req.request_id,
                attributes)
        except Exception as e:
            logging.error(t('error_getting_job_attributes', error=str(e)))
            return IppRequest(
                (1, 1),
                StatusCodeEnum.server_error_internal_error,
                req.request_id,
                self.minimal_attributes())

    def operation_cancel_job_response(self, req, _psfile):
        try:
            job_id = get_job_id(req)
            job = self.job_manager.get_job(job_id)
            
            if not job:
                return IppRequest(
                    (1, 1),
                    StatusCodeEnum.client_error_not_found,
                    req.request_id,
                    self.minimal_attributes())
            
            # Check if job can be canceled - 检查作业是否可以取消
            if job['state'] in [JobStateEnum.completed, JobStateEnum.canceled, JobStateEnum.aborted]:
                return IppRequest(
                    (1, 1),
                    StatusCodeEnum.client_error_not_possible,
                    req.request_id,
                    self.minimal_attributes())
            
            # Cancel the job - 取消作业
            self.job_manager.update_job_state(job_id, JobStateEnum.canceled, [b'job-canceled-by-user'])
            
            # Update printer state if no more jobs - 如果没有更多作业，更新打印机状态
            active_jobs = [j for j in self.job_manager.jobs.values() 
                          if j['state'] in [JobStateEnum.processing, JobStateEnum.pending]]
            if not active_jobs and self.printer_state == PrinterStateEnum.processing:
                self.printer_state = PrinterStateEnum.idle
            
            # Update queued job count - 更新排队作业计数
            self.queued_job_count = len([j for j in self.job_manager.jobs.values() 
                                        if j['state'] in [JobStateEnum.pending, JobStateEnum.pending_held]])
            
            attributes = self.get_job_attributes_dict(job_id)
            return IppRequest(
                (1, 1),
                StatusCodeEnum.ok,
                req.request_id,
                attributes)
        except Exception as e:
            logging.error(t('error_canceling_job', error=str(e)))
            return IppRequest(
                (1, 1),
                StatusCodeEnum.server_error_internal_error,
                req.request_id,
                self.minimal_attributes())

    def operation_pause_printer_response(self, req, _psfile):
        self.printer_state = PrinterStateEnum.stopped
        self.printer_state_reasons = [b'paused']
        
        attributes = self.minimal_attributes()
        return IppRequest(
            (1, 1),
            StatusCodeEnum.ok,
            req.request_id,
            attributes)

    def operation_resume_printer_response(self, req, _psfile):
        self.printer_state = PrinterStateEnum.idle
        self.printer_state_reasons = [b'none']
        
        attributes = self.minimal_attributes()
        return IppRequest(
            (1, 1),
            StatusCodeEnum.ok,
            req.request_id,
            attributes)

    def operation_purge_jobs_response(self, req, _psfile):
        # Remove completed, canceled, and aborted jobs - 删除已完成的、已取消的和已中止的作业
        jobs_to_delete = []
        for job_id, job in self.job_manager.jobs.items():
            if job['state'] in [JobStateEnum.completed, JobStateEnum.canceled, JobStateEnum.aborted]:
                jobs_to_delete.append(job_id)
        
        for job_id in jobs_to_delete:
            self.job_manager.delete_job(job_id)
        
        # Update queued job count - 更新排队作业计数
        self.queued_job_count = len([j for j in self.job_manager.jobs.values() 
                                    if j['state'] in [JobStateEnum.pending, JobStateEnum.pending_held]])
        
        attributes = self.minimal_attributes()
        return IppRequest(
            (1, 1),
            StatusCodeEnum.ok,
            req.request_id,
            attributes)

    def operation_misidentified_as_http(self, _req, _psfile):
        raise Exception(t('misidentified_as_http'))

    def minimal_attributes(self):
        return {
            # Required operation attributes (RFC 8011 section 4.1.7) - 必需的操作属性（RFC 8011 章节 4.1.7）
            (
                SectionEnum.operation,
                b'attributes-charset',
                TagEnum.charset
            ): [b'utf-8'],
            (
                SectionEnum.operation,
                b'attributes-natural-language',
                TagEnum.natural_language
            ): [b'en'],
            (
                SectionEnum.operation,
                b'status-message',
                TagEnum.text_without_language
            ): [b'Success'],
        }

    def printer_list_attributes(self):
        attr = {
            # Printer description attributes (RFC 8011 section 5.4.1) - 打印机描述属性（RFC 8011 章节 5.4.1）
            (
                SectionEnum.printer,
                b'printer-uri-supported',
                TagEnum.uri
            ): [self.printer_uri],
            (
                SectionEnum.printer,
                b'uri-authentication-supported',
                TagEnum.keyword
            ): [b'none', b'requesting-user-name'],
            (
                SectionEnum.printer,
                b'uri-security-supported',
                TagEnum.keyword
            ): [b'none', b'ssl3', b'tls'],
            (
                SectionEnum.printer,
                b'printer-name',
                TagEnum.name_without_language
            ): [self.printer_name],  # 使用UTF-8编码的打印机名称 - Printer name encoded in UTF-8
            (
                SectionEnum.printer,
                b'printer-info',
                TagEnum.text_without_language
            ): [self.printer_description],  # 使用UTF-8编码的打印机描述 - Printer description encoded in UTF-8
            (
                SectionEnum.printer,
                b'printer-location',
                TagEnum.text_without_language
            ): [self.printer_location],  # 使用UTF-8编码的打印机位置 - Printer location encoded in UTF-8
            (
                SectionEnum.printer,
                b'printer-make-and-model',
                TagEnum.text_without_language
            ): [b'Virtual Photo Printer with Full Color Support'],
            (
                SectionEnum.printer,
                b'printer-state',
                TagEnum.enum
            ): [Enum(self.printer_state).bytes()],
            (
                SectionEnum.printer,
                b'printer-state-reasons',
                TagEnum.keyword
            ): self.printer_state_reasons,
            (
                SectionEnum.printer,
                b'printer-state-message',
                TagEnum.text_without_language
            ): [b'Ready for Color Photo Printing'],
            (
                SectionEnum.printer,
                b'printer-is-accepting-jobs',
                TagEnum.boolean
            ): [Boolean(True).bytes()],
            
            # IPP version support - IPP版本支持
            (
                SectionEnum.printer,
                b'ipp-versions-supported',
                TagEnum.keyword
            ): [b'1.1', b'2.0', b'2.1', b'2.2'],
            (
                SectionEnum.printer,
                b'ipp-features-supported',
                TagEnum.keyword
            ): [b'ipp-everywhere', b'page-overrides', b'photo-printing'],
            
            # Operation support - 操作支持
            (
                SectionEnum.printer,
                b'operations-supported',
                TagEnum.enum
            ): [
                Enum(x).bytes()
                for x in self.operations_supported
            ],
            
            # Multiple document handling - 多文档处理
            (
                SectionEnum.printer,
                b'multiple-document-jobs-supported',
                TagEnum.boolean
            ): [Boolean(True).bytes()],
            (
                SectionEnum.printer,
                b'multiple-operation-time-out',
                TagEnum.integer
            ): [Integer(120).bytes()],  # 2 minutes - 2分钟
            
            # Character set and language - 字符集和语言
            (
                SectionEnum.printer,
                b'charset-configured',
                TagEnum.charset
            ): [b'utf-8'],
            (
                SectionEnum.printer,
                b'charset-supported',
                TagEnum.charset
            ): [b'utf-8', b'us-ascii', b'iso-8859-1'],
            (
                SectionEnum.printer,
                b'natural-language-configured',
                TagEnum.natural_language
            ): [b'en'],
            (
                SectionEnum.printer,
                b'generated-natural-language-supported',
                TagEnum.natural_language
            ): [b'en', b'fr', b'de'],
            
            # Document format - 扩展格式支持 - Document format - extended format support
            (
                SectionEnum.printer,
                b'document-format-default',
                TagEnum.mime_media_type
            ): [b'application/pdf'],
            (
                SectionEnum.printer,
                b'document-format-supported',
                TagEnum.mime_media_type
            ): self.document_formats_supported,
            (
                SectionEnum.printer,
                b'document-format-varying-attributes',
                TagEnum.keyword
            ): [b'media', b'media-col', b'print-color-mode', b'print-quality', b'copies'],
            
            # Compression support - 添加压缩支持 - Compression support - add compression support
            (
                SectionEnum.printer,
                b'compression-supported',
                TagEnum.keyword
            ): [b'none', b'gzip', b'deflate', b'compress'],
            (
                SectionEnum.printer,
                b'compression-default',
                TagEnum.keyword
            ): [b'none'],
            
            # Job handling - 作业处理
            (
                SectionEnum.printer,
                b'queued-job-count',
                TagEnum.integer
            ): [Integer(self.queued_job_count).bytes()],
            (
                SectionEnum.printer,
                b'pdl-override-supported',
                TagEnum.keyword
            ): [b'not-attempted', b'attempted'],
            (
                SectionEnum.printer,
                b'printer-up-time',
                TagEnum.integer
            ): [Integer(int(time.time() - self.printer_uptime_start)).bytes()],
            (
                SectionEnum.printer,
                b'printer-current-time',
                TagEnum.datetime_str
            ): [create_ipp_datetime()],
            
            # Media handling - 扩展的纸张大小支持 - Media handling - extended paper size support
            (
                SectionEnum.printer,
                b'media-supported',
                TagEnum.keyword
            ): self.media_supported,
            (
                SectionEnum.printer,
                b'media-default',
                TagEnum.keyword
            ): [b'iso_a4_210x297mm'],
            (
                SectionEnum.printer,
                b'media-ready',
                TagEnum.keyword
            ): self.media_supported,
            
            # Print quality - 扩展为支持照片打印 - Print quality - extended for photo printing support
            (
                SectionEnum.printer,
                b'print-quality-supported',
                TagEnum.enum
            ): [
                Enum(PrintQualityEnum.draft).bytes(),
                Enum(PrintQualityEnum.normal).bytes(),
                Enum(PrintQualityEnum.high).bytes()
            ],
            (
                SectionEnum.printer,
                b'print-quality-default',
                TagEnum.enum
            ): [Enum(PrintQualityEnum.normal).bytes()],
            
            # Sides - 双面
            (
                SectionEnum.printer,
                b'sides-supported',
                TagEnum.keyword
            ): [b'one-sided', b'two-sided-long-edge', b'two-sided-short-edge'],
            (
                SectionEnum.printer,
                b'sides-default',
                TagEnum.keyword
            ): [b'one-sided'],
            
            # Color - 扩展的颜色支持，专门为Windows照片打印优化 - 关键修改部分
            # Color - Extended color support, specifically optimized for Windows photo printing - Key modification section
            (
                SectionEnum.printer,
                b'color-supported',
                TagEnum.boolean
            ): [Boolean(True).bytes()],
            
            # IPP标准颜色模型支持 - 必须添加这些 - IPP standard color model support - must add these
            (
                SectionEnum.printer,
                b'color-model-supported',
                TagEnum.keyword
            ): [b'rgb', b'cmyk', b'gray', b'srgb', b'adobe-rgb', b'device-cmyk'],
            (
                SectionEnum.printer,
                b'color-model-default',
                TagEnum.keyword
            ): [b'rgb'],
            
            # 更完整的颜色模式支持 - Windows需要这些 - More complete color mode support - Windows needs these
            (
                SectionEnum.printer,
                b'print-color-mode-supported',
                TagEnum.keyword
            ): [
                b'auto', 
                b'color', 
                b'monochrome', 
                b'bi-level',
                b'color-saturated',
                b'process-color',
                b'process-monochrome',
                b'auto-monochrome',
                b'photo-color'
            ],
            (
                SectionEnum.printer,
                b'print-color-mode-default',
                TagEnum.keyword
            ): [b'auto'],
            
            # Windows照片打印关键设置 - 添加这些新属性 - Windows photo printing key settings - add these new attributes
            (
                SectionEnum.printer,
                b'color-print-quality-default',
                TagEnum.keyword
            ): [b'color'],
            
            # 声明支持所有颜色模式 - Declare support for all color modes
            (
                SectionEnum.printer,
                b'print-color-mode-ready',
                TagEnum.keyword
            ): [b'color', b'auto', b'photo-color'],
            
            # 颜色深度支持 - Windows照片打印需要这个 - Color depth support - Windows photo printing needs this
            (
                SectionEnum.printer,
                b'color-depth-supported',
                TagEnum.range_of_integer
            ): [RangeOfInteger(8, 48).bytes()],
            (
                SectionEnum.printer,
                b'color-depth-default',
                TagEnum.integer
            ): [Integer(24).bytes()],
            
            # 分辨率支持 - 专门为照片优化 - Resolution support - specifically optimized for photos
            (
                SectionEnum.printer,
                b'color-resolution-supported',
                TagEnum.resolution
            ): [
                Resolution(300, 300, 3).bytes(),
                Resolution(600, 600, 3).bytes(),
                Resolution(1200, 1200, 3).bytes(),
                Resolution(2400, 2400, 3).bytes(),
                Resolution(4800, 4800, 3).bytes()
            ],
            (
                SectionEnum.printer,
                b'color-resolution-default',
                TagEnum.resolution
            ): [Resolution(1200, 1200, 3).bytes()],
            
            # Windows特定的照片打印支持 - 关键属性 - Windows-specific photo printing support - key attributes
            (
                SectionEnum.printer,
                b'photographic-printing-supported',
                TagEnum.boolean
            ): [Boolean(True).bytes()],
            (
                SectionEnum.printer,
                b'photographic-color-supported',
                TagEnum.boolean
            ): [Boolean(True).bytes()],
            
            # 更完整的照片媒体支持 - More complete photo media support
            (
                SectionEnum.printer,
                b'photographic-media-supported',
                TagEnum.keyword
            ): [
                b'photo_4x6_4x6in',
                b'photo_5x7_5x7in',
                b'photo_8x10_8x10in',
                b'photo_10x15_10x15cm',
                b'photo_13x18_13x18cm',
                b'photo_15x20_15x20cm',
                b'photo_20x25_20x25cm',
                b'photo_30x40_30x40cm'
            ],
            
            # 照片特定的分辨率 - Photo-specific resolution
            (
                SectionEnum.printer,
                b'photographic-resolution-supported',
                TagEnum.resolution
            ): [
                Resolution(600, 600, 3).bytes(),
                Resolution(1200, 1200, 3).bytes(),
                Resolution(2400, 2400, 3).bytes(),
                Resolution(4800, 4800, 3).bytes()
            ],
            (
                SectionEnum.printer,
                b'photographic-resolution-default',
                TagEnum.resolution
            ): [Resolution(2400, 2400, 3).bytes()],
            
            # 照片颜色模式支持 - Photo color mode support
            (
                SectionEnum.printer,
                b'photographic-color-mode-supported',
                TagEnum.keyword
            ): [
                b'color',
                b'photo-color',
                b'photo-black-white'
            ],
            (
                SectionEnum.printer,
                b'photographic-color-mode-default',
                TagEnum.keyword
            ): [b'color'],
            
            # 添加Windows照片打印特定的IPP属性 - Add Windows photo printing specific IPP attributes
            (
                SectionEnum.printer,
                b'photo-printing-supported',
                TagEnum.boolean
            ): [Boolean(True).bytes()],
            
            # Windows照片查看器特定的属性 - Windows Photo Viewer specific attributes
            (
                SectionEnum.printer,
                b'photo-optimized-default',
                TagEnum.boolean
            ): [Boolean(True).bytes()],
            (
                SectionEnum.printer,
                b'photo-optimized-supported',
                TagEnum.boolean
            ): [Boolean(True).bytes()],
            
            # ICC配置文件支持 - 专业照片打印需要 - ICC profile support - needed for professional photo printing
            (
                SectionEnum.printer,
                b'icc-profile-supported',
                TagEnum.keyword
            ): [
                b'sRGB IEC61966-2.1',
                b'AdobeRGB1998',
                b'ProPhoto RGB',
                b'ISO Coated v2 300% (ECI)',
                b'FOGRA39L'
            ],
            
            # 图像增强功能 - Image enhancement features
            (
                SectionEnum.printer,
                b'image-enhancement-supported',
                TagEnum.keyword
            ): [
                b'red-eye-reduction',
                b'skin-tone-enhancement',
                b'sharpen',
                b'noise-reduction',
                b'color-correction'
            ],
            
            # Printer identification - 打印机标识
            (
                SectionEnum.printer,
                b'printer-uuid',
                TagEnum.uri
            ): [self.printer_uuid],
            (
                SectionEnum.printer,
                b'system-name',
                TagEnum.name_without_language
            ): [socket.gethostname().encode('utf-8', errors='replace')],  # 改为UTF-8编码 - Changed to UTF-8 encoding
            (
                SectionEnum.printer,
                b'system-location',
                TagEnum.text_without_language
            ): [self.printer_location],
            
            # Resolution - 扩展的分辨率支持 - Resolution - extended resolution support
            (
                SectionEnum.printer,
                b'printer-resolution-supported',
                TagEnum.resolution
            ): [
                res.bytes() for res in self.resolutions_supported
            ],
            (
                SectionEnum.printer,
                b'printer-resolution-default',
                TagEnum.resolution
            ): [Resolution(600, 600, 3).bytes()],
            
            # Job template - 扩展模板支持 - Job template - extended template support
            (
                SectionEnum.printer,
                b'job-template-supported',
                TagEnum.keyword
            ): [
                b'media', b'media-col', b'copies', b'sides',
                b'print-quality', b'print-color-mode', b'job-priority',
                b'output-bin', b'orientation-requested', b'media-source',
                b'media-type', b'finishings', b'page-ranges', b'number-up',
                b'photo-printing', b'photo-resolution', b'photo-media',
                b'color-model', b'color-depth', b'compression'
            ],
            
            # Job priority - 作业优先级
            (
                SectionEnum.printer,
                b'job-priority-supported',
                TagEnum.integer
            ): [Integer(100).bytes()],
            (
                SectionEnum.printer,
                b'job-priority-default',
                TagEnum.integer
            ): [Integer(50).bytes()],
            
            # Copies - 副本
            (
                SectionEnum.printer,
                b'copies-supported',
                TagEnum.range_of_integer
            ): [RangeOfInteger(1, 999).bytes()],
            (
                SectionEnum.printer,
                b'copies-default',
                TagEnum.integer
            ): [Integer(1).bytes()],
            
            # Output bins - 输出盒
            (
                SectionEnum.printer,
                b'output-bin-supported',
                TagEnum.keyword
            ): [b'auto', b'top', b'bottom', b'mailbox-1', b'mailbox-2', b'photo-tray'],
            (
                SectionEnum.printer,
                b'output-bin-default',
                TagEnum.keyword
            ): [b'auto'],
            
            # Orientation - 方向
            (
                SectionEnum.printer,
                b'orientation-requested-supported',
                TagEnum.enum
            ): [
                Enum(3).bytes(),  # portrait - 纵向
                Enum(4).bytes(),  # landscape - 横向
                Enum(5).bytes(),  # reverse-landscape - 反向横向
                Enum(6).bytes()   # reverse-portrait - 反向纵向
            ],
            (
                SectionEnum.printer,
                b'orientation-requested-default',
                TagEnum.enum
            ): [Enum(3).bytes()],  # portrait - 纵向
            
            # Number-up - 合并页数
            (
                SectionEnum.printer,
                b'number-up-supported',
                TagEnum.integer
            ): [
                Integer(1).bytes(),
                Integer(2).bytes(),
                Integer(4).bytes(),
                Integer(6).bytes(),
                Integer(9).bytes(),
                Integer(16).bytes()
            ],
            (
                SectionEnum.printer,
                b'number-up-default',
                TagEnum.integer
            ): [Integer(1).bytes()],
            
            # Media types - 添加照片专用类型 - Media types - add photo-specific types
            (
                SectionEnum.printer,
                b'media-type-supported',
                TagEnum.keyword
            ): [
                b'stationery', b'transparency', b'envelope', b'cardstock',
                b'labels', b'photographic', b'photographic-glossy',
                b'photographic-matte', b'photographic-semi-gloss',
                b'photographic-high-gloss', b'photographic-film'
            ],
            (
                SectionEnum.printer,
                b'media-type-default',
                TagEnum.keyword
            ): [b'stationery'],
            
            # Finishings - 整理
            (
                SectionEnum.printer,
                b'finishings-supported',
                TagEnum.enum
            ): [
                Enum(3).bytes(),   # none - 无
                Enum(4).bytes(),   # staple - 装订
                Enum(5).bytes()    # punch - 打孔
            ],
            (
                SectionEnum.printer,
                b'finishings-default',
                TagEnum.enum
            ): [Enum(3).bytes()],  # none - 无
            
            # Windows特定的扩展属性 - Windows-specific extended attributes
            (
                SectionEnum.printer,
                b'printer-type',
                TagEnum.integer
            ): [Integer(0x00000100 | 0x00001000 | 0x00002000).bytes()],  # 标识为照片打印机并支持彩色和照片优化 - Identified as photo printer and supports color and photo optimization
            (
                SectionEnum.printer,
                b'printer-type-mask',
                TagEnum.integer
            ): [Integer(0x00000100 | 0x00001000 | 0x00002000).bytes()],  # 照片打印机掩码 - Photo printer mask
            
            # Windows照片打印注册表项模拟 - Windows photo printing registry entry simulation
            (
                SectionEnum.printer,
                b'printer-driver-data',
                TagEnum.octet_str
            ): [b'ColorSupport=3;PhotoColorMode=1;PhotoOptimized=1;'],  # 3表示支持彩色 - 3 indicates color support
            
            # 添加颜色处理特定属性 - Add color processing specific attributes
            (
                SectionEnum.printer,
                b'color-handling-supported',
                TagEnum.keyword
            ): [b'auto', b'manual', b'photo-optimized'],
            (
                SectionEnum.printer,
                b'color-handling-default',
                TagEnum.keyword
            ): [b'photo-optimized'],
            
            # 添加图像特定的颜色属性 - Add image-specific color attributes
            (
                SectionEnum.printer,
                b'image-color-mode-default',
                TagEnum.keyword
            ): [b'color'],
            (
                SectionEnum.printer,
                b'image-color-mode-supported',
                TagEnum.keyword
            ): [b'color', b'grayscale'],
        }
        attr.update(self.minimal_attributes())
        return attr
    
    def get_job_attributes_dict(self, job_id):
        job = self.job_manager.get_job(job_id)
        if not job:
            return {}
        
        job_uri = b'%sjob/%d' % (self.base_uri, job_id,)
        
        attr = {
            # Required job attributes (RFC 8011 section 5.3) - 必需的作业属性（RFC 8011 章节 5.3）
            (
                SectionEnum.job,
                b'job-uri',
                TagEnum.uri
            ): [job_uri],
            (
                SectionEnum.job,
                b'job-id',
                TagEnum.integer
            ): [Integer(job_id).bytes()],
            (
                SectionEnum.job,
                b'job-state',
                TagEnum.enum
            ): [Enum(job['state']).bytes()],
            (
                SectionEnum.job,
                b'job-state-reasons',
                TagEnum.keyword
            ): job['state_reasons'],
            (
                SectionEnum.job,
                b'job-state-message',
                TagEnum.text_without_language
            ): [self.get_job_state_message(job['state']).encode('utf-8')],  # 改为UTF-8编码 - Changed to UTF-8 encoding
            
            # Job description - 作业描述
            (
                SectionEnum.job,
                b'job-printer-uri',
                TagEnum.uri
            ): [self.printer_uri],
            (
                SectionEnum.job,
                b'job-name',
                TagEnum.name_without_language
            ): [job['job_name'].encode('utf-8', errors='ignore')],  # 改为UTF-8编码 - Changed to UTF-8 encoding
            (
                SectionEnum.job,
                b'job-originating-user-name',
                TagEnum.name_without_language
            ): [job['user_name'].encode('utf-8', errors='ignore')],  # 改为UTF-8编码 - Changed to UTF-8 encoding
            
            # Job timing - 作业时间
            (
                SectionEnum.job,
                b'time-at-creation',
                TagEnum.integer
            ): [Integer(int(job['creation_time'])).bytes()],
            (
                SectionEnum.job,
                b'date-time-at-creation',
                TagEnum.datetime_str
            ): [create_ipp_datetime(job['creation_time'])],
            
            # Document size - 文档大小
            (
                SectionEnum.job,
                b'job-k-octets',
                TagEnum.integer
            ): [Integer((job.get('document_size', 0) + 1023) // 1024).bytes()],
        }
        
        # Add processing time if available - 如果可用，添加处理时间
        if job['processing_time']:
            attr[(
                SectionEnum.job,
                b'time-at-processing',
                TagEnum.integer
            )] = [Integer(int(job['processing_time'])).bytes()]
            attr[(
                SectionEnum.job,
                b'date-time-at-processing',
                TagEnum.datetime_str
            )] = [create_ipp_datetime(job['processing_time'])]
        
        # Add completion time if available - 如果可用，添加完成时间
        if job['completion_time']:
            attr[(
                SectionEnum.job,
                b'time-at-completed',
                TagEnum.integer
            )] = [Integer(int(job['completion_time'])).bytes()]
            attr[(
                SectionEnum.job,
                b'date-time-at-completed',
                TagEnum.datetime_str
            )] = [create_ipp_datetime(job['completion_time'])]
        
        # Add printer uptime - 添加打印机运行时间
        attr[(
            SectionEnum.job,
            b'job-printer-up-time',
            TagEnum.integer
        )] = [Integer(int(time.time() - self.printer_uptime_start)).bytes()]
        
        # Add number of documents and copies (simplified) - 添加文档数量和副本数（简化）
        attr[(
            SectionEnum.job,
            b'number-of-documents',
            TagEnum.integer
        )] = [Integer(1).bytes()]
        
        attr[(
            SectionEnum.job,
            b'number-of-intervening-jobs',
            TagEnum.integer
        )] = [Integer(self.queued_job_count).bytes()]
        
        # Add output attributes - 添加输出属性
        attr[(
            SectionEnum.job,
            b'job-media-sheets-completed',
            TagEnum.integer
        )] = [Integer(1).bytes()] if job['state'] == JobStateEnum.completed else [Integer(0).bytes()]
        
        # Add job attributes if available - 如果可用，添加作业属性
        if 'job_attributes' in job:
            job_attrs = job['job_attributes']
            if 'media' in job_attrs:
                attr[(
                    SectionEnum.job,
                    b'media',
                    TagEnum.keyword
                )] = [job_attrs['media'].encode('ascii')]
            
            if 'copies' in job_attrs:
                attr[(
                    SectionEnum.job,
                    b'copies',
                    TagEnum.integer
                )] = [Integer(job_attrs['copies']).bytes()]
            
            if 'print_quality' in job_attrs:
                attr[(
                    SectionEnum.job,
                    b'print-quality',
                    TagEnum.enum
                )] = [Enum(job_attrs['print_quality']).bytes()]
            
            if 'print_color_mode' in job_attrs:
                attr[(
                    SectionEnum.job,
                    b'print-color-mode',
                    TagEnum.keyword
                )] = [job_attrs['print_color_mode'].encode('ascii')]
        
        # Add document format - 添加文档格式
        if 'document_format' in job:
            attr[(
                SectionEnum.job,
                b'document-format',
                TagEnum.mime_media_type
            )] = [job['document_format'].encode('ascii')]
        
        # Add compression info - 添加压缩信息
        if 'compression_type' in job and job['compression_type']:
            attr[(
                SectionEnum.job,
                b'compression',
                TagEnum.keyword
            )] = [job['compression_type'].encode('ascii')]
        
        # 添加图片特定的属性 - Add image-specific attributes
        if job.get('is_image', False):
            attr[(
                SectionEnum.job,
                b'image-color-mode',
                TagEnum.keyword
            )] = [b'color']  # 强制声明为彩色 - Force declare as color
            
            attr[(
                SectionEnum.job,
                b'photo-optimized',
                TagEnum.boolean
            )] = [Boolean(True).bytes()]
        
        attr.update(self.minimal_attributes())
        return attr

    def get_job_state_message(self, state):
        messages = {
            JobStateEnum.pending: t('job_state_pending'),
            JobStateEnum.pending_held: t('job_state_pending_held'),
            JobStateEnum.processing: t('job_state_processing'),
            JobStateEnum.processing_stopped: t('job_state_processing_stopped'),
            JobStateEnum.canceled: t('job_state_canceled'),
            JobStateEnum.aborted: t('job_state_aborted'),
            JobStateEnum.completed: t('job_state_completed'),
        }
        return messages.get(state, t('job_state_unknown'))

    def process_job(self, job_id, ipp_request, postscript_file, document_format=None, job_attributes=None, is_image_document=False):
        """Process a print job in background - 在后台处理打印作业"""
        try:
            logging.info(t('starting_to_process_job', job_id=job_id))
            
            # 确保文件指针在开头 - Ensure file pointer is at the beginning
            if hasattr(postscript_file, 'seek'):
                postscript_file.seek(0)
            
            # 获取文档数据 - Get document data
            data = postscript_file.read()
            
            if data:
                # 转换为PDF - Convert to PDF
                pdf_data = convert_to_pdf(data, document_format)
                
                # 创建包含PDF数据的文件对象 - Create file object containing PDF data
                pdf_file = io.BytesIO(pdf_data)
                
                # 记录打印参数 - Log printing parameters
                if job_attributes:
                    logging.info(t('print_job_parameters').format(job_id=job_id))
                    logging.info(t('document_format_info_short').format(format=document_format, is_image=is_image_document))
                    for key, value in job_attributes.items():
                        logging.info(t('job_parameter').format(key=key, value=value))
                
                # 调用实际的处理器方法 - Call actual handler method
                self.handle_pdf(ipp_request, pdf_file, pdf_data, job_attributes)
            
            # 标记作业为完成 - Mark job as completed
            self.job_manager.update_job_state(job_id, JobStateEnum.completed, [b'none'])
            
            # 如果没有更多作业，更新打印机状态 - If no more jobs, update printer state
            active_jobs = [j for j in self.job_manager.jobs.values() 
                          if j['state'] in [JobStateEnum.processing, JobStateEnum.pending]]
            if not active_jobs and self.printer_state == PrinterStateEnum.processing:
                self.printer_state = PrinterStateEnum.idle
            
            # 更新排队作业计数 - Update queued job count
            self.queued_job_count = len([j for j in self.job_manager.jobs.values() 
                                        if j['state'] in [JobStateEnum.pending, JobStateEnum.pending_held]])
            
            logging.info(t('job_completed_successfully', job_id=job_id))
            
        except Exception as e:
            logging.error(t('error_processing_job', job_id=job_id, error=str(e)))
            self.job_manager.update_job_state(job_id, JobStateEnum.aborted, [b'job-aborted-by-system'])
            
            # 更新打印机状态 - Update printer state
            active_jobs = [j for j in self.job_manager.jobs.values() 
                          if j['state'] in [JobStateEnum.processing, JobStateEnum.pending]]
            if not active_jobs and self.printer_state == PrinterStateEnum.processing:
                self.printer_state = PrinterStateEnum.idle
            
            # 更新排队作业计数 - Update queued job count
            self.queued_job_count = len([j for j in self.job_manager.jobs.values() 
                                        if j['state'] in [JobStateEnum.pending, JobStateEnum.pending_held]])

    def handle_pdf(self, ipp_request, pdf_file, pdf_data, job_attributes=None):
        """处理PDF文件 - 子类需要重写此方法 - Handle PDF file - subclass needs to override this method"""
        raise NotImplementedError(t('pdf_handler_not_implemented'))


class StatelessPrinter(Behaviour):
    """A minimal printer which implements all the things a printer needs to work. - 实现打印机工作所需所有功能的最小打印机"""

    def __init__(self, ppd=BasicPdfPPD(), uri=DEFAULT_PRINTER_URI, name=DEFAULT_PRINTER_NAME, description=DEFAULT_PRINTER_DESCRIPTION, location=DEFAULT_PRINTER_LOCATION, printer_uuid=DEFAULT_PRINTER_UUID):
        super().__init__(ppd=ppd, uri=uri, name=name, description=description, location=location, printer_uuid=printer_uuid)


class RejectAllPrinter(StatelessPrinter):
    """A printer that rejects all the print jobs it receives. - 拒绝接收到的所有打印作业的打印机"""

    def operation_get_job_attributes_response(self, req, _psfile):
        job_id = get_job_id(req)
        job = self.job_manager.get_job(job_id)
        
        if not job:
            return IppRequest(
                (1, 1),
                StatusCodeEnum.client_error_not_found,
                req.request_id,
                self.minimal_attributes())
        
        attributes = self.get_job_attributes_dict(job_id)
        return IppRequest(
            (1, 1),
            StatusCodeEnum.server_error_job_canceled,
            req.request_id,
            attributes)


class SaveFilePrinter(StatelessPrinter):
    def __init__(self, directory, uri=DEFAULT_PRINTER_URI, name=DEFAULT_PRINTER_NAME, description=DEFAULT_PRINTER_DESCRIPTION, location=DEFAULT_PRINTER_LOCATION, printer_uuid=DEFAULT_PRINTER_UUID):
        self.directory = directory
        super().__init__(ppd=BasicPdfPPD(), uri=uri, name=name, description=description, location=location, printer_uuid=printer_uuid)

    def handle_pdf(self, ipp_request, pdf_file, pdf_data, job_attributes=None):
        try:
            filename = self.filename(ipp_request, job_attributes)
            logging.info(t('saving_print_job_as', filename=filename))
            
            # 确保目录存在 - Ensure directory exists
            os.makedirs(self.directory, exist_ok=True)
            
            # 保存PDF数据 - Save PDF data
            if pdf_data:
                with open(filename, 'wb') as diskfile:
                    diskfile.write(pdf_data)
                
                self.run_after_saving(filename, ipp_request, job_attributes)
                logging.info(t('successfully_saved_job', filename=filename, size=len(pdf_data)))
            else:
                logging.warning(t('no_pdf_data_to_save'))
                
        except Exception as e:
            logging.error(t('error_saving_pdf_file', error=str(e)))
            raise

    def run_after_saving(self, filename, ipp_request, job_attributes=None):
        pass

    def filename(self, ipp_request, job_attributes=None):
        leaf = self.leaf_filename(ipp_request, job_attributes)
        return os.path.join(self.directory, leaf)

    def leaf_filename(self, ipp_request, job_attributes=None):
        job_name = ipp_request.lookup(SectionEnum.operation, b'job-name', TagEnum.name_without_language)
        if job_name:
            # 解码为UTF-8，支持中文文件名 - Decode as UTF-8, supports Chinese filenames
            base_name = job_name[0].decode('utf-8', errors='ignore')
            
            # 清理文件名：移除非法字符，保留中文 - Clean filename: remove illegal characters, keep Chinese
            # Windows不允许的字符：\ / : * ? " < > | - Characters not allowed in Windows: \ / : * ? " < > |
            base_name = re.sub(r'[\\/*?:"<>|]', '_', base_name)
            
            # 如果清理后名称为空，使用默认名称 - If name is empty after cleaning, use default name
            if not base_name.strip():
                base_name = t('default_print_job_name')
        else:
            base_name = t('default_print_job_name')
        
        # 添加打印参数信息到文件名 - Add printing parameter information to filename
        params = []
        if job_attributes:
            if 'media' in job_attributes:
                media_name = job_attributes['media'].split('_')[0]
                params.append(media_name)
            if 'print_color_mode' in job_attributes:
                color_name = job_attributes['print_color_mode'][:3]
                params.append(color_name)
            if 'copies' in job_attributes and job_attributes['copies'] > 1:
                params.append(f"{job_attributes['copies']}x")
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        random_suffix = uuid.uuid4().hex[:8]
        
        if params:
            params_str = '_'.join(params)
            return f'{base_name}_{params_str}_{timestamp}_{random_suffix}.pdf'
        else:
            return f'{base_name}_{timestamp}_{random_suffix}.pdf'


class SaveAndRunPrinter(SaveFilePrinter):
    def __init__(self, directory, use_env, command, uri=DEFAULT_PRINTER_URI, name=DEFAULT_PRINTER_NAME, description=DEFAULT_PRINTER_DESCRIPTION, location=DEFAULT_PRINTER_LOCATION, printer_uuid=DEFAULT_PRINTER_UUID):
        self.command = command
        self.use_env = use_env
        super().__init__(
            directory=directory, uri=uri, name=name, description=description, location=location, printer_uuid=printer_uuid
        )

    def run_after_saving(self, filename, ipp_request, job_attributes=None):
        try:
            env = prepare_environment(ipp_request) if self.use_env else None
            full_command = self.command + [filename]
            
            # 添加打印参数到环境变量 - Add printing parameters to environment variables
            if job_attributes:
                env = env or os.environ.copy()
                for key, value in job_attributes.items():
                    env[f'IPP_JOB_{key.upper()}'] = str(value)
            
            logging.info(t('running_command', command=' '.join(full_command)))
            
            proc = subprocess.Popen(full_command,
                                  env=env,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  universal_newlines=True)
            
            stdout, stderr = proc.communicate(timeout=300)  # 5 minute timeout - 5分钟超时
            
            if proc.returncode != 0:
                logging.error(
                    t('command_exited_with_code'),
                    proc.returncode,
                    stdout,
                    stderr
                )
                raise RuntimeError(t('command_failed_with_exit_code', code=proc.returncode))
            else:
                logging.info(t('command_executed_successfully', output=stdout))
                
        except subprocess.TimeoutExpired:
            logging.error(t('command_timed_out'))
            if proc:
                proc.kill()
            raise RuntimeError(t('command_timed_out'))
        except Exception as e:
            logging.error(t('error_running_command', error=str(e)))
            raise


class RunCommandPrinter(StatelessPrinter):
    def __init__(self, command, use_env, uri=DEFAULT_PRINTER_URI, name=DEFAULT_PRINTER_NAME, description=DEFAULT_PRINTER_DESCRIPTION, location=DEFAULT_PRINTER_LOCATION, printer_uuid=DEFAULT_PRINTER_UUID):
        self.command = command
        self.use_env = use_env
        super().__init__(ppd=BasicPdfPPD(), uri=uri, name=name, description=description, location=location, printer_uuid=printer_uuid)

    def handle_pdf(self, ipp_request, pdf_file, pdf_data, job_attributes=None):
        logging.info(t('running_command_for_job_with_pdf'))
        
        try:
            # 确保文件指针在开头 - Ensure file pointer is at the beginning
            if hasattr(pdf_file, 'seek'):
                pdf_file.seek(0)
            
            env = prepare_environment(ipp_request) if self.use_env else None
            
            # 添加打印参数到环境变量 - Add printing parameters to environment variables
            if job_attributes:
                env = env or os.environ.copy()
                for key, value in job_attributes.items():
                    env[f'IPP_JOB_{key.upper()}'] = str(value)
            
            logging.info(t('running_command', command=' '.join(self.command)))
            
            proc = subprocess.Popen(
                self.command,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True)
            
            data = pdf_file.read()
            if not data:
                logging.warning(t('no_pdf_data_to_process'))
                data = b''
            
            stdout, stderr = proc.communicate(data.decode('utf-8', errors='ignore') if isinstance(data, bytes) else data, 
                                             timeout=300)  # 5 minute timeout - 5分钟超时
            
            if proc.returncode != 0:
                logging.error(
                    t('command_exited_with_code'),
                    proc.returncode,
                    stdout,
                    stderr
                )
                raise RuntimeError(t('command_failed_with_exit_code', code=proc.returncode))
            else:
                logging.info(t('command_executed_successfully', output=stdout))
                
        except subprocess.TimeoutExpired:
            logging.error(t('command_timed_out'))
            if proc:
                proc.kill()
            raise RuntimeError(t('command_timed_out'))
        except Exception as e:
            logging.error(t('error_running_command', error=str(e)))
            raise


class PostageServicePrinter(StatelessPrinter):
    def __init__(self, service_api, uri=DEFAULT_PRINTER_URI, name=DEFAULT_PRINTER_NAME, description=DEFAULT_PRINTER_DESCRIPTION, location=DEFAULT_PRINTER_LOCATION, printer_uuid=DEFAULT_PRINTER_UUID):
        self.service_api = service_api
        super().__init__(ppd=BasicPdfPPD(), uri=uri, name=name, description=description, location=location, printer_uuid=printer_uuid)

    def handle_pdf(self, ipp_request, pdf_file, pdf_data, job_attributes=None):
        # 确保文件指针在开头 - Ensure file pointer is at the beginning
        if hasattr(pdf_file, 'seek'):
            pdf_file.seek(0)
        
        # 在文件名中包含打印参数 - Include printing parameters in filename
        timestamp = int(time.time())
        if job_attributes and 'media' in job_attributes:
            media_name = job_attributes['media'].split('_')[0]
            filename = f'ipp-server-{media_name}-{timestamp}.pdf'
        else:
            filename = f'ipp-server-{timestamp}.pdf'
        
        if pdf_data:
            self.service_api.post_pdf_letter(filename, pdf_data)
            logging.info(t('posted_pdf_document_to_service', filename=filename, size=len(pdf_data)))
        else:
            logging.warning(t('no_pdf_data_to_post'))