from enum import IntEnum


class SectionEnum(IntEnum):
    # 分隔符（段）- Delimiters (sections)
    SECTIONS = 0x00
    SECTIONS_MASK = 0xf0
    operation = 0x01  # 操作段 - Operation section
    job = 0x02        # 作业段 - Job section
    END = 0x03        # 结束标记 - End marker
    printer = 0x04    # 打印机段 - Printer section
    unsupported = 0x05  # 不支持段 - Unsupported section

    @classmethod
    def is_section_tag(cls, tag):
        # 检查是否为段标记 - Check if tag is a section tag
        return (tag & cls.SECTIONS_MASK) == cls.SECTIONS


class TagEnum(IntEnum):
    # 值类型 - Value types
    unsupported_value = 0x10  # 不支持的值 - Unsupported value
    unknown_value = 0x12      # 未知值 - Unknown value
    no_value = 0x13           # 无值 - No value

    # 整数类型 - Integer types
    integer = 0x21            # 整数 - Integer
    boolean = 0x22            # 布尔值 - Boolean
    enum = 0x23               # 枚举 - Enum

    # 字符串类型 - String types
    octet_str = 0x30          # 八位字节字符串 - Octet string
    datetime_str = 0x31       # 日期时间字符串 - Datetime string
    resolution = 0x32         # 分辨率 - Resolution
    range_of_integer = 0x33   # 整数范围 - Range of integer
    text_with_language = 0x35 # 带语言的文本 - Text with language
    name_with_language = 0x36 # 带语言的名称 - Name with language

    text_without_language = 0x41  # 无语言的文本 - Text without language
    name_without_language = 0x42  # 无语言的名称 - Name without language
    keyword = 0x44                # 关键字 - Keyword
    uri = 0x45                    # URI - URI
    uri_scheme = 0x46             # URI方案 - URI scheme
    charset = 0x47                # 字符集 - Charset
    natural_language = 0x48       # 自然语言 - Natural language
    mime_media_type = 0x49        # MIME媒体类型 - MIME media type


class StatusCodeEnum(IntEnum):
    # RFC 8011 - IPP Version 1.1
    # 成功状态码 - Successful status codes
    ok = 0x0000  # 成功 - OK
    successful_ok = 0x0000  # 成功完成 - Successful OK
    successful_ok_ignored_or_substituted_attributes = 0x0001  # 成功，忽略或替换属性 - Successful OK, ignored or substituted attributes
    successful_ok_conflicting_attributes = 0x0002  # 成功，冲突属性 - Successful OK, conflicting attributes
    
    # 客户端错误状态码 - Client error status codes
    client_error_bad_request = 0x0400  # 错误请求 - Bad request
    client_error_forbidden = 0x0401    # 禁止访问 - Forbidden
    client_error_not_authenticated = 0x0402  # 未认证 - Not authenticated
    client_error_not_authorized = 0x0403     # 未授权 - Not authorized
    client_error_not_possible = 0x0404       # 不可行 - Not possible
    client_error_timeout = 0x0405            # 超时 - Timeout
    client_error_not_found = 0x0406          # 未找到 - Not found
    client_error_gone = 0x0407               # 已不存在 - Gone
    client_error_request_entity_too_large = 0x0408  # 请求实体过大 - Request entity too large
    client_error_request_value_too_long = 0x0409    # 请求值过长 - Request value too long
    client_error_document_format_not_supported = 0x040A  # 文档格式不支持 - Document format not supported
    client_error_attributes_or_values_not_supported = 0x040B  # 属性或值不支持 - Attributes or values not supported
    client_error_uri_scheme_not_supported = 0x040C  # URI方案不支持 - URI scheme not supported
    client_error_charset_not_supported = 0x040D     # 字符集不支持 - Charset not supported
    client_error_conflicting_attributes = 0x040E    # 冲突属性 - Conflicting attributes
    client_error_compression_not_supported = 0x040F # 压缩不支持 - Compression not supported
    client_error_compression_error = 0x0410         # 压缩错误 - Compression error
    client_error_document_format_error = 0x0411     # 文档格式错误 - Document format error
    client_error_document_access_error = 0x0412     # 文档访问错误 - Document access error
    
    # 服务器错误状态码 - Server error status codes
    server_error_internal_error = 0x0500            # 内部服务器错误 - Internal server error
    server_error_operation_not_supported = 0x0501   # 操作不支持 - Operation not supported
    server_error_service_unavailable = 0x0502       # 服务不可用 - Service unavailable
    server_error_version_not_supported = 0x0503     # 版本不支持 - Version not supported
    server_error_device_error = 0x0504              # 设备错误 - Device error
    server_error_temporary_error = 0x0505           # 临时错误 - Temporary error
    server_error_not_accepting_jobs = 0x0506        # 不接受作业 - Not accepting jobs
    server_error_busy = 0x0507                      # 繁忙 - Busy
    server_error_job_canceled = 0x0508              # 作业已取消 - Job canceled
    server_error_multiple_document_jobs_not_supported = 0x0509  # 多文档作业不支持 - Multiple document jobs not supported


