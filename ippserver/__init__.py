# This is the ippserver package
# 这是 ippserver 包 - This is the ippserver package
__version__ = "1.0.0"

# ============================================================================
# 打印机配置常量
# ============================================================================
# Printer Configuration Constants
# ============================================================================

# 打印机基本信息
# Printer Basic Information
DEFAULT_PRINTER_NAME = "Virtual Photo Printer"                    # 打印机名称 - Printer name
DEFAULT_PRINTER_DESCRIPTION = "IPP Virtual Photo Printer - Full Color Support"  # 打印机描述 - Printer description
DEFAULT_PRINTER_LOCATION = "Local Network"                        # 打印机位置 - Printer location

# 打印机URI和标识
# Printer URI and Identification
DEFAULT_PRINTER_URI = "ipps://localhost:443/"                     # 打印机URI（优先使用HTTPS）- Printer URI (prefer HTTPS)
DEFAULT_PRINTER_UUID = "884d7c0a-f449-45a7-8bbe-095e2943d315"     # 打印机唯一标识符 - Printer unique identifier

# Windows显示名称（在Windows添加打印机时显示的名称）
# Windows Display Name (Name shown when adding printer in Windows)
WINDOWS_DISPLAY_NAME = "virtual photo printer"                      # Windows显示名称（小写无空格）- Windows display name (lowercase, no spaces)

# 服务器监听配置
# Server Listening Configuration
DEFAULT_HOST = "0.0.0.0"                                          # 监听地址（0.0.0.0表示所有接口）- Listen address (0.0.0.0 means all interfaces)
DEFAULT_PORT = 631                                                # HTTP端口（IPP over HTTP）- HTTP port (IPP over HTTP)
DEFAULT_SSL_PORT = 443                                            # HTTPS端口（IPP over HTTPS）- HTTPS port (IPP over HTTPS)

# 打印机硬件信息（用于mDNS广播和IPP属性）
# Printer Hardware Information (for mDNS broadcasting and IPP attributes)
DEFAULT_MANUFACTURER = "IPP Manufacturer"                         # 设备制造商 - Device manufacturer
DEFAULT_MODEL = "Virtual Photo Printer"                           # 打印机型号 - Printer model
DEFAULT_SERIAL_NUMBER = "SN1234567890"                            # 序列号 - Serial number

# PPD文件信息（Windows驱动程序使用）
# PPD File Information (Used by Windows drivers)
PPD_PRODUCT = "ipp-server"                                        # PPD产品名称 - PPD product name
PPD_MANUFACTURER = "h2g2bob"                                      # PPD制造商 - PPD manufacturer
PPD_MODEL = "ipp-server-pdf"                                      # PPD模型名称 - PPD model name
PPD_SHORT_NICKNAME = "IPP Photo Printer"                          # PPD短名称 - PPD short name
PPD_NICKNAME = "IPP Virtual Photo Printer"                        # PPD完整名称 - PPD full name

# 1284设备ID（Windows设备识别）
# 1284 Device ID (Windows device identification)
PPD_1284_DEVICE_ID = "MFG:{manufacturer};MDL:{model};DES:{model};CLS:PRINTER;CMD:POSTSCRIPT;"