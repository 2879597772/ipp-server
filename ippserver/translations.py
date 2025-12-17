# 翻译文件 - Translations File
# 支持多语言打印输出和日志信息 - Support multi-language print output and log messages

# 语言代码 - Language codes
LANG_ZH = 'zh'  # 中文 - Chinese
LANG_EN = 'en'  # 英文 - English

# 当前语言设置 - Current language setting
CURRENT_LANG = LANG_ZH  # 默认中文 - Default Chinese

# 翻译字典 - Translation dictionary
TRANSLATIONS = {
    # 通用消息 - General messages
    'ssl_certificate_valid': {
        LANG_ZH: "✓ SSL证书有效，HTTPS已启用",
        LANG_EN: "✓ SSL certificate is valid, HTTPS enabled"
    },
    'ssl_certificate_invalid': {
        LANG_ZH: "✗ SSL证书无效或缺失，HTTPS已禁用",
        LANG_EN: "✗ SSL certificate is invalid or missing, HTTPS disabled"
    },
    'ssl_enabled': {
        LANG_ZH: "SSL/TLS支持已启用 - SSL/TLS support enabled",
        LANG_EN: "SSL/TLS support enabled"
    },
    'ssl_disabled': {
        LANG_ZH: "SSL/TLS支持已禁用 - SSL/TLS support disabled",
        LANG_EN: "SSL/TLS support disabled"
    },
    # 服务器启动消息 - Server startup messages
    'server_starting': {
        LANG_ZH: "服务器正在启动...",
        LANG_EN: "Server starting..."
    },
    'http_server_started': {
        LANG_ZH: "✓ HTTP服务器已启动于 http://{host}:{port}",
        LANG_EN: "✓ HTTP server started on http://{host}:{port}"
    },
    'https_server_started': {
        LANG_ZH: "✓ HTTPS服务器已启动于 https://{host}:{port}",
        LANG_EN: "✓ HTTPS server started on https://{host}:{port}"
    },
    'mdns_broadcasting_started': {
        LANG_ZH: "mDNS广播已启动，打印机: {name}",
        LANG_EN: "mDNS broadcasting started for printer: {name}"
    },
    'mdns_broadcasting_stopped': {
        LANG_ZH: "mDNS广播已停止 - mDNS broadcasting stopped",
        LANG_EN: "mDNS broadcasting stopped"
    },
    'mdns_broadcast_failed': {
        LANG_ZH: "mDNS广播启动失败: {error}",
        LANG_EN: "Failed to start mDNS broadcasting: {error}"
    },
    # 打印机信息 - Printer information
    'printer_info': {
        LANG_ZH: "打印机信息",
        LANG_EN: "Printer Information"
    },
    'printer_name': {
        LANG_ZH: "打印机名称",
        LANG_EN: "Printer Name"
    },
    'printer_description': {
        LANG_ZH: "打印机描述",
        LANG_EN: "Printer Description"
    },
    'printer_location': {
        LANG_ZH: "打印机位置",
        LANG_EN: "Printer Location"
    },
    'printer_uuid': {
        LANG_ZH: "打印机UUID",
        LANG_EN: "Printer UUID"
    },
    # 操作模式 - Operation modes
    'http_only_mode': {
        LANG_ZH: "启动纯HTTP服务器于 {host}:{port}（SSL证书无效）",
        LANG_EN: "Starting HTTP-only server on {host}:{port} (SSL certificate invalid)"
    },
    'http_only_mode_no_ssl': {
        LANG_ZH: "启动纯HTTP服务器于 {host}:{port}（SSL被--no-ssl禁用）",
        LANG_EN: "Starting HTTP-only server on {host}:{port} (SSL disabled by --no-ssl)"
    },
    'dual_mode': {
        LANG_ZH: "启动双模式服务器（HTTP + HTTPS）",
        LANG_EN: "Starting dual mode server (HTTP + HTTPS)"
    },
    # 错误消息 - Error messages
    'unknown_action': {
        LANG_ZH: "未知操作: {action}",
        LANG_EN: "Unknown action: {action}"
    },
    'command_failed': {
        LANG_ZH: "命令执行失败，退出码: {code}",
        LANG_EN: "Command failed with exit code {code}"
    },
    'command_timeout': {
        LANG_ZH: "命令超时",
        LANG_EN: "Command timed out"
    },
    # 参数帮助文本 - Argument help texts
    'arg_verbose_help': {
        LANG_ZH: "添加调试信息",
        LANG_EN: "Add debugging"
    },
    'arg_lang_help': {
        LANG_ZH: "设置语言: zh为中文, en为英文",
        LANG_EN: "Set language: zh for Chinese, en for English"
    },
    'arg_host_help': {
        LANG_ZH: "监听地址 (默认: {default})",
        LANG_EN: "Address to listen on (default: {default})"
    },
    'arg_port_help': {
        LANG_ZH: "HTTP监听端口 (默认: {default})",
        LANG_EN: "HTTP port to listen on (default: {default})"
    },
    'arg_ssl_port_help': {
        LANG_ZH: "HTTPS监听端口 (默认: {default})",
        LANG_EN: "HTTPS port to listen on (default: {default})"
    },
    'arg_no_ssl_help': {
        LANG_ZH: "禁用SSL/TLS支持（强制使用HTTP）",
        LANG_EN: "Disable SSL/TLS support (force HTTP only)"
    },
    'arg_no_mdns_help': {
        LANG_ZH: "禁用mDNS广播",
        LANG_EN: "Disable mDNS broadcasting"
    },
    'arg_uri_help': {
        LANG_ZH: "打印机URI (默认: {default})",
        LANG_EN: "Printer URI (default: {default})"
    },
    'arg_uuid_help': {
        LANG_ZH: "打印机UUID (默认: {default})",
        LANG_EN: "Printer UUID (default: {default})"
    },
    'arg_name_help': {
        LANG_ZH: "打印机名称 (默认: {default})",
        LANG_EN: "Printer name (default: {default})"
    },
    'arg_description_help': {
        LANG_ZH: "打印机描述 (默认: {default})",
        LANG_EN: "Printer description (default: {default})"
    },
    'arg_location_help': {
        LANG_ZH: "打印机位置 (默认: {default})",
        LANG_EN: "Printer location (default: {default})"
    },
    'arg_manufacturer_help': {
        LANG_ZH: "打印机制造商 (默认: {default})",
        LANG_EN: "Printer manufacturer (default: {default})"
    },
    'arg_model_help': {
        LANG_ZH: "打印机型号 (默认: {default})",
        LANG_EN: "Printer model (default: {default})"
    },
    'arg_serial_help': {
        LANG_ZH: "打印机序列号 (默认: {default})",
        LANG_EN: "Printer serial number (default: {default})"
    },
    # 子命令帮助 - Subcommand help
    'save_help': {
        LANG_ZH: "将打印作业保存到磁盘",
        LANG_EN: "Write any print jobs to disk"
    },
    'run_help': {
        LANG_ZH: "接收到打印作业时运行命令",
        LANG_EN: "Run a command when receiving a print job"
    },
    'saveandrun_help': {
        LANG_ZH: "保存打印作业到磁盘然后运行命令",
        LANG_EN: "Write any print jobs to disk and then run a command on them"
    },
    'reject_help': {
        LANG_ZH: "拒绝所有打印作业",
        LANG_EN: "Respond to all print jobs with job-canceled-at-device"
    },
    'pc2paper_help': {
        LANG_ZH: "使用http://www.pc2paper.org/投递打印作业",
        LANG_EN: "Post print jobs using http://www.pc2paper.org/"
    },
    'load_help': {
        LANG_ZH: "加载自定义行为",
        LANG_EN: "Load own behaviour"
    },
    # PC2Paper服务消息 - PC2Paper service messages
    'uploading_pdf': {
        LANG_ZH: "正在上传PDF文档...",
        LANG_EN: "Uploading PDF document..."
    },
    'posting_letter': {
        LANG_ZH: "正在投递信件...",
        LANG_EN: "Posting letter..."
    },
    'upload_response': {
        LANG_ZH: "上传响应: {response}",
        LANG_EN: "Response to uploading: {response}"
    },
    'post_response': {
        LANG_ZH: "投递响应: {response}",
        LANG_EN: "Response to posting: {response}"
    },
    # 状态码描述 - Status code descriptions
    'status_ok': {
        LANG_ZH: "成功 - OK",
        LANG_EN: "OK"
    },
    'status_bad_request': {
        LANG_ZH: "错误请求",
        LANG_EN: "Bad Request"
    },
    'status_not_found': {
        LANG_ZH: "未找到 - Not Found",
        LANG_EN: "Not Found"
    },
    'status_internal_error': {
        LANG_ZH: "内部服务器错误 - Internal Server Error",
        LANG_EN: "Internal Server Error"
    },
    # 子命令参数帮助 - Subcommand argument help
    'directory_help': {
        LANG_ZH: "保存文件的目录",
        LANG_EN: "Directory to save files into"
    },
    'command_help': {
        LANG_ZH: "要运行的命令",
        LANG_EN: "Command to run"
    },
    'command_with_filename_help': {
        LANG_ZH: "要运行的命令（文件名将添加在末尾）",
        LANG_EN: "Command to run (the filename will be added at the end)"
    },
    'env_help': {
        LANG_ZH: "将作业属性存储在环境变量中 (IPP_JOB_ATTRIBUTES)",
        LANG_EN: "Store Job attributes in environment (IPP_JOB_ATTRIBUTES)"
    },
    'config_help': {
        LANG_ZH: "包含发送地址的JSON配置文件",
        LANG_EN: "File containing an address to send to, in json format"
    },
    'path_help': {
        LANG_ZH: "实现行为的模块",
        LANG_EN: "Module implementing behaviour"
    },
    'module_args_help': {
        LANG_ZH: "模块的参数",
        LANG_EN: "Arguments for the module"
    },
    # PPD文件相关 - PPD file related
    'ppd_file_header': {
        LANG_ZH: "*%% PPD配置文件",
        LANG_EN: "*%% PPD Configuration File"
    },
    'ppd_printer_name': {
        LANG_ZH: "*%% 打印机名称",
        LANG_EN: "*%% Printer Name"
    },
    'ppd_windows_id_info': {
        LANG_ZH: "*%% Windows识别信息 - 关键：指定为照片打印机",
        LANG_EN: "*%% Windows Identification Information - Key: Specified as Photo Printer"
    },
    'ppd_color_support': {
        LANG_ZH: "*%% 颜色支持 - 确保声明为彩色设备",
        LANG_EN: "*%% Color Support - Ensure declared as color device"
    },
    'ppd_windows_color_matching': {
        LANG_ZH: "*%% Windows颜色匹配",
        LANG_EN: "*%% Windows Color Matching"
    },
    'ppd_extended_windows_support': {
        LANG_ZH: "*%% 扩展的Windows照片打印支持",
        LANG_EN: "*%% Extended Windows Photo Printing Support"
    },
    'ppd_windows_photo_viewer': {
        LANG_ZH: "*%% Windows照片查看器特定的MIME类型",
        LANG_EN: "*%% Windows Photo Viewer specific MIME types"
    },
    'ppd_windows_photo_print_key': {
        LANG_ZH: "*%% Windows照片打印的关键设置",
        LANG_EN: "*%% Key settings for Windows photo printing"
    },
    'ppd_supported_paper_sizes': {
        LANG_ZH: "*%% 支持的纸张大小 - 扩展列表包含照片尺寸",
        LANG_EN: "*%% Supported paper sizes - Extended list includes photo sizes"
    },
    'ppd_imageable_areas': {
        LANG_ZH: "*%% 图像区域设置",
        LANG_EN: "*%% Imageable Area Settings"
    },
    'ppd_page_size_selection': {
        LANG_ZH: "*%% 页面大小选择",
        LANG_EN: "*%% Page Size Selection"
    },
    'ppd_page_region': {
        LANG_ZH: "*%% 页面区域",
        LANG_EN: "*%% Page Region"
    },
    'ppd_input_slots': {
        LANG_ZH: "*%% 输入槽",
        LANG_EN: "*%% Input Slots"
    },
    'ppd_resolution_settings': {
        LANG_ZH: "*%% 分辨率设置 - 为照片打印优化",
        LANG_EN: "*%% Resolution settings - Optimized for photo printing"
    },
    'ppd_color_model': {
        LANG_ZH: "*%% 颜色模型 - Windows照片打印关键设置",
        LANG_EN: "*%% Color Model - Key settings for Windows photo printing"
    },
    'ppd_print_quality': {
        LANG_ZH: "*%% 打印质量 - 添加照片质量选项",
        LANG_EN: "*%% Print Quality - Added photo quality options"
    },
    'ppd_copies_settings': {
        LANG_ZH: "*%% 副本设置",
        LANG_EN: "*%% Copies Settings"
    },
    'ppd_media_types': {
        LANG_ZH: "*%% 介质类型 - 为照片打印添加选项",
        LANG_EN: "*%% Media Types - Added options for photo printing"
    },
    'ppd_windows_photo_filters': {
        LANG_ZH: "*%% Windows照片打印的关键过滤器",
        LANG_EN: "*%% Key filters for Windows photo printing"
    },
    'ppd_generic_pdf_filters': {
        LANG_ZH: "*%% 通用的PDF过滤器",
        LANG_EN: "*%% Generic PDF filters"
    },
    'ppd_windows_gdi_printing': {
        LANG_ZH: "*%% Windows GDI打印支持",
        LANG_EN: "*%% Windows GDI Printing Support"
    },
    'ppd_duplex_support': {
        LANG_ZH: "*%% 双面打印支持",
        LANG_EN: "*%% Duplex Printing Support"
    },
    'ppd_windows_photo_specific': {
        LANG_ZH: "*%% 照片打印特定的Windows设置",
        LANG_EN: "*%% Windows-specific settings for photo printing"
    },
    'ppd_finishing_options': {
        LANG_ZH: "*%% 完成选项",
        LANG_EN: "*%% Finishing Options"
    },
    'ppd_job_template_support': {
        LANG_ZH: "*%% 作业模板支持",
        LANG_EN: "*%% Job Template Support"
    },
    'ppd_windows_registry_compatibility': {
        LANG_ZH: "*%% Windows注册表兼容性设置",
        LANG_EN: "*%% Windows Registry Compatibility Settings"
    },
    'ppd_output_order': {
        LANG_ZH: "*%% 输出顺序",
        LANG_EN: "*%% Output Order"
    },
    'ppd_paper_handling': {
        LANG_ZH: "*%% 纸张处理",
        LANG_EN: "*%% Paper Handling"
    },
    'ppd_stapling_offset': {
        LANG_ZH: "*%% 装订偏移",
        LANG_EN: "*%% Staple Offset"
    },
    'ppd_installable_options': {
        LANG_ZH: "*%% 可安装选项（无）",
        LANG_EN: "*%% Installable Options (none)"
    },
    'ppd_end_marker': {
        LANG_ZH: "*%% 结束标记",
        LANG_EN: "*%% End Marker"
    },
    # 解析器相关消息 - Parser related messages
    'parser_integer_value_error': {
        LANG_ZH: "整数值必须为4字节，实际获取: {length}字节",
        LANG_EN: "Integer value must be 4 bytes, got: {length} bytes"
    },
    'parser_datetime_value_error': {
        LANG_ZH: "DateTime需要11字节，实际获取: {length}字节",
        LANG_EN: "DateTime requires 11 bytes, got: {length} bytes"
    },
    'parser_resolution_value_error': {
        LANG_ZH: "Resolution需要9字节，实际获取: {length}字节",
        LANG_EN: "Resolution requires 9 bytes, got: {length} bytes"
    },
    'parser_range_of_integer_error': {
        LANG_ZH: "RangeOfInteger需要8字节，实际获取: {length}字节",
        LANG_EN: "RangeOfInteger requires 8 bytes, got: {length} bytes"
    },
    # 请求处理相关消息 - Request handling related messages
    'request_no_section_delimiter': {
        LANG_ZH: "无段分隔符",
        LANG_EN: "No section delimiter"
    },
    'request_additional_attribute_needs_name': {
        LANG_ZH: "附加属性需要名称",
        LANG_EN: "Additional attribute needs a name"
    },
    'request_attributes_key_error': {
        LANG_ZH: "self._attributes[{section}, {name}, {tag}] 是空列表",
        LANG_EN: "self._attributes[{section}, {name}, {tag}] is empty list"
    },
    'request_attributes_multiple_values': {
        LANG_ZH: "self._attributes[{section}, {name}, {tag}] 有多个值",
        LANG_EN: "self._attributes[{section}, {name}, {tag}] has more than one value"
    },
    'request_unsupported_version': {
        LANG_ZH: "不支持的IPP版本: {version_code}",
        LANG_EN: "Unsupported IPP version: {version_code}"
    },
    # 通用调试消息 - General debugging messages
    'debug_chunk_size': {
        LANG_ZH: "块大小: {chunk_size}",
        LANG_EN: "Chunk size: {chunk_size}"
    },
    'debug_chunk_length': {
        LANG_ZH: "块长度: 0x{length:x}",
        LANG_EN: "Chunk length: 0x{length:x}"
    },
    'debug_ssl_handshake_completed': {
        LANG_ZH: "SSL握手完成于 {address}",
        LANG_EN: "SSL handshake completed with {address}"
    },
    'debug_ssl_handshake_failed': {
        LANG_ZH: "SSL握手失败于 {address}: {error}",
        LANG_EN: "SSL handshake failed with {address}: {error}"
    },
    'debug_ssl_handshake_timeout': {
        LANG_ZH: "SSL握手超时于 {address}",
        LANG_EN: "SSL handshake timeout with {address}"
    },
    'debug_http_headers': {
        LANG_ZH: "HTTP头信息",
        LANG_EN: "HTTP Headers"
    },
    # mDNS相关翻译 - mDNS related translations
    'mdns_initialized': {
        LANG_ZH: "mDNS已初始化: {hostname}.local ({local_ip})",
        LANG_EN: "mDNS initialized: {hostname}.local ({local_ip})"
    },
    'display_name': {
        LANG_ZH: "显示名称: {display_name}",
        LANG_EN: "Display name: {display_name}"
    },
    'mdns_socket_creation_failed': {
        LANG_ZH: "创建IPv{ip_version} mDNS socket失败: {error}",
        LANG_EN: "Failed to create IPv{ip_version} mDNS socket: {error}"
    },
    'failed_to_broadcast_service': {
        LANG_ZH: "广播{service_type}失败: {error}",
        LANG_EN: "Failed to broadcast {service_type}: {error}"
    },
    'https_available_status': {
        LANG_ZH: "HTTPS{status}，mDNS将广播{type}服务",
        LANG_EN: "HTTPS is {status}, mDNS will advertise {type} services"
    },
    'mdns_already_running': {
        LANG_ZH: "mDNS广播器已在运行",
        LANG_EN: "mDNS broadcaster is already running"
    },
    'mdns_ipv6_unavailable': {
        LANG_ZH: "IPv6 mDNS不可用",
        LANG_EN: "IPv6 mDNS not available"
    },
    'mdns_no_sockets': {
        LANG_ZH: "未能创建任何mDNS socket",
        LANG_EN: "Failed to create any mDNS socket"
    },
    'initial_advertisements': {
        LANG_ZH: "正在发送初始mDNS广播...",
        LANG_EN: "Sending initial mDNS advertisements..."
    },
    'initial_advertisements_sent': {
        LANG_ZH: "初始mDNS广播已发送",
        LANG_EN: "Initial mDNS advertisements sent"
    },
    'broadcast_cycle_error': {
        LANG_ZH: "mDNS广播周期错误: {error}",
        LANG_EN: "Error in mDNS broadcast cycle: {error}"
    },
    'broadcast_loop_terminated': {
        LANG_ZH: "mDNS广播循环终止: {error}",
        LANG_EN: "mDNS broadcast loop terminated: {error}"
    },
    'mdns_stopping': {
        LANG_ZH: "正在停止mDNS广播器...",
        LANG_EN: "Stopping mDNS broadcaster..."
    },
    'mdns_stopped': {
        LANG_ZH: "mDNS广播器已停止",
        LANG_EN: "mDNS broadcaster stopped"
    },
    'failed_to_start_mdns': {
        LANG_ZH: "启动mDNS广播器失败: {error}",
        LANG_EN: "Failed to start mDNS broadcaster: {error}"
    },
    'mdns_service_started': {
        LANG_ZH: "mDNS广播服务已启动",
        LANG_EN: "mDNS Broadcast Service Started"
    },
    'printer_display_name': {
        LANG_ZH: "打印机显示名称: {display_name}",
        LANG_EN: "Printer Display Name: {display_name}"
    },
    'hostname_info': {
        LANG_ZH: "主机名: {hostname}.local",
        LANG_EN: "Hostname: {hostname}.local"
    },
    'ip_address': {
        LANG_ZH: "IP地址: {local_ip}",
        LANG_EN: "IP Address: {local_ip}"
    },
    'http_port_info': {
        LANG_ZH: "HTTP端口: {port}",
        LANG_EN: "HTTP Port: {port}"
    },
    'https_port_info': {
        LANG_ZH: "HTTPS端口: {port} ({status})",
        LANG_EN: "HTTPS Port: {port} ({status})"
    },
    'primary_url': {
        LANG_ZH: "主URL: {url}",
        LANG_EN: "Primary URL: {url}"
    },
    'http_redirect_note': {
        LANG_ZH: "HTTP请求将重定向到HTTPS",
        LANG_EN: "HTTP requests will be redirected to HTTPS"
    },
    'serving_over_http': {
        LANG_ZH: "仅通过HTTP提供服务",
        LANG_EN: "Serving requests over HTTP only"
    },
    'hardware_information': {
        LANG_ZH: "硬件信息:",
        LANG_EN: "Hardware Information:"
    },
    'manufacturer_label': {
        LANG_ZH: "制造商: {manufacturer}",
        LANG_EN: "Manufacturer: {manufacturer}"
    },
    'model_label': {
        LANG_ZH: "型号: {model}",
        LANG_EN: "Model: {model}"
    },
    'serial_label': {
        LANG_ZH: "序列号: {serial}",
        LANG_EN: "Serial Number: {serial}"
    },
    'uuid_label': {
        LANG_ZH: "UUID: {uuid}",
        LANG_EN: "UUID: {uuid}"
    },
    'color_support_info': {
        LANG_ZH: "颜色支持: 全彩色(CMYK)带照片打印",
        LANG_EN: "Color Support: Full Color (CMYK) with Photo Printing"
    },
    'paper_sizes_info': {
        LANG_ZH: "纸张大小: A0-A10, B0-B10, Letter, Legal, Tabloid, Ledger, Executive, 照片尺寸",
        LANG_EN: "Paper Sizes: A0-A10, B0-B10, Letter, Legal, Tabloid, Ledger, Executive, Photo sizes"
    },
    'resolutions_info': {
        LANG_ZH: "分辨率: 72-4800 DPI (照片: 1200-2400 DPI)",
        LANG_EN: "Resolutions: 72-4800 DPI (Photo: 1200-2400 DPI)"
    },
    'windows_photo_printing': {
        LANG_ZH: "Windows照片打印: 已启用",
        LANG_EN: "Windows Photo Printing: ENABLED"
    },
    'services_advertised': {
        LANG_ZH: "已广播的服务:",
        LANG_EN: "Services advertised:"
    },
    'service_instance': {
        LANG_ZH: "服务实例: {instance}",
        LANG_EN: "Service Instance: {instance}"
    },
        # PDF转换器相关消息 - PDF Converter related messages
    'pdf_converter_no_data': {
        LANG_ZH: "没有数据可转换 - No data to convert",
        LANG_EN: "No data to convert"
    },
    'pdf_converter_converting_format': {
        LANG_ZH: "正在转换 {format} 到PDF - Converting {format} to PDF",
        LANG_EN: "Converting {format} to PDF"
    },
    'pdf_converter_already_pdf': {
        LANG_ZH: "数据已经是PDF格式，直接返回 - Data is already in PDF format, returning directly",
        LANG_EN: "Data is already in PDF format, returning directly"
    },
    'pdf_converter_converting_postscript': {
        LANG_ZH: "正在转换PostScript到PDF - Converting PostScript to PDF",
        LANG_EN: "Converting PostScript to PDF"
    },
    'pdf_converter_converting_image': {
        LANG_ZH: "正在转换图像 {format} 到PDF - Converting image {format} to PDF",
        LANG_EN: "Converting image {format} to PDF"
    },
    'pdf_converter_converting_text': {
        LANG_ZH: "正在转换文本到PDF - Converting text to PDF",
        LANG_EN: "Converting text to PDF"
    },
    'pdf_converter_unknown_format': {
        LANG_ZH: "未知格式 {format}，尝试使用通用方法转换 - Unknown format {format}, trying generic conversion",
        LANG_EN: "Unknown format {format}, trying generic conversion"
    },
    'pdf_converter_conversion_error': {
        LANG_ZH: "转换 {format} 到PDF时出错: {error} - Error converting {format} to PDF: {error}",
        LANG_EN: "Error converting {format} to PDF: {error}"
    },
    'pdf_converter_returning_original': {
        LANG_ZH: "转换失败，返回原始数据 - Conversion failed, returning original data",
        LANG_EN: "Conversion failed, returning original data"
    },
    'pdf_converter_detected_gzip': {
        LANG_ZH: "检测到GZIP压缩数据 - Detected GZIP compressed data",
        LANG_EN: "Detected GZIP compressed data"
    },
    'pdf_converter_detected_zip': {
        LANG_ZH: "检测到ZIP压缩数据 - Detected ZIP compressed data",
        LANG_EN: "Detected ZIP compressed data"
    },
    'pdf_converter_zip_file_empty': {
        LANG_ZH: "ZIP文件为空 - ZIP file is empty",
        LANG_EN: "ZIP file is empty"
    },
    'pdf_converter_unsupported_compression': {
        LANG_ZH: "不支持的压缩类型: {type} - Unsupported compression type: {type}",
        LANG_EN: "Unsupported compression type: {type}"
    },
    'pdf_converter_trying_ghostscript': {
        LANG_ZH: "尝试使用Ghostscript转换 - Trying Ghostscript conversion",
        LANG_EN: "Trying Ghostscript conversion"
    },
    'pdf_converter_ghostscript_failed': {
        LANG_ZH: "Ghostscript转换失败: {error} - Ghostscript conversion failed: {error}",
        LANG_EN: "Ghostscript conversion failed: {error}"
    },
    'pdf_converter_trying_imagemagick': {
        LANG_ZH: "尝试使用ImageMagick转换 - Trying ImageMagick conversion",
        LANG_EN: "Trying ImageMagick conversion"
    },
    'pdf_converter_imagemagick_failed': {
        LANG_ZH: "ImageMagick转换失败: {error} - ImageMagick conversion failed: {error}",
        LANG_EN: "ImageMagick conversion failed: {error}"
    },
    'pdf_converter_trying_pypdf': {
        LANG_ZH: "尝试使用PyPDF转换 - Trying PyPDF conversion",
        LANG_EN: "Trying PyPDF conversion"
    },
    'pdf_converter_pypdf_failed': {
        LANG_ZH: "PyPDF转换失败: {error} - PyPDF conversion failed: {error}",
        LANG_EN: "PyPDF conversion failed: {error}"
    },
    'pdf_converter_all_methods_failed': {
        LANG_ZH: "所有转换方法都失败，返回原始数据 - All conversion methods failed, returning original data",
        LANG_EN: "All conversion methods failed, returning original data"
    },
    'pdf_converter_using_ghostscript': {
        LANG_ZH: "使用Ghostscript转换，命令: {command} - Using Ghostscript for conversion, command: {command}",
        LANG_EN: "Using Ghostscript for conversion, command: {command}"
    },
    'pdf_converter_running_command': {
        LANG_ZH: "运行命令: {command} - Running command: {command}",
        LANG_EN: "Running command: {command}"
    },
    'pdf_converter_ghostscript_error': {
        LANG_ZH: "Ghostscript错误: {error} - Ghostscript error: {error}",
        LANG_EN: "Ghostscript error: {error}"
    },
    'pdf_converter_conversion_successful': {
        LANG_ZH: "转换成功，生成 {bytes} 字节PDF数据 - Conversion successful, generated {bytes} bytes of PDF data",
        LANG_EN: "Conversion successful, generated {bytes} bytes of PDF data"
    },
    'pdf_converter_using_imagemagick': {
        LANG_ZH: "使用ImageMagick转换 - Using ImageMagick for conversion",
        LANG_EN: "Using ImageMagick for conversion"
    },
    'pdf_converter_imagemagick_error': {
        LANG_ZH: "ImageMagick错误: {error} - ImageMagick error: {error}",
        LANG_EN: "ImageMagick error: {error}"
    },
    'pdf_converter_using_pypdf': {
        LANG_ZH: "使用PyPDF转换（纯Python）- Using PyPDF conversion (pure Python)",
        LANG_EN: "Using PyPDF conversion (pure Python)"
    },
    'pdf_converter_no_pdf_library': {
        LANG_ZH: "未找到PDF库 - No PDF library found",
        LANG_EN: "No PDF library found"
    },
    'pdf_converter_install_pypdf': {
        LANG_ZH: "未找到PDF库。请安装: pip install pypdf - No PDF library found. Install with: pip install pypdf",
        LANG_EN: "No PDF library found. Install with: pip install pypdf"
    },
    'pdf_converter_reportlab_unavailable': {
        LANG_ZH: "reportlab不可用 - reportlab not available",
        LANG_EN: "reportlab not available"
    },
    'pdf_converter_pypdf_error': {
        LANG_ZH: "PyPDF转换错误: {error} - PyPDF conversion error: {error}",
        LANG_EN: "PyPDF conversion error: {error}"
    },
    'pdf_converter_pypdf_success': {
        LANG_ZH: "PyPDF转换成功，生成 {bytes} 字节PDF数据 - PyPDF conversion successful, generated {bytes} bytes of PDF data",
        LANG_EN: "PyPDF conversion successful, generated {bytes} bytes of PDF data"
    },
    'pdf_converter_image_to_pdf': {
        LANG_ZH: "将图像 {format} 转换为PDF - Converting image {format} to PDF",
        LANG_EN: "Converting image {format} to PDF"
    },
    'pdf_converter_image_loaded': {
        LANG_ZH: "图像已加载，尺寸: {size}，模式: {mode} - Image loaded, size: {size}, mode: {mode}",
        LANG_EN: "Image loaded, size: {size}, mode: {mode}"
    },
    'pdf_converter_image_converted_rgb': {
        LANG_ZH: "图像已转换为RGB模式 - Image converted to RGB mode",
        LANG_EN: "Image converted to RGB mode"
    },
    'pdf_converter_image_conversion_success': {
        LANG_ZH: "图像转换成功，生成 {bytes} 字节PDF数据 - Image conversion successful, generated {bytes} bytes of PDF data",
        LANG_EN: "Image conversion successful, generated {bytes} bytes of PDF data"
    },
    'pdf_converter_pillow_unavailable': {
        LANG_ZH: "PIL/Pillow不可用，尝试其他方法 - PIL/Pillow not available, trying alternative methods",
        LANG_EN: "PIL/Pillow not available, trying alternative methods"
    },
    'pdf_converter_fallback_imagemagick': {
        LANG_ZH: "回退到使用ImageMagick转换 - Fallback to ImageMagick conversion",
        LANG_EN: "Fallback to ImageMagick conversion"
    },
    'pdf_converter_fallback_failed': {
        LANG_ZH: "备用转换方法失败: {error} - Fallback conversion method failed: {error}",
        LANG_EN: "Fallback conversion method failed: {error}"
    },
    'pdf_converter_creating_minimal_pdf': {
        LANG_ZH: "创建最简单的PDF文档 - Creating simplest PDF document",
        LANG_EN: "Creating simplest PDF document"
    },
    'pdf_converter_text_to_pdf': {
        LANG_ZH: "将文本转换为PDF - Converting text to PDF",
        LANG_EN: "Converting text to PDF"
    },
    'pdf_converter_text_decoded': {
        LANG_ZH: "文本已解码，长度: {length} 字符，行数: {lines} - Text decoded, length: {length} characters, lines: {lines}",
        LANG_EN: "Text decoded, length: {length} characters, lines: {lines}"
    },
    'pdf_converter_text_conversion_success': {
        LANG_ZH: "文本转换成功，生成 {bytes} 字节PDF数据 - Text conversion successful, generated {bytes} bytes of PDF data",
        LANG_EN: "Text conversion successful, generated {bytes} bytes of PDF data"
    },
    'pdf_converter_text_conversion_failed': {
        LANG_ZH: "文本到PDF转换失败: {error} - Text to PDF conversion failed: {error}",
        LANG_EN: "Text to PDF conversion failed: {error}"
    },
    'pdf_converter_generic_conversion': {
        LANG_ZH: "通用转换方法，格式: {format} - Generic conversion method, format: {format}",
        LANG_EN: "Generic conversion method, format: {format}"
    },
    'pdf_converter_trying_unoconv': {
        LANG_ZH: "尝试使用unoconv转换 - Trying unoconv conversion",
        LANG_EN: "Trying unoconv conversion"
    },
    'pdf_converter_generic_failed': {
        LANG_ZH: "通用转换失败: {error} - Generic conversion failed: {error}",
        LANG_EN: "Generic conversion failed: {error}"
    },
    'pdf_converter_creating_embedded_pdf': {
        LANG_ZH: "创建包含原始数据的PDF - Creating PDF with embedded original data",
        LANG_EN: "Creating PDF with embedded original data"
    },
    'pdf_converter_using_unoconv': {
        LANG_ZH: "使用unoconv转换，格式: {format} - Using unoconv conversion, format: {format}",
        LANG_EN: "Using unoconv conversion, format: {format}"
    },
    'pdf_converter_determined_extension': {
        LANG_ZH: "确定文件扩展名: {ext} - Determined file extension: {ext}",
        LANG_EN: "Determined file extension: {ext}"
    },
    'pdf_converter_unoconv_error': {
        LANG_ZH: "Unoconv错误: {error} - Unoconv error: {error}",
        LANG_EN: "Unoconv error: {error}"
    },
    'pdf_converter_unoconv_success': {
        LANG_ZH: "Unoconv转换成功，生成 {bytes} 字节PDF数据 - Unoconv conversion successful, generated {bytes} bytes of PDF data",
        LANG_EN: "Unoconv conversion successful, generated {bytes} bytes of PDF data"
    },
    'pdf_converter_creating_embedded_pdf_detail': {
        LANG_ZH: "创建包含原始数据的PDF，格式: {format}，大小: {size} 字节 - Creating PDF with embedded original data, format: {format}, size: {size} bytes",
        LANG_EN: "Creating PDF with embedded original data, format: {format}, size: {size} bytes"
    },
    'pdf_converter_embedded_title': {
        LANG_ZH: "原始文件: {format} - Original File: {format}",
        LANG_EN: "Original File: {format}"
    },
    'pdf_converter_embedded_size': {
        LANG_ZH: "大小: {size} 字节 - Size: {size} bytes",
        LANG_EN: "Size: {size} bytes"
    },
    'pdf_converter_embedded_cannot_convert': {
        LANG_ZH: "内容无法转换为PDF - Content could not be converted to PDF",
        LANG_EN: "Content could not be converted to PDF"
    },
    'pdf_converter_embedded_data_preserved': {
        LANG_ZH: "原始数据已保存但未显示 - Original data is preserved but not displayed",
        LANG_EN: "Original data is preserved but not displayed"
    },
    'pdf_converter_embedded_pdf_created': {
        LANG_ZH: "包含原始数据的PDF已创建，大小: {bytes} 字节 - PDF with embedded data created, size: {bytes} bytes",
        LANG_EN: "PDF with embedded data created, size: {bytes} bytes"
    },
    # 服务器启动消息 - Server startup messages
    'listening_on': {
        LANG_ZH: "监听地址: {address}",
        LANG_EN: "Listening on {address}"
    },
    'http_server_started_detail': {
        LANG_ZH: "HTTP服务器已启动 - HTTP server started",
        LANG_EN: "HTTP server started"
    },
    'https_server_started_detail': {
        LANG_ZH: "HTTPS服务器已启动 - HTTPS server started",
        LANG_EN: "HTTPS server started"
    },
    'ssl_context_created': {
        LANG_ZH: "SSL/TLS上下文创建成功 - SSL/TLS context created successfully",
        LANG_EN: "SSL/TLS context created successfully"
    },
    'ssl_certificates_loaded': {
        LANG_ZH: "SSL证书已加载 - SSL certificates loaded",
        LANG_EN: "SSL certificates loaded"
    },
    'ssl_tls_enabled': {
        LANG_ZH: "SSL/TLS已启用 - SSL/TLS enabled",
    LANG_EN: "SSL/TLS enabled"
    },
    'ssl_tls_failed': {
        LANG_ZH: "SSL/TLS启用失败 - SSL/TLS enabling failed",
        LANG_EN: "SSL/TLS enabling failed"
    },
    'ssl_disabled_fallback': {
        LANG_ZH: "SSL已禁用，回退到HTTP - SSL disabled, falling back to HTTP",
        LANG_EN: "SSL disabled, falling back to HTTP"
    },
    'ssl_handshake_completed': {
        LANG_ZH: "SSL握手完成 - SSL handshake completed",
        LANG_EN: "SSL handshake completed"
    },
    'ssl_handshake_failed': {
        LANG_ZH: "SSL握手失败 - SSL handshake failed",
        LANG_EN: "SSL handshake failed"
    },
    'ssl_handshake_timeout': {
        LANG_ZH: "SSL握手超时 - SSL handshake timeout",
        LANG_EN: "SSL handshake timeout"
    },
    # 服务器关闭消息 - Server shutdown messages
    'shutting_down_servers': {
        LANG_ZH: "正在关闭服务器... - Shutting down servers...",
        LANG_EN: "Shutting down servers..."
    },
    'http_server_stopped': {
        LANG_ZH: "HTTP服务器已停止 - HTTP server stopped",
        LANG_EN: "HTTP server stopped"
    },
    'https_server_stopped': {
        LANG_ZH: "HTTPS服务器已停止 - HTTPS server stopped",
        LANG_EN: "HTTPS server stopped"
    },
    'ready_to_shut_down': {
        LANG_ZH: "准备关闭服务器 - Ready to shut down",
        LANG_EN: "Ready to shut down"
    },
    # 错误消息 - Error messages
    'unhandled_error_in_request': {
        LANG_ZH: "请求中的未处理错误: {error}",
        LANG_EN: "Unhandled error in request: {error}"
    },
    'connection_error': {
        LANG_ZH: "连接错误 - Connection error",
        LANG_EN: "Connection error"
    },
    # 请求处理消息 - Request handling messages
    'error_parsing_request': {
        LANG_ZH: "解析请求时出错: {error}",
        LANG_EN: "Error parsing request: {error}"
    },
    'error_handling_ipp_request': {
        LANG_ZH: "处理IPP请求时出错: {error}",
        LANG_EN: "Error handling IPP request: {error}"
    },
    'error_handling_http_request': {
        LANG_ZH: "处理HTTP请求时出错: {error}",
        LANG_EN: "Error handling HTTP request: {error}"
    },
    'error_processing_ipp_request': {
        LANG_ZH: "处理IPP请求时出错: {error}",
        LANG_EN: "Error processing IPP request: {error}"
    },
    'error_processing_http_request': {
        LANG_ZH: "处理HTTP请求时出错: {error}",
        LANG_EN: "Error processing HTTP request: {error}"
    },
    # 证书处理消息 - Certificate handling messages
    'certificate_validation_passed': {
        LANG_ZH: "✓ SSL证书验证通过 - SSL certificate validation passed",
        LANG_EN: "✓ SSL certificate validation passed"
    },
    'certificate_validation_failed': {
        LANG_ZH: "✗ SSL证书验证失败 - SSL certificate validation failed",
        LANG_EN: "✗ SSL certificate validation failed"
    },
    'certificate_validation_error': {
        LANG_ZH: "证书验证错误 - Certificate validation error",
        LANG_EN: "Certificate validation error"
    },
    'error_checking_ssl_certificate': {
        LANG_ZH: "检查SSL证书时出错 - Error checking SSL certificate",
        LANG_EN: "Error checking SSL certificate"
    },
    'ssl_certificate_missing': {
        LANG_ZH: "SSL证书或私钥缺失 - SSL certificate or private key is missing",
        LANG_EN: "SSL certificate or private key is missing"
    },
    'certificate_loading_failed': {
        LANG_ZH: "证书加载失败 - Certificate loading failed",
        LANG_EN: "Certificate loading failed"
    },
    'ssl_error_loading_certificates': {
        LANG_ZH: "加载SSL证书时出错 - SSL error loading certificates",
        LANG_EN: "SSL error loading certificates"
    },
    'failed_to_create_certificate_files': {
        LANG_ZH: "创建证书文件失败 - Failed to create certificate files",
        LANG_EN: "Failed to create certificate files"
    },
    # 双模式服务器消息 - Dual mode server messages
    'dual_server_starting_https': {
        LANG_ZH: "尝试启动HTTPS服务器... - Attempting to start HTTPS server...",
        LANG_EN: "Attempting to start HTTPS server..."
    },
    'dual_server_https_failed': {
        LANG_ZH: "HTTPS服务器启动失败 - HTTPS server creation failed",
        LANG_EN: "HTTPS server creation failed"
    },
    'dual_server_http_started': {
        LANG_ZH: "✓ HTTP服务器已启动于 http://{host}:{port}",
        LANG_EN: "✓ HTTP server started on http://{host}:{port}"
    },
    'dual_server_https_started': {
        LANG_ZH: "✓ HTTPS服务器已启动于 https://{host}:{port}",
        LANG_EN: "✓ HTTPS server started on https://{host}:{port}"
    },
    'use_https_for_secure_printing': {
        LANG_ZH: "   使用HTTPS进行安全打印: https://{host}:{port}",
        LANG_EN: "   Use HTTPS for secure printing: https://{host}:{port}"
    },
    'https_unavailable_http_only': {
        LANG_ZH: "   HTTPS不可用，仅提供HTTP服务 - HTTPS unavailable, serving requests over HTTP only",
        LANG_EN: "   HTTPS unavailable, serving requests over HTTP only"
    },
    # 调试消息 - Debug messages
    'chunk_size_debug': {
        LANG_ZH: "块大小调试 - chunksz={chunk_size}",
        LANG_EN: "chunksz={chunk_size}"
    },
    'chunk_length_debug': {
        LANG_ZH: "块长度调试 - chunk=0x{length:x}",
        LANG_EN: "chunk=0x{length:x}"
    },
    'ssl_connection_established': {
        LANG_ZH: "SSL连接已建立 - SSL connection established",
        LANG_EN: "SSL connection established"
    },
    'ssl_setup_error': {
        LANG_ZH: "SSL设置时出错: {error}",
        LANG_EN: "Error during SSL setup: {error}"
    },
    'http_headers_debug': {
        LANG_ZH: "HTTP头信息 - HTTP Headers",
        LANG_EN: "HTTP Headers"
    },
    'http_header_item': {
        LANG_ZH: "  {header}: {value}",
        LANG_EN: "  {header}: {value}"
    },
    # 压缩相关 - Compression related
    'decompressing_gzip': {
        LANG_ZH: "正在解压缩gzip数据",
        LANG_EN: "Decompressing gzip data"
    },
    'decompressing_deflate': {
        LANG_ZH: "正在解压缩deflate数据",
        LANG_EN: "Decompressing deflate data"
    },
    'decompressing_zip': {
        LANG_ZH: "正在解压缩zip数据",
        LANG_EN: "Decompressing zip data"
    },
    'zip_file_empty': {
        LANG_ZH: "ZIP文件为空",
        LANG_EN: "ZIP file is empty"
    },
    'no_compression_applied': {
        LANG_ZH: "未应用压缩",
        LANG_EN: "No compression applied"
    },
    'unsupported_compression_type': {
        LANG_ZH: "不支持的压缩类型: {type}",
        LANG_EN: "Unsupported compression type: {type}"
    },
    'error_decompressing_data': {
        LANG_ZH: "解压缩{type}数据时出错: {error}",
        LANG_EN: "Error decompressing {type} data: {error}"
    },
    # IPP操作相关 - IPP operation related
    'operation_not_supported': {
        LANG_ZH: "不支持的操作 {code}",
        LANG_EN: "Operation not supported {code}"
    },
    'error_validating_job': {
        LANG_ZH: "验证作业时出错: {error}",
        LANG_EN: "Error validating job: {error}"
    },
    'error_getting_jobs': {
        LANG_ZH: "获取作业时出错: {error}",
        LANG_EN: "Error getting jobs: {error}"
    },
    'request_specifies_compression': {
        LANG_ZH: "请求指定压缩: {type}",
        LANG_EN: "Request specifies compression: {type}"
    },
    'image_document_detected': {
        LANG_ZH: "检测到图像文档: {format}",
        LANG_EN: "Image document detected: {format}"
    },
    'original_color_mode': {
        LANG_ZH: "原始颜色模式: {mode}",
        LANG_EN: "Original color mode: {mode}"
    },
    'forcing_color_mode_for_image': {
        LANG_ZH: "为图像文档强制使用彩色模式 (Windows照片打印要求)",
        LANG_EN: "Forcing color mode for image document (Windows Photo Printing requirement)"
    },
    'setting_color_mode_to_color_for_image': {
        LANG_ZH: "为自动模式下的图像文档设置颜色模式为'color'",
        LANG_EN: "Setting color mode to 'color' for image document in auto mode"
    },
    'image_document_using_color_mode': {
        LANG_ZH: "图像文档使用颜色模式: {mode}",
        LANG_EN: "Image document using color mode: {mode}"
    },
    'setting_print_quality_to_high_for_image': {
        LANG_ZH: "为图像文档设置打印质量为'high'",
        LANG_EN: "Setting print quality to 'high' for image document"
    },
    'raw_data_received': {
        LANG_ZH: "接收到原始数据: {size} 字节",
        LANG_EN: "Raw data received: {size} bytes"
    },
    'decompression_complete': {
        LANG_ZH: "解压缩完成: {original} 字节 -> {final} 字节 (压缩: {type})",
        LANG_EN: "Decompressed {original} bytes to {final} bytes (compression: {type})"
    },
    'failed_to_decompress_data': {
        LANG_ZH: "解压缩数据失败 ({type}): {error}",
        LANG_EN: "Failed to decompress data ({type}): {error}"
    },
    'document_format_info': {
        LANG_ZH: "文档格式: {format}, 是否为图像: {is_image}, 最终颜色模式: {color_mode}",
        LANG_EN: "Document format: {format}, Is image: {is_image}, Final color mode: {color_mode}"
    },
    'error_reading_document_data': {
        LANG_ZH: "读取文档数据时出错: {error}",
        LANG_EN: "Error reading document data: {error}"
    },
    'error_creating_print_job': {
        LANG_ZH: "创建打印作业时出错: {error}",
        LANG_EN: "Error creating print job: {error}"
    },
    'error_getting_job_attributes': {
        LANG_ZH: "获取作业属性时出错: {error}",
        LANG_EN: "Error getting job attributes: {error}"
    },
    'error_canceling_job': {
        LANG_ZH: "取消作业时出错: {error}",
        LANG_EN: "Error canceling job: {error}"
    },
    'misidentified_as_http': {
        LANG_ZH: "此操作的操作ID为\\r\\n，表明该请求实际上是一个HTTP请求",
        LANG_EN: "The opid for this operation is \\r\\n, which suggests the request was actually a http request."
    },
    # 状态转换 - State transitions
    'invalid_state_transition': {
        LANG_ZH: "无效的状态转换: 从 {old} 到 {new}",
        LANG_EN: "Invalid state transition from {old} to {new}"
    },
    # 作业状态消息 - Job state messages
    'job_state_pending': {
        LANG_ZH: "作业挂起中",
        LANG_EN: "Job is pending"
    },
    'job_state_pending_held': {
        LANG_ZH: "作业挂起保持",
        LANG_EN: "Job is held pending"
    },
    'job_state_processing': {
        LANG_ZH: "作业处理中",
        LANG_EN: "Job is processing"
    },
    'job_state_processing_stopped': {
        LANG_ZH: "作业处理停止",
        LANG_EN: "Job processing stopped"
    },
    'job_state_canceled': {
        LANG_ZH: "作业已取消",
        LANG_EN: "Job was canceled"
    },
    'job_state_aborted': {
        LANG_ZH: "作业已中止",
        LANG_EN: "Job was aborted"
    },
    'job_state_completed': {
        LANG_ZH: "作业成功完成",
        LANG_EN: "Job completed successfully"
    },
    'job_state_unknown': {
        LANG_ZH: "未知作业状态",
        LANG_EN: "Unknown job state"
    },
    # 作业处理 - Job processing
    'starting_to_process_job': {
        LANG_ZH: "开始处理作业 {job_id}",
        LANG_EN: "Starting to process job {job_id}"
    },
    'print_job_parameters': {
        LANG_ZH: "作业 {job_id} 的打印参数:",
        LANG_EN: "Print job parameters for job {job_id}:"
    },
    'document_format_info_short': {
        LANG_ZH: "  文档格式: {format}, 是否为图像: {is_image}",
        LANG_EN: "  Document format: {format}, Is image: {is_image}"
    },
    'job_parameter': {
        LANG_ZH: "  {key}: {value}",
        LANG_EN: "  {key}: {value}"
    },
    'job_completed_successfully': {
        LANG_ZH: "作业 {job_id} 成功完成",
        LANG_EN: "Job {job_id} completed successfully"
    },
    'error_processing_job': {
        LANG_ZH: "处理作业 {job_id} 时出错: {error}",
        LANG_EN: "Error processing job {job_id}: {error}"
    },
    'pdf_handler_not_implemented': {
        LANG_ZH: "PDF处理器必须在子类中实现",
        LANG_EN: "PDF handler must be implemented in subclass"
    },
    # 文件保存和命令执行 - File saving and command execution
    'saving_print_job_as': {
        LANG_ZH: "正在将打印作业保存为 '{filename}'",
        LANG_EN: "Saving print job as '{filename}'"
    },
    'successfully_saved_job': {
        LANG_ZH: "成功将作业保存到 {filename} ({size} 字节)",
        LANG_EN: "Successfully saved job to {filename} ({size} bytes)"
    },
    'no_pdf_data_to_save': {
        LANG_ZH: "没有要保存的PDF数据",
        LANG_EN: "No PDF data to save"
    },
    'error_saving_pdf_file': {
        LANG_ZH: "保存PDF文件时出错: {error}",
        LANG_EN: "Error saving PDF file: {error}"
    },
    'default_print_job_name': {
        LANG_ZH: "打印作业",
        LANG_EN: "Print job"
    },
    'running_command': {
        LANG_ZH: "正在运行命令: {command}",
        LANG_EN: "Running command: {command}"
    },
    'command_exited_with_code': {
        LANG_ZH: "命令 {command} 以代码 {code} 退出\nstdout: {stdout}\nstderr: {stderr}",
        LANG_EN: "The command {command} exited with code {code}\nstdout: {stdout}\nstderr: {stderr}"
    },
    'command_failed_with_exit_code': {
        LANG_ZH: "命令执行失败，退出码: {code}",
        LANG_EN: "Command failed with exit code {code}"
    },
    'command_executed_successfully': {
        LANG_ZH: "命令执行成功: {output}",
        LANG_EN: "Command executed successfully: {output}"
    },
    'command_timed_out': {
        LANG_ZH: "命令超时",
        LANG_EN: "Command timed out"
    },
    'error_running_command': {
        LANG_ZH: "运行命令 {command} 时出错: {error}",
        LANG_EN: "Error running command {command}: {error}"
    },
    'running_command_for_job_with_pdf': {
        LANG_ZH: "正在为带有PDF数据的作业运行命令",
        LANG_EN: "Running command for job with PDF data"
    },
    'no_pdf_data_to_process': {
        LANG_ZH: "没有要处理的PDF数据",
        LANG_EN: "No PDF data to process"
    },
    'posted_pdf_document_to_service': {
        LANG_ZH: "已将PDF文档 {filename} ({size} 字节) 发布到服务",
        LANG_EN: "Posted PDF document {filename} ({size} bytes) to service"
    },
    'no_pdf_data_to_post': {
        LANG_ZH: "没有要发布到服务的PDF数据",
        LANG_EN: "No PDF data to post to service"
    },
}


def set_language(lang_code):
    """设置当前语言 - Set current language"""
    global CURRENT_LANG
    if lang_code in [LANG_ZH, LANG_EN]:
        CURRENT_LANG = lang_code
    else:
        print(f"不支持的语言代码: {lang_code} - 使用默认中文 - Unsupported language code: {lang_code} - Using default Chinese")


def t(key, **kwargs):
    """获取翻译文本 - Get translated text"""
    if key in TRANSLATIONS and CURRENT_LANG in TRANSLATIONS[key]:
        text = TRANSLATIONS[key][CURRENT_LANG]
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError as e:
                print(f"翻译格式化错误: {e} - 键: {key} - Translation formatting error: {e} - Key: {key}")
        return text
    else:
        return key  # 返回键本身如果没有翻译 - Return key itself if no translation


def get_all_translations(key):
    """获取所有语言的翻译 - Get translations in all languages"""
    if key in TRANSLATIONS:
        return TRANSLATIONS[key]
    return {LANG_ZH: key, LANG_EN: key}


# 语言特定的格式化函数 - Language-specific formatting functions
def format_help(help_key, **kwargs):
    """格式化帮助文本 - Format help text"""
    return t(help_key, **kwargs)