class OperationEnum(IntEnum):
    # RFC 8011 - IPP Version 1.1
    print_job = 0x0002                # 打印作业 - Print job
    print_uri = 0x0003                # 打印URI - Print URI
    validate_job = 0x0004             # 验证作业 - Validate job
    create_job = 0x0005               # 创建作业 - Create job
    send_document = 0x0006            # 发送文档 - Send document
    send_uri = 0x0007                 # 发送URI - Send URI
    cancel_job = 0x0008               # 取消作业 - Cancel job
    get_job_attributes = 0x0009       # 获取作业属性 - Get job attributes
    get_jobs = 0x000A                 # 获取作业列表 - Get jobs
    get_printer_attributes = 0x000B   # 获取打印机属性 - Get printer attributes
    hold_job = 0x000C                 # 保持作业 - Hold job
    release_job = 0x000D              # 释放作业 - Release job
    restart_job = 0x000E              # 重新启动作业 - Restart job
    pause_printer = 0x0010            # 暂停打印机 - Pause printer
    resume_printer = 0x0011           # 恢复打印机 - Resume printer
    purge_jobs = 0x0012               # 清除作业 - Purge jobs

    # CUPS扩展 (0x4000 - 0xFFFF) - CUPS extensions (0x4000 - 0xFFFF)
    cups_get_default = 0x4001         # CUPS获取默认打印机 - CUPS get default printer
    cups_list_all_printers = 0x4002   # CUPS列出所有打印机 - CUPS list all printers
    cups_get_ppd = 0x4003             # CUPS获取PPD - CUPS get PPD
    cups_move_job = 0x4004            # CUPS移动作业 - CUPS move job
    cups_authenticate_job = 0x4005    # CUPS认证作业 - CUPS authenticate job


class JobStateEnum(IntEnum):
    # RFC 8011 - IPP Version 1.1
    pending = 3                # 挂起 - Pending
    pending_held = 4           # 挂起保持 - Pending held
    processing = 5             # 处理中 - Processing
    processing_stopped = 6     # 处理停止 - Processing stopped
    canceled = 7               # 已取消 - Canceled
    aborted = 8                # 已中止 - Aborted
    completed = 9              # 已完成 - Completed


class PrinterStateEnum(IntEnum):
    # RFC 8011 - IPP Version 1.1
    idle = 3                   # 空闲 - Idle
    processing = 4             # 处理中 - Processing
    stopped = 5                # 已停止 - Stopped


class PrinterStateReasonsEnum(IntEnum):
    # 通用打印机状态原因 - Common printer state reasons
    none = 0                     # 无 - None
    media_needed = 1             # 需要介质 - Media needed
    media_jam = 2                # 介质卡纸 - Media jam
    moving_to_paused = 3         # 正在移动到暂停 - Moving to paused
    paused = 4                   # 已暂停 - Paused
    shutdown = 5                 # 关机 - Shutdown
    connecting_to_device = 6     # 正在连接设备 - Connecting to device
    timed_out = 7                # 超时 - Timed out
    stopping = 8                 # 正在停止 - Stopping
    stopped_partly = 9           # 部分停止 - Stopped partly
    toner_low = 10               # 墨粉不足 - Toner low
    toner_empty = 11             # 墨粉耗尽 - Toner empty
    spool_area_full = 12         # 缓冲池区域已满 - Spool area full
    cover_open = 13              # 盖子打开 - Cover open
    interlock_open = 14          # 联锁打开 - Interlock open
    door_open = 15               # 门打开 - Door open
    input_tray_missing = 16      # 输入托盘缺失 - Input tray missing
    output_tray_missing = 17     # 输出托盘缺失 - Output tray missing
    marker_supply_low = 18       # 标记剂供应不足 - Marker supply low
    marker_supply_empty = 19     # 标记剂耗尽 - Marker supply empty
    output_tray_full = 20        # 输出托盘已满 - Output tray full


class IppVersionEnum(IntEnum):
    # 支持的IPP版本 - Supported IPP versions
    v1_0 = 0x0100  # IPP 1.0版本 - IPP Version 1.0
    v1_1 = 0x0101  # IPP 1.1版本 - IPP Version 1.1
    v2_0 = 0x0200  # IPP 2.0版本 - IPP Version 2.0
    v2_1 = 0x0201  # IPP 2.1版本 - IPP Version 2.1
    v2_2 = 0x0202  # IPP 2.2版本 - IPP Version 2.2


class PrintQualityEnum(IntEnum):
    """IPP打印质量值 - IPP Print Quality values"""
    draft = 3   # 草稿质量 - Draft quality
    normal = 4  # 普通质量 - Normal quality
    high = 5    # 高质量 - High quality


class PrintColorModeEnum(IntEnum):
    """IPP打印颜色模式值（简化）- IPP Print Color Mode values (simplified)"""
    auto = 0        # 自动 - Auto
    color = 1       # 彩色 - Color
    monochrome = 2  # 单色 - Monochrome


class ColorSupportedEnum(IntEnum):
    """IPP颜色支持值 - IPP Color Support values"""
    color = 3        # 支持彩色 - Color supported
    monochrome = 4   # 支持单色 - Monochrome supported