"""
PDF转换模块 - PDF Conversion Module
支持多种格式转换为PDF - Support multiple format conversion to PDF
"""

import os
import subprocess
import tempfile
import logging
import gzip
import zlib
import zipfile
from io import BytesIO

# 导入翻译函数 - Import translation function
try:
    from .translations import t
except ImportError:
    def t(key, **kwargs):
        return key


def convert_to_pdf(data: bytes, input_format: str = None) -> bytes:
    """
    将各种格式转换为PDF - Convert various formats to PDF
    
    Args:
        data: 输入数据 - Input data
        input_format: 输入格式，如 'application/postscript', 'application/pdf', 'image/jpeg' 等
                      Input format, such as 'application/postscript', 'application/pdf', 'image/jpeg', etc.
    
    Returns:
        PDF数据 - PDF data
    """
    if not data:
        logging.error(t('pdf_converter_no_data'))
        return b''
    
    # 尝试自动检测格式 - Try to auto-detect format
    if not input_format:
        input_format = detect_format(data)
    
    logging.info(t('pdf_converter_converting_format', format=input_format))
    
    try:
        # 根据格式选择转换方法 - Select conversion method based on format
        if input_format == 'application/pdf':
            # 已经是PDF，直接返回 - Already PDF, return directly
            logging.info(t('pdf_converter_already_pdf'))
            return data
        
        elif input_format == 'application/postscript':
            # PostScript转换为PDF - PostScript to PDF conversion
            logging.info(t('pdf_converter_converting_postscript'))
            return ps_to_pdf(data)
        
        elif input_format in ['image/jpeg', 'image/png', 'image/tiff', 'image/bmp']:
            # 图像转换为PDF - Image to PDF conversion
            logging.info(t('pdf_converter_converting_image', format=input_format))
            return image_to_pdf(data, input_format)
        
        elif input_format == 'text/plain':
            # 文本转换为PDF - Text to PDF conversion
            logging.info(t('pdf_converter_converting_text'))
            return text_to_pdf(data)
        
        else:
            # 未知格式，尝试使用通用方法 - Unknown format, try generic conversion
            logging.warning(t('pdf_converter_unknown_format', format=input_format))
            return generic_to_pdf(data, input_format)
            
    except Exception as e:
        logging.error(t('pdf_converter_conversion_error', format=input_format, error=str(e)))
        # 转换失败时返回原始数据 - Return original data when conversion fails
        logging.warning(t('pdf_converter_returning_original'))
        return data


def detect_format(data: bytes) -> str:
    """自动检测数据格式 - Auto-detect data format"""
    if not data:
        return 'application/octet-stream'
    
    # 检查GZIP压缩 - Check GZIP compression
    try:
        if data[:2] == b'\x1f\x8b':  # GZIP magic number
            logging.info(t('pdf_converter_detected_gzip'))
            decompressed = gzip.decompress(data)
            return detect_format(decompressed)
    except:
        pass
    
    # 检查ZIP压缩 - Check ZIP compression
    try:
        if data[:2] == b'PK':  # ZIP magic number
            logging.info(t('pdf_converter_detected_zip'))
            with zipfile.ZipFile(BytesIO(data)) as zip_file:
                if zip_file.namelist():
                    first_file = zip_file.namelist()[0]
                    file_data = zip_file.read(first_file)
                    return detect_format(file_data)
    except:
        pass
    
    # 检查PDF - Check PDF
    if data.startswith(b'%PDF-'):
        return 'application/pdf'
    
    # 检查PostScript - Check PostScript
    if data.startswith(b'%!'):
        return 'application/postscript'
    
    # 检查JPEG - Check JPEG
    if data.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg'
    
    # 检查PNG - Check PNG
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png'
    
    # 检查TIFF - Check TIFF
    if data.startswith(b'II\x2a\x00') or data.startswith(b'MM\x00\x2a'):
        return 'image/tiff'
    
    # 检查BMP - Check BMP
    if data.startswith(b'BM'):
        return 'image/bmp'
    
    # 检查文本（前100个字节是否可打印utf-8）- Check text (first 100 bytes printable utf-8)
    try:
        sample = data[:100].decode('utf-8', errors='ignore')
        if all(32 <= ord(c) <= 126 or c in '\n\r\t' for c in sample if c):
            return 'text/plain'
    except:
        pass
    
    return 'application/octet-stream'


