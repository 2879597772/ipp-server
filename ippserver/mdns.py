"""
mDNS (Bonjour/Avahi) 服务广播模块 - 支持带空格打印机名称版
mDNS (Bonjour/Avahi) Service Broadcasting Module - Support for Printer Names with Spaces
"""

import socket
import threading
import time
import logging
import struct
import re
import os
from typing import Optional, Dict, List
import uuid as uuid_module

try:
    from .translations import t
except ImportError:
    def t(key, **kwargs):
        return key


class MDNSBroadcaster:
    """优化的mDNS广播器，支持带空格打印机名称
    Optimized mDNS broadcaster supporting printer names with spaces"""
    
    MDNS_IP = '224.0.0.251'
    MDNS_PORT = 5353
    DNS_TTL = 120  # 2分钟 - 2 minutes
    
    def __init__(self, printer_name: str, port: int, ssl_port: int, host: str = '0.0.0.0',
                 description: str = 'IPP Virtual Printer', location: str = 'Local Network',
                 printer_uuid: str = None, ssl_enabled: bool = True):
        """
        初始化mDNS广播器
        Initialize mDNS broadcaster
        
        Args:
            printer_name: 打印机名称（可以包含空格，如："My Photo Printer"）
                        Printer name (can contain spaces, e.g., "My Photo Printer")
            port: HTTP端口 (631) - HTTP port (631)
            ssl_port: HTTPS端口 (443) - HTTPS port (443)
            host: 监听地址 - Listening address
            description: 打印机描述 - Printer description
            location: 打印机位置 - Printer location
            printer_uuid: 打印机UUID - Printer UUID
            ssl_enabled: 是否启用SSL - Whether SSL is enabled
        """
        # 保存原始名称（可能包含空格）- Save original name (may contain spaces)
        self.original_name = printer_name
        
        # 清理后的主机名（用于 .local 域名）：不能有空格
        # Sanitized hostname (for .local domain): cannot have spaces
        self.hostname = self._sanitize_hostname(printer_name)
        
        # 显示名称（用于 TXT 记录和 Windows 显示）：保持原始名称，包含空格
        # Display name (for TXT records and Windows display): keep original name, including spaces
        self.display_name = printer_name
        
        # 服务实例名称（包含空格）- Service instance name (contains spaces)
        # 格式: "My Photo Printer._ipp._tcp.local" - Format: "My Photo Printer._ipp._tcp.local"
        self.service_instance_name = f"{printer_name}"
        
        self.port = port  # HTTP端口 (631) - HTTP port (631)
        self.ssl_port = ssl_port  # HTTPS端口 (443) - HTTPS port (443)
        self.host = host
        self.description = description
        self.location = location
        
        # 打印机硬件信息 - 符合IPP协议
        # Printer hardware information - Compliant with IPP protocol
        self.printer_manufacturer = "IPP Manufacturer"        # 设备制造商 - Device manufacturer
        self.printer_model = "Virtual Photo Printer"          # 型号 - Model
        self.printer_serial_number = "SN1234567890"           # 序列号（SN）- Serial number (SN)
        self.printer_uuid = printer_uuid or self._generate_uuid()  # UUID
        self.ssl_enabled = ssl_enabled
        self.https_available = ssl_enabled  # 默认假设HTTPS可用，将在启动时检查
                                          # Default assumes HTTPS is available, will check at startup
        
        self._running = False
        self._broadcast_thread = None
        self._socket_v4 = None
        self._socket_v6 = None
        
        # 获取本地IP地址 - Get local IP address
        self.local_ip = self._get_local_ip()
        
        # 生成网页接口URL - Generate web interface URL
        self.web_interface_url = f"http://{self.local_ip}:{self.port}/"
        if self.ssl_enabled:
            self.web_interface_secure_url = f"https://{self.local_ip}:{self.ssl_port}/"
        else:
            self.web_interface_secure_url = self.web_interface_url
        
        logging.info(t('mdns_initialized', hostname=self.hostname, local_ip=self.local_ip))
        logging.info(t('display_name', display_name=self.display_name))
    
    def _generate_uuid(self) -> str:
        """生成UUID - Generate UUID"""
        return str(uuid_module.uuid4())
    
    def _sanitize_hostname(self, name: str) -> str:
        """
        清理主机名，确保符合RFC 1123
        Sanitize hostname to ensure RFC 1123 compliance
        
        Args:
            name: 原始名称（可能包含空格）- Original name (may contain spaces)
            
        Returns:
            清理后的主机名（无空格）- Sanitized hostname (no spaces)
        """
        if not name:
            return 'ipp-printer'
        
        # 1. 将空格替换为连字符 - Replace spaces with hyphens
        name = name.replace(' ', '-')
        
        # 2. 移除所有不允许的字符，只保留字母、数字和连字符
        # Remove all disallowed characters, keep only letters, numbers, and hyphens
        sanitized = re.sub(r'[^a-zA-Z0-9\-]', '', name)
        
        # 3. 确保不以连字符开头或结尾 - Ensure doesn't start or end with hyphen
        sanitized = sanitized.strip('-')
        
        # 4. 转换为小写 - Convert to lowercase
        sanitized = sanitized.lower()
        
        # 5. 确保长度在1-63字符之间 - Ensure length between 1-63 characters
        if len(sanitized) > 63:
            sanitized = sanitized[:63]
        elif len(sanitized) == 0:
            sanitized = 'ipp-printer'
        
        # 6. 确保没有连续多个连字符 - Ensure no consecutive hyphens
        while '--' in sanitized:
            sanitized = sanitized.replace('--', '-')
        
        logging.debug(f"Sanitized hostname: '{name}' -> '{sanitized}'")
        return sanitized
    
    def _get_local_ip(self) -> str:
        """获取本地IP地址 - 优化版
        Get local IP address - Optimized version"""
        try:
            # 方法1: 连接到外部地址 - Method 1: Connect to external address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.1)
            try:
                s.connect(('8.8.8.8', 80))
                ip = s.getsockname()[0]
                s.close()
                if ip and ip != '127.0.0.1':
                    return ip
            except:
                s.close()
            
            # 方法2: 使用 netifaces（如果可用）- Method 2: Use netifaces (if available)
            try:
                import netifaces
                for interface in netifaces.interfaces():
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        for addr in addrs[netifaces.AF_INET]:
                            ip = addr.get('addr', '')
                            if ip and not ip.startswith('127.'):
                                return ip
            except ImportError:
                pass
            
            # 方法3: 使用gethostbyname - Method 3: Use gethostbyname
            try:
                ip = socket.gethostbyname(socket.gethostname())
                if ip and ip != '127.0.0.1':
                    return ip
            except Exception:
                pass
            
        except Exception as e:
            logging.debug(f"Error getting local IP: {e}")
        
        return '127.0.0.1'
    
    def _create_mdns_socket(self, ip_version: int = 4) -> socket.socket:
        """创建mDNS广播socket
        Create mDNS broadcast socket"""
        try:
            if ip_version == 4:
                # IPv4 socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                
                # 设置多播TTL - Set multicast TTL
                ttl = struct.pack('b', 255)  # 增加到255以穿透更多网络设备
                                          # Increase to 255 to penetrate more network devices
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
                
                # 绑定到所有接口 - Bind to all interfaces
                sock.bind(('', self.MDNS_PORT))
                
                # 加入多播组 - Join multicast group
                mreq = struct.pack('4sl', socket.inet_aton(self.MDNS_IP), socket.INADDR_ANY)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                
                # 启用多播回环 - Enable multicast loopback
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
                
            else:
                # IPv6 socket (如果支持) - IPv6 socket (if supported)
                sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                # 加入IPv6多播组 - Join IPv6 multicast group
                mreq = struct.pack('16sI', socket.inet_pton(socket.AF_INET6, 'ff02::fb'), 0)
                sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)
                
                # 绑定 - Bind
                sock.bind(('', self.MDNS_PORT))
            
            sock.settimeout(1.0)
            return sock
            
        except Exception as e:
            logging.debug(t('mdns_socket_creation_failed', ip_version=ip_version, error=str(e)))
            return None
    
    def _encode_dns_name(self, name: str) -> bytes:
        """
        编码DNS名称为字节
        Encode DNS name to bytes
        
        Args:
            name: 域名（可以包含空格）- Domain name (can contain spaces)
            
        Returns:
            编码后的字节 - Encoded bytes
        """
        # 处理服务实例名称中的空格
        # Handle spaces in service instance name
        # 例如: "My Printer._ipp._tcp.local" - e.g., "My Printer._ipp._tcp.local"
        parts = name.split('.')
        encoded = b''
        for part in parts:
            if part:
                # 对于包含空格的部分，直接编码
                # For parts containing spaces, encode directly
                # DNS标签允许除空字节外的任何字节
                # DNS labels allow any bytes except null bytes
                part_bytes = part.encode('utf-8')
                if len(part_bytes) > 63:
                    part_bytes = part_bytes[:63]
                encoded += bytes([len(part_bytes)]) + part_bytes
        encoded += b'\x00'  # 结束标记 - End marker
        return encoded
    
    def _create_dns_record(self, name: str, rtype: int, ttl: int, data: bytes) -> bytes:
        """创建DNS记录
        Create DNS record"""
        encoded_name = self._encode_dns_name(name)
        
        # DNS记录头部 - DNS record header
        record = encoded_name
        
        # 类型和类 - Type and class
        record += struct.pack('>HH', rtype, 0x8001)  # IN class with cache flush flag
        
        # TTL
        record += struct.pack('>I', ttl)
        
        # 数据长度和数据 - Data length and data
        record += struct.pack('>H', len(data))
        record += data
        
        return record
    
    def _create_service_packet(self, service_type: str, port: int, is_ssl: bool = False) -> bytes:
        """创建完整的服务广播包
        Create complete service broadcast packet"""
        # 服务实例名称（可以包含空格）
        # Service instance name (can contain spaces)
        # 例如: "My Photo Printer._ipp._tcp.local"
        # e.g., "My Photo Printer._ipp._tcp.local"
        service_instance = f"{self.display_name}.{service_type}"
        
        # 构建DNS报文 - Build DNS message
        packet = b''
        
        # 事务ID (0x0000用于公告) - Transaction ID (0x0000 for announcements)
        packet += b'\x00\x00'
        
        # 标志：响应，权威答案，递归可用
        # Flags: response, authoritative answer, recursion available
        packet += b'\x84\x00'
        
        # 问题数、回答数、权威数、附加数
        # Question count, answer count, authority count, additional count
        answers = 3  # PTR, SRV, TXT
        additionals = 1  # A记录 - A record
        
        packet += struct.pack('>HHHH', 0, answers, 0, additionals)
        
        # 1. PTR记录 - 服务发现
        # 1. PTR record - Service discovery
        packet += self._create_dns_record(
            service_type,
            12,  # PTR类型 - PTR type
            self.DNS_TTL,
            self._encode_dns_name(service_instance)
        )
        
        # 2. SRV记录 - 服务位置
        # 2. SRV record - Service location
        srv_data = struct.pack('>HHH', 0, 0, port)
        srv_data += self._encode_dns_name(f"{self.hostname}.local")
        
        packet += self._create_dns_record(
            service_instance,
            33,  # SRV类型 - SRV type
            self.DNS_TTL,
            srv_data
        )
        
        # 3. TXT记录 - 服务属性
        # 3. TXT record - Service attributes
        txt_attrs = {
            # IPP协议标准属性 - IPP protocol standard attributes
            'txtvers': '1',
            'adminurl': self.web_interface_url,
            'note': self.description,
            
            # 打印机硬件信息 - 符合IPP协议
            # Printer hardware information - Compliant with IPP protocol
            'product': self.printer_model,
            'ty': self.display_name,  # 使用带空格的显示名称 - Use display name with spaces
            'usb_MFG': self.printer_manufacturer,
            'usb_MDL': self.printer_model,
            'usb_CMD': 'POSTSCRIPT,PDF,PCL',
            
            # 序列号和UUID - Serial number and UUID
            'SN': self.printer_serial_number,
            'UUID': self.printer_uuid,
            
            # 服务信息 - Service information
            'rp': 'ipp/print',
            'pdl': 'application/postscript,application/pdf,image/jpeg,image/png,image/tiff,image/bmp,image/gif,text/plain',
            
            # 作业处理 - Job handling
            'qtotal': '1',
            'priority': '0',
            
            # 打印机能力 - Printer capabilities
            'color': 'T',
            'duplex': 'T',
            'copies': 'T',
            'Collate': 'F',
            'Staple': 'F',
            
            # 主机名（无空格版本）- Hostname (no spaces version)
            'hostname': f"{self.hostname}.local",
            
            # 纸张支持 - Paper support
            'papersize': 'A0,A1,A2,A3,A4,A5,A6,A7,A8,A9,A10,B0,B1,B2,B3,B4,B5,B6,B7,B8,B9,B10,Letter,Legal,Tabloid,Ledger,Executive,Photo4x6,Photo5x7,Photo8x10,Photo10x15,Photo13x18,Photo15x20',
            
            # 分辨率 - Resolution
            'resolution': '72,100,150,200,300,400,600,800,1200,1600,2400,3200,4800dpi',
            
            # Windows照片打印支持 - Windows photo printing support
            'kind': 'document,envelope,postcard,photo,label',
            'paper': 'plain,photo,glossy,transparency',
            'print_color_mode': 'color,monochrome',
            'Bin': 'tray1,tray2,photo-tray',
            'photo': 'T',
            'photopaper': 'T',
            'photoresolution': '1200,2400dpi',
        }
        
        # 如果是HTTPS服务，添加安全URL和TLS标志
        # If HTTPS service, add secure URL and TLS flag
        if is_ssl and self.https_available:
            txt_attrs['adminurl'] = self.web_interface_secure_url
            txt_attrs['TLS'] = '1'
            txt_attrs['URISchemes'] = 'https,ipps'
        elif self.https_available:
            # 对于HTTP服务，如果HTTPS可用，也指向HTTPS URL
            # For HTTP service, if HTTPS is available, also point to HTTPS URL
            txt_attrs['adminurl'] = self.web_interface_secure_url
            txt_attrs['URISchemes'] = 'https,ipps'
        else:
            # 如果HTTPS不可用，只使用HTTP
            # If HTTPS is unavailable, use HTTP only
            txt_attrs['adminurl'] = self.web_interface_url
            txt_attrs['URISchemes'] = 'http,ipp'
        
        # 构建TXT数据 - Build TXT data
        txt_data = b''
        for key, value in txt_attrs.items():
            entry = f"{key}={value}".encode('utf-8')
            if len(entry) > 255:
                entry = entry[:255]
            txt_data += bytes([len(entry)]) + entry
        
        packet += self._create_dns_record(
            service_instance,
            16,  # TXT类型 - TXT type
            self.DNS_TTL,
            txt_data
        )
        
        # 4. A记录 - 主机地址
        # 4. A record - Host address
        packet += self._create_dns_record(
            f"{self.hostname}.local",
            1,  # A类型 - A type
            self.DNS_TTL,
            socket.inet_aton(self.local_ip)
        )
        
        return packet
    
    def _broadcast_service(self, socket_obj, service_type: str, port: int, is_ssl: bool = False):
        """广播单个服务
        Broadcast single service"""
        try:
            packet = self._create_service_packet(service_type, port, is_ssl)
            
            # 广播3次以提高可靠性
            # Broadcast 3 times for reliability
            for i in range(3):
                if socket_obj.family == socket.AF_INET:
                    socket_obj.sendto(packet, (self.MDNS_IP, self.MDNS_PORT))
                else:
                    # IPv6多播地址 - IPv6 multicast address
                    socket_obj.sendto(packet, ('ff02::fb', self.MDNS_PORT))
                
                if i < 2:  # 前两次之间短暂延迟 - Short delay between first two broadcasts
                    time.sleep(0.1)
                    
        except Exception as e:
            logging.warning(t('failed_to_broadcast_service', service_type=service_type, error=str(e)))
    
    def set_https_available(self, available: bool):
        """设置HTTPS是否可用
        Set whether HTTPS is available"""
        self.https_available = available
        if available:
            logging.info(t('https_available_status', status='available', type='secure'))
        else:
            logging.info(t('https_available_status', status='not available', type='HTTP-only'))
    
    def _broadcast_loop(self):
        """广播循环
        Broadcast loop"""
        broadcast_count = 0
        
        try:
            # 首次广播：立即发送多次
            # Initial broadcast: send multiple times immediately
            logging.info(t('initial_advertisements'))
            for i in range(10):
                self._broadcast_all_services()
                time.sleep(0.5)
            
            logging.info(t('initial_advertisements_sent'))
            
            while self._running:
                try:
                    # 每20秒广播一次
                    # Broadcast every 20 seconds
                    for i in range(20):
                        if not self._running:
                            break
                        time.sleep(1)
                    
                    if not self._running:
                        break
                    
                    # 广播所有服务
                    # Broadcast all services
                    self._broadcast_all_services()
                    
                    broadcast_count += 1
                    
                    # 每10次广播记录一次日志
                    # Log every 10 broadcasts
                    if broadcast_count % 10 == 0:
                        logging.info(f"mDNS broadcast #{broadcast_count} completed")
                        
                except Exception as e:
                    logging.error(t('broadcast_cycle_error', error=str(e)))
                    time.sleep(5)
                    
        except Exception as e:
            logging.error(t('broadcast_loop_terminated', error=str(e)))
        finally:
            self._cleanup_sockets()
    
    def _broadcast_all_services(self):
        """广播所有服务
        Broadcast all services"""
        services = []
        
        # 总是广播HTTP服务
        # Always broadcast HTTP service
        services.append(("_ipp._tcp.local", self.port, False))
        
        # 如果HTTPS可用，广播HTTPS服务
        # If HTTPS is available, broadcast HTTPS service
        if self.https_available:
            services.append(("_ipps._tcp.local", self.ssl_port, True))
            services.append(("_printer._tcp.local", self.ssl_port, True))
            services.append(("_universal._sub._ipp._tcp.local", self.ssl_port, True))
        else:
            # 如果HTTPS不可用，只广播HTTP服务
            # If HTTPS is unavailable, broadcast HTTP service only
            services.append(("_printer._tcp.local", self.port, False))
            services.append(("_universal._sub._ipp._tcp.local", self.port, False))
        
        for service_type, port, is_ssl in services:
            if self._socket_v4:
                self._broadcast_service(self._socket_v4, service_type, port, is_ssl)
            
            if self._socket_v6:
                self._broadcast_service(self._socket_v6, service_type, port, is_ssl)
    
    def _cleanup_sockets(self):
        """清理socket
        Cleanup sockets"""
        for sock in [self._socket_v4, self._socket_v6]:
            if sock:
                try:
                    sock.close()
                except:
                    pass
    
    def start(self):
        """启动mDNS广播
        Start mDNS broadcasting"""
        if self._running:
            logging.warning(t('mdns_already_running'))
            return
        
        try:
            # 创建IPv4和IPv6 socket
            # Create IPv4 and IPv6 sockets
            self._socket_v4 = self._create_mdns_socket(4)
            try:
                self._socket_v6 = self._create_mdns_socket(6)
            except Exception:
                self._socket_v6 = None
                logging.debug(t('mdns_ipv6_unavailable'))
            
            if not self._socket_v4 and not self._socket_v6:
                raise Exception(t('mdns_no_sockets'))
            
            self._running = True
            self._broadcast_thread = threading.Thread(
                target=self._broadcast_loop, 
                daemon=True,
                name="mDNS-Broadcaster"
            )
            self._broadcast_thread.start()
            
            # 打印详细信息 - Print detailed information
            logging.info("=" * 60)
            logging.info(t('mdns_service_started'))
            logging.info("=" * 60)
            logging.info(t('printer_display_name', display_name=self.display_name))
            logging.info(t('hostname_info', hostname=self.hostname))
            logging.info(t('ip_address', local_ip=self.local_ip))
            logging.info(t('http_port_info', port=self.port))
            
            if self.https_available:
                logging.info(t('https_port_info', port=self.ssl_port, status='available'))
                logging.info(t('primary_url', url=self.web_interface_secure_url))
                logging.info(t('http_redirect_note'))
            else:
                logging.info(t('https_port_info', port=self.ssl_port, status='not available'))
                logging.info(t('primary_url', url=self.web_interface_url))
                logging.info(t('serving_over_http'))
            
            # 打印硬件信息 - Print hardware information
            logging.info(t('hardware_information'))
            logging.info(t('manufacturer_label', manufacturer=self.printer_manufacturer))
            logging.info(t('model_label', model=self.printer_model))
            logging.info(t('serial_label', serial=self.printer_serial_number))
            logging.info(t('uuid_label', uuid=self.printer_uuid))
            
            logging.info(t('color_support_info'))
            logging.info(t('paper_sizes_info'))
            logging.info(t('resolutions_info'))
            logging.info(t('windows_photo_printing'))
            logging.info(t('services_advertised'))
            if self.https_available:
                logging.info(f"  • _ipp._tcp.local (HTTP on port {self.port}, redirects to HTTPS)")
                logging.info(f"  • _ipps._tcp.local (HTTPS on port {self.ssl_port}, primary)")
                logging.info(f"  • _printer._tcp.local (Generic printer discovery)")
                logging.info(f"  • _universal._sub._ipp._tcp.local (Universal printing)")
                logging.info(t('service_instance', instance=f"{self.display_name}._ipps._tcp.local"))
            else:
                logging.info(f"  • _ipp._tcp.local (HTTP on port {self.port})")
                logging.info(f"  • _printer._tcp.local (Generic printer discovery)")
                logging.info(f"  • _universal._sub._ipp._tcp.local (Universal printing)")
                logging.info(t('service_instance', instance=f"{self.display_name}._ipp._tcp.local"))
            logging.info("=" * 60)
            
        except Exception as e:
            logging.error(t('failed_to_start_mdns', error=str(e)))
            self._running = False
            self._cleanup_sockets()
            raise
    
    def stop(self):
        """停止mDNS广播
        Stop mDNS broadcasting"""
        if not self._running:
            return
        
        logging.info(t('mdns_stopping'))
        self._running = False
        
        if self._broadcast_thread:
            self._broadcast_thread.join(timeout=5)
            self._broadcast_thread = None
        
        self._cleanup_sockets()
        
        logging.info(t('mdns_stopped'))
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()