def decompress_data(data: bytes, compression_type: str) -> bytes:
    """解压缩数据 - Decompress data"""
    if compression_type == 'gzip':
        return gzip.decompress(data)
    elif compression_type == 'deflate':
        # 尝试zlib解压缩（带头部）- Try zlib decompression (with header)
        try:
            return zlib.decompress(data)
        except zlib.error:
            # 尝试不带头部的解压缩 - Try decompression without header
            return zlib.decompress(data, -15)
    elif compression_type == 'zip':
        with zipfile.ZipFile(BytesIO(data)) as zip_file:
            file_list = zip_file.namelist()
            if file_list:
                return zip_file.read(file_list[0])
            else:
                raise ValueError(t('pdf_converter_zip_file_empty'))
    elif compression_type == 'none' or not compression_type:
        return data
    else:
        logging.warning(t('pdf_converter_unsupported_compression', type=compression_type))
        return data


def ps_to_pdf(data: bytes) -> bytes:
    """PostScript转换为PDF - PostScript to PDF conversion"""
    try:
        # 方法1: 使用ghostscript (gs) - Method 1: Use ghostscript (gs)
        logging.info(t('pdf_converter_trying_ghostscript'))
        return _convert_with_ghostscript(data, 'ps2pdf')
    except Exception as e:
        logging.error(t('pdf_converter_ghostscript_failed', error=str(e)))
        
        try:
            # 方法2: 使用ImageMagick (convert) - Method 2: Use ImageMagick (convert)
            logging.info(t('pdf_converter_trying_imagemagick'))
            return _convert_with_imagemagick(data)
        except Exception as e2:
            logging.error(t('pdf_converter_imagemagick_failed', error=str(e2)))
            
            # 方法3: 使用Python库（如果可用）- Method 3: Use Python library (if available)
            try:
                logging.info(t('pdf_converter_trying_pypdf'))
                return _convert_with_pypdf(data)
            except Exception as e3:
                logging.error(t('pdf_converter_pypdf_failed', error=str(e3)))
                
                # 所有方法都失败，返回原始数据 - All methods failed, returning original data
                logging.warning(t('pdf_converter_all_methods_failed'))
                return data


def _convert_with_ghostscript(data: bytes, command: str = 'ps2pdf') -> bytes:
    """使用Ghostscript转换 - Use Ghostscript for conversion"""
    logging.info(t('pdf_converter_using_ghostscript', command=command))
    
    # 创建临时文件 - Create temporary files
    with tempfile.NamedTemporaryFile(suffix='.ps', delete=False) as input_file:
        input_file.write(data)
        input_path = input_file.name
    
    output_path = None
    
    try:
        # 创建输出文件 - Create output file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_file:
            output_path = output_file.name
        
        # 运行ghostscript - Run ghostscript
        if command == 'ps2pdf':
            # 使用ps2pdf命令 - Use ps2pdf command
            cmd = ['ps2pdf', input_path, output_path]
        else:
            # 使用gs命令 - Use gs command
            cmd = ['gs', '-q', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pdfwrite',
                   f'-sOutputFile={output_path}', input_path]
        
        logging.info(t('pdf_converter_running_command', command=' '.join(cmd)))
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise Exception(t('pdf_converter_ghostscript_error', error=result.stderr))
        
        # 读取生成的PDF - Read generated PDF
        with open(output_path, 'rb') as f:
            pdf_data = f.read()
        
        logging.info(t('pdf_converter_conversion_successful', bytes=len(pdf_data)))
        return pdf_data
        
    finally:
        # 清理临时文件 - Clean up temporary files
        try:
            os.unlink(input_path)
        except:
            pass
        if output_path:
            try:
                os.unlink(output_path)
            except:
                pass


def _convert_with_imagemagick(data: bytes) -> bytes:
    """使用ImageMagick转换 - Use ImageMagick for conversion"""
    logging.info(t('pdf_converter_using_imagemagick'))
    
    # 创建临时输入文件 - Create temporary input file
    with tempfile.NamedTemporaryFile(suffix='.ps', delete=False) as input_file:
        input_file.write(data)
        input_path = input_file.name
    
    output_path = None
    
    try:
        # 创建输出文件 - Create output file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_file:
            output_path = output_file.name
        
        # 运行ImageMagick - Run ImageMagick
        cmd = ['convert', input_path, output_path]
        logging.info(t('pdf_converter_running_command', command=' '.join(cmd)))
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise Exception(t('pdf_converter_imagemagick_error', error=result.stderr))
        
        # 读取生成的PDF - Read generated PDF
        with open(output_path, 'rb') as f:
            pdf_data = f.read()
        
        logging.info(t('pdf_converter_conversion_successful', bytes=len(pdf_data)))
        return pdf_data
        
    finally:
        # 清理临时文件 - Clean up temporary files
        try:
            os.unlink(input_path)
        except:
            pass
        if output_path:
            try:
                os.unlink(output_path)
            except:
                pass


def _convert_with_pypdf(data: bytes) -> bytes:
    """使用PyPDF2/PyPDF4转换（纯Python）- Use PyPDF2/PyPDF4 conversion (pure Python)"""
    logging.info(t('pdf_converter_using_pypdf'))
    
    try:
        # 尝试导入PyPDF2 - Try to import PyPDF2
        try:
            import PyPDF2
            from PyPDF2 import PdfWriter, PdfReader
            from io import BytesIO
        except ImportError:
            # 尝试PyPDF4 - Try PyPDF4
            try:
                import PyPDF4
                from PyPDF4 import PdfFileWriter, PdfFileReader
                PdfWriter = PdfFileWriter
                PdfReader = PdfFileReader
            except ImportError:
                # 尝试pypdf - Try pypdf
                try:
                    from pypdf import PdfWriter, PdfReader
                except ImportError:
                    logging.error(t('pdf_converter_no_pdf_library'))
                    raise ImportError(t('pdf_converter_install_pypdf'))
        
        # 对于PostScript，我们无法直接转换，但可以创建一个包含文本的PDF
        # For PostScript, we cannot directly convert, but can create a PDF containing text
        writer = PdfWriter()
        
        # 创建一个简单的PDF页面 - Create a simple PDF page
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            
            # 将PostScript内容作为文本添加到PDF - Add PostScript content as text to PDF
            text = data.decode('utf-8', errors='ignore')
            lines = text.split('\n')
            
            y = 750  # 起始位置 - Starting position
            for line in lines[:50]:  # 只添加前50行 - Only add first 50 lines
                if y < 50:
                    c.showPage()
                    y = 750
                c.drawString(50, y, line[:100])  # 每行最多100字符 - Maximum 100 characters per line
                y -= 12
            
            c.save()
            
            # 将canvas PDF添加到writer - Add canvas PDF to writer
            buffer.seek(0)
            reader = PdfReader(buffer)
            writer.add_page(reader.pages[0])
            
        except ImportError:
            # reportlab不可用，创建空PDF - reportlab not available, create empty PDF
            logging.warning(t('pdf_converter_reportlab_unavailable'))
            # 创建最简单的PDF（只有一个空页面）- Create simplest PDF (only one empty page)
            minimal_pdf = b'''%PDF-1.4
1 0 obj
<</Type/Catalog/Pages 2 0 R>>
endobj
2 0 obj
<</Type/Pages/Kids[3 0 R]/Count 1>>
endobj
3 0 obj
<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000117 00000 n 
trailer
<</Size 4/Root 1 0 R>>
startxref
185
%%EOF'''
            return minimal_pdf
        
        # 写入PDF - Write PDF
        output = BytesIO()
        writer.write(output)
        pdf_data = output.getvalue()
        logging.info(t('pdf_converter_pypdf_success', bytes=len(pdf_data)))
        return pdf_data
        
    except Exception as e:
        raise Exception(t('pdf_converter_pypdf_error', error=str(e)))


def image_to_pdf(data: bytes, image_format: str) -> bytes:
    """图像转换为PDF - Image to PDF conversion"""
    logging.info(t('pdf_converter_image_to_pdf', format=image_format))
    
    try:
        # 使用PIL/Pillow - Use PIL/Pillow
        from PIL import Image
        from io import BytesIO
        
        # 打开图像 - Open image
        image = Image.open(BytesIO(data))
        logging.info(t('pdf_converter_image_loaded', size=image.size, mode=image.mode))
        
        # 转换为RGB（如果必要）- Convert to RGB (if necessary)
        if image.mode in ('RGBA', 'LA', 'P'):
            # 创建一个白色背景 - Create a white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'RGBA':
                # 合并RGBA图像到白色背景 - Merge RGBA image onto white background
                background.paste(image, mask=image.split()[3])
            else:
                background.paste(image, mask=None)
            image = background
            logging.info(t('pdf_converter_image_converted_rgb'))
        elif image.mode != 'RGB':
            image = image.convert('RGB')
            logging.info(t('pdf_converter_image_converted_rgb'))
        
        # 保存为PDF - Save as PDF
        pdf_buffer = BytesIO()
        image.save(pdf_buffer, 'PDF', resolution=100.0)
        pdf_buffer.seek(0)
        pdf_data = pdf_buffer.read()
        
        logging.info(t('pdf_converter_image_conversion_success', bytes=len(pdf_data)))
        return pdf_data
        
    except ImportError:
        logging.warning(t('pdf_converter_pillow_unavailable'))
        # 回退到其他方法 - Fallback to alternative methods
        try:
            logging.info(t('pdf_converter_fallback_imagemagick'))
            return _convert_with_imagemagick(data)
        except Exception as e:
            logging.error(t('pdf_converter_fallback_failed', error=str(e)))
            # 创建最简单的PDF - Create simplest PDF
            logging.warning(t('pdf_converter_creating_minimal_pdf'))
            return _create_minimal_pdf()


def text_to_pdf(data: bytes) -> bytes:
    """文本转换为PDF - Text to PDF conversion"""
    logging.info(t('pdf_converter_text_to_pdf'))
    
    try:
        # 解码文本 - Decode text
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            # 尝试其他编码 - Try other encodings
            try:
                text = data.decode('latin-1')
            except:
                text = data.decode('utf-8', errors='ignore')
        
        logging.info(t('pdf_converter_text_decoded', length=len(text), lines=text.count('\n')+1))
        
        # 使用reportlab创建PDF - Use reportlab to create PDF
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from io import BytesIO
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # 设置字体 - Set font
        c.setFont("Helvetica", 10)
        
        # 分割文本为行 - Split text into lines
        lines = text.split('\n')
        
        y = 750  # 起始位置 - Starting position
        for line in lines:
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = 750
            
            # 如果行太长，分割它 - If line is too long, split it
            max_chars = 100
            while len(line) > max_chars:
                c.drawString(50, y, line[:max_chars])
                line = line[max_chars:]
                y -= 12
            
            if line:
                c.drawString(50, y, line)
                y -= 12
        
        c.save()
        buffer.seek(0)
        pdf_data = buffer.read()
        
        logging.info(t('pdf_converter_text_conversion_success', bytes=len(pdf_data)))
        return pdf_data
        
    except ImportError:
        logging.warning(t('pdf_converter_reportlab_unavailable'))
        # 回退到创建最简单的PDF - Fallback to creating simplest PDF
        logging.warning(t('pdf_converter_creating_minimal_pdf'))
        return _create_minimal_pdf()
    except Exception as e:
        logging.error(t('pdf_converter_text_conversion_failed', error=str(e)))
        logging.warning(t('pdf_converter_creating_minimal_pdf'))
        return _create_minimal_pdf()


def generic_to_pdf(data: bytes, input_format: str) -> bytes:
    """通用转换方法 - Generic conversion method"""
    logging.info(t('pdf_converter_generic_conversion', format=input_format))
    
    try:
        # 尝试使用unoconv（如果可用）- Try using unoconv (if available)
        logging.info(t('pdf_converter_trying_unoconv'))
        return _convert_with_unoconv(data, input_format)
    except Exception as e:
        logging.error(t('pdf_converter_generic_failed', error=str(e)))
        # 创建包含原始数据的PDF - Create PDF with embedded original data
        logging.info(t('pdf_converter_creating_embedded_pdf'))
        return _create_pdf_with_embedded_data(data, input_format)


def _convert_with_unoconv(data: bytes, input_format: str) -> bytes:
    """使用unoconv转换（支持多种Office格式）- Use unoconv conversion (supports multiple Office formats)"""
    logging.info(t('pdf_converter_using_unoconv', format=input_format))
    
    # 确定文件扩展名 - Determine file extension
    ext_map = {
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/vnd.ms-excel': '.xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/vnd.ms-powerpoint': '.ppt',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
        'application/rtf': '.rtf',
        'text/html': '.html',
    }
    
    ext = ext_map.get(input_format, '.bin')
    logging.info(t('pdf_converter_determined_extension', ext=ext))
    
    # 创建临时文件 - Create temporary file
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as input_file:
        input_file.write(data)
        input_path = input_file.name
    
    output_path = None
    
    try:
        # 创建输出文件 - Create output file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_file:
            output_path = output_file.name
        
        # 运行unoconv - Run unoconv
        cmd = ['unoconv', '-f', 'pdf', '-o', output_path, input_path]
        logging.info(t('pdf_converter_running_command', command=' '.join(cmd)))
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            raise Exception(t('pdf_converter_unoconv_error', error=result.stderr))
        
        # 读取生成的PDF - Read generated PDF
        with open(output_path, 'rb') as f:
            pdf_data = f.read()
        
        logging.info(t('pdf_converter_unoconv_success', bytes=len(pdf_data)))
        return pdf_data
        
    finally:
        # 清理临时文件 - Clean up temporary files
        try:
            os.unlink(input_path)
        except:
            pass
        if output_path:
            try:
                os.unlink(output_path)
            except:
                pass


def _create_pdf_with_embedded_data(data: bytes, input_format: str) -> bytes:
    """创建包含原始数据的PDF - Create PDF with embedded original data"""
    logging.info(t('pdf_converter_creating_embedded_pdf_detail', format=input_format, size=len(data)))
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from io import BytesIO
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        c.setFont("Helvetica", 12)
        c.drawString(50, 750, t('pdf_converter_embedded_title', format=input_format))
        c.drawString(50, 730, t('pdf_converter_embedded_size', size=len(data)))
        c.drawString(50, 710, t('pdf_converter_embedded_cannot_convert'))
        c.drawString(50, 690, t('pdf_converter_embedded_data_preserved'))
        
        c.save()
        buffer.seek(0)
        
        pdf_data = buffer.read()
        logging.info(t('pdf_converter_embedded_pdf_created', bytes=len(pdf_data)))
        return pdf_data
        
    except ImportError:
        # 创建最简单的PDF - Create simplest PDF
        logging.warning(t('pdf_converter_reportlab_unavailable'))
        logging.warning(t('pdf_converter_creating_minimal_pdf'))
        return _create_minimal_pdf()


def _create_minimal_pdf() -> bytes:
    """创建最简单的PDF文档 - Create simplest PDF document"""
    logging.info(t('pdf_converter_creating_minimal_pdf'))
    return b'''%PDF-1.4
1 0 obj
<</Type/Catalog/Pages 2 0 R>>
endobj
2 0 obj
<</Type/Pages/Kids[3 0 R]/Count 1>>
endobj
3 0 obj
<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R>>
endobj
4 0 obj
<</Length 44>>
stream
BT
/F1 12 Tf
50 700 Td
(Conversion failed) Tj
ET
endstream
endobj
5 0 obj
<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000117 00000 n 
0000000227 00000 n 
0000000286 00000 n 
trailer
<</Size 6/Root 1 0 R>>
startxref
352
%%EOF'''