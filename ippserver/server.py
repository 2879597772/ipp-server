from io import BytesIO
import threading
import socketserver
import http.server
import socket
import ssl
import time
import logging
import os.path
import tempfile
import atexit
import subprocess
from http import HTTPStatus
from urllib.parse import urlparse, urlunparse

try:
    from . import ssl_config
except ImportError:
    # 如果ssl_config不存在，创建一个空配置 - If ssl_config doesn't exist, create an empty configuration
    class ssl_config:
        SSL_CERTIFICATE = None
        SSL_PRIVATE_KEY = None

from . import request
from .constants import StatusCodeEnum

# 导入翻译模块 - Import translation module
try:
    from .translations import t
except ImportError:
    # 如果翻译模块不存在，创建一个简单的替代函数 - If translation module doesn't exist, create a simple fallback
    def t(key, **kwargs):
        return key.format(**kwargs) if kwargs else key


def _get_next_chunk(rfile):
    while True:
        chunk_size_s = rfile.readline()
        logging.debug(t('chunk_size_debug', chunk_size=chunk_size_s))
        if not chunk_size_s:
            raise RuntimeError(
                'Socket closed in the middle of a chunked request'
            )
        if chunk_size_s.strip() != b'':
            break

    chunk_size = int(chunk_size_s, 16)
    if chunk_size == 0:
        return b''
    chunk = rfile.read(chunk_size)
    logging.debug(t('chunk_length_debug', length=len(chunk)))
    # 读取尾随的CRLF - Read the trailing CRLF
    rfile.read(2)
    return chunk


def read_chunked(rfile):
    while True:
        chunk = _get_next_chunk(rfile)
        if chunk == b'':
            break
        else:
            yield chunk


def check_ssl_certificate_valid():
    """检查SSL证书是否有效 - Check SSL certificate validity"""
    try:
        # 检查证书和私钥是否存在 - Check if certificate and private key exist
        if not ssl_config.SSL_CERTIFICATE or not ssl_config.SSL_PRIVATE_KEY:
            logging.warning(t('ssl_certificate_missing'))
            return False
        
        # 创建临时文件 - Create temporary files
        cert_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pem')
        key_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.key')
        
        try:
            # 写入证书和私钥 - Write certificate and private key
            cert_file.write(ssl_config.SSL_CERTIFICATE)
            key_file.write(ssl_config.SSL_PRIVATE_KEY)
            
            cert_file.close()
            key_file.close()
            
            # 尝试创建SSL上下文并加载证书 - Try to create SSL context and load certificate
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cert_file.name, key_file.name)
            
            # 验证证书基本格式 - Verify basic certificate format
            logging.info(t('certificate_validation_passed'))
            logging.info(f"Certificate size: {len(ssl_config.SSL_CERTIFICATE)} bytes")
            logging.info(f"Private key size: {len(ssl_config.SSL_PRIVATE_KEY)} bytes")
            
            return True
            
        except ssl.SSLError as e:
            logging.error(t('certificate_validation_failed', error=e))
            return False
        except Exception as e:
            logging.error(t('certificate_validation_error', error=e))
            return False
        finally:
            # 清理临时文件 - Clean up temporary files
            try:
                os.unlink(cert_file.name)
            except:
                pass
            try:
                os.unlink(key_file.name)
            except:
                pass
                
    except Exception as e:
        logging.error(t('error_checking_ssl_certificate', error=e))
        return False


class IPPRequestHandler(http.server.BaseHTTPRequestHandler):
    default_request_version = "HTTP/1.1"
    protocol_version = "HTTP/1.1"
    
    def setup(self):
        """初始化连接 - Initialize connection"""
        http.server.BaseHTTPRequestHandler.setup(self)
        
        # 检查是否是SSL连接 - Check if this is an SSL connection
        if hasattr(self.connection, 'context'):  # 如果是SSL socket - If it's an SSL socket
            try:
                # SSL握手已经在服务器层面完成 - SSL handshake already completed at server level
                logging.debug(t('ssl_connection_established'))
            except Exception as e:
                logging.error(t('ssl_setup_error', error=e))
                self.close_connection = True
        
    def parse_request(self):
        """解析请求，支持HTTP和HTTPS - Parse request, support HTTP and HTTPS"""
        try:
            ret = http.server.BaseHTTPRequestHandler.parse_request(self)
            
            if ret:
                # Now self.headers exists
                if 'chunked' in self.headers.get('transfer-encoding', ''):
                    # 读取分块数据 - Read chunked data
                    chunked_data = b"".join(read_chunked(self.rfile))
                    self.rfile = BytesIO(chunked_data)
            self.close_connection = True
            return ret
        except Exception as e:
            logging.error(t('error_parsing_request', error=str(e)))
            self.close_connection = True
            return False

    def log_error(self, format, *args):
        logging.error(format, *args)

    def log_message(self, format, *args):
        logging.debug(format, *args)

    def send_headers(self, status=200, content_type='text/plain',
                     content_length=None):
        self.log_request(status)
        self.send_response_only(status)
        self.send_header('Server', 'ipp-server')
        self.send_header('Date', self.date_time_string())
        self.send_header('Content-Type', content_type)
        if content_length:
            self.send_header('Content-Length', '%u' % content_length)
        self.send_header('Connection', 'close')
        self.end_headers()

    def do_POST(self):
        try:
            self.handle_ipp()
        except Exception as e:
            logging.error(t('error_handling_ipp_request', error=str(e)))
            try:
                self.send_error(HTTPStatus.BAD_REQUEST, "Bad request")
            except:
                pass

    def do_GET(self):
        try:
            self.handle_www()
        except Exception as e:
            logging.error(t('error_handling_http_request', error=str(e)))
            try:
                self.send_error(HTTPStatus.BAD_REQUEST, "Bad request")
            except:
                pass

    def is_secure(self):
        """检查是否是安全连接 - Check if connection is secure"""
        return hasattr(self.connection, 'context') and isinstance(self.connection, ssl.SSLSocket)

    def handle_www(self):
        if self.path == '/':
            self.send_headers(
                status=HTTPStatus.OK, content_type='text/plain'
            )
            self.wfile.write(b'IPP server is running ...')
        elif self.path.endswith('.ppd'):
            self.send_headers(
                status=HTTPStatus.OK, content_type='text/plain'
            )
            self.wfile.write(self.server.behaviour.ppd.text())
        else:
            self.send_headers(
                status=HTTPStatus.NOT_FOUND, content_type='text/plain'
            )
            self.wfile.write(b'404 Not Found')

    def handle_expect_100(self):
        """禁用expect 100-continue - Disable expect 100-continue"""
        return True

    def handle_ipp(self):
        try:
            # 记录所有HTTP头（调试） - Log all HTTP headers (debug)
            logging.debug(t('http_headers_debug'))
            for header, value in self.headers.items():
                logging.debug(t('http_header_item', header=header, value=value))
            
            # 特别检查压缩相关头 - Specifically check compression-related headers
            content_encoding = self.headers.get('Content-Encoding', '')
            transfer_encoding = self.headers.get('Transfer-Encoding', '')
            content_length = self.headers.get('Content-Length')
        
            logging.info(f"Content-Encoding: {content_encoding}")
            logging.info(f"Transfer-Encoding: {transfer_encoding}")
            logging.info(f"Content-Length: {content_length}")
            
            # 检查是否有压缩内容 - Check if there is compressed content
            if content_encoding:
                logging.info(f"Content is encoded with: {content_encoding}")
                # 注意：我们不会在这里解压，因为IPP请求处理会在behaviour.py中处理
                # Note: We won't decompress here because IPP request processing will handle it in behaviour.py
            
            # 解析IPP请求 - Parse IPP request
            self.ipp_request = request.IppRequest.from_file(self.rfile)

            # 处理Expect: 100-continue - Handle Expect: 100-continue
            expect_header = self.headers.get('Expect', '')
            if expect_header.lower() == '100-continue':
                self.send_response_only(100)
                self.end_headers()

            if self.server.behaviour.expect_page_data_follows(self.ipp_request):
                if '100-continue' not in expect_header.lower():
                    self.send_headers(
                        status=100, content_type='application/ipp'
                    )
                postscript_file = self.rfile
            else:
                postscript_file = None

            # 处理请求 - Process the request
            ipp_response = self.server.behaviour.handle_ipp(
                self.ipp_request, postscript_file
            ).to_string()
            
            # 将IPP状态码映射到HTTP状态码 - Map IPP status codes to HTTP status codes
            http_status = self.map_ipp_status_to_http(ipp_response[2:4])
            
            self.send_headers(
                status=http_status, content_type='application/ipp',
                content_length=len(ipp_response)
            )
            self.wfile.write(ipp_response)
            
        except Exception as e:
            logging.error(t('error_processing_ipp_request', error=str(e)))
            try:
                self.send_error(HTTPStatus.BAD_REQUEST, "Bad IPP request")
            except:
                pass

    def map_ipp_status_to_http(self, ipp_status_bytes):
        """将IPP状态码映射到HTTP状态码 - Map IPP status code to HTTP status code"""
        if len(ipp_status_bytes) != 2:
            return HTTPStatus.OK
        
        ipp_status = struct.unpack('>H', ipp_status_bytes)[0]
        
        # 成功状态码 - Successful status codes
        if ipp_status in [StatusCodeEnum.ok, 
                         StatusCodeEnum.successful_ok_ignored_or_substituted_attributes,
                         StatusCodeEnum.successful_ok_conflicting_attributes]:
            return HTTPStatus.OK
        
        # 客户端错误状态码 - Client error status codes
        elif ipp_status in [StatusCodeEnum.client_error_bad_request,
                           StatusCodeEnum.client_error_forbidden,
                           StatusCodeEnum.client_error_not_authenticated,
                           StatusCodeEnum.client_error_not_authorized,
                           StatusCodeEnum.client_error_not_possible,
                           StatusCodeEnum.client_error_timeout,
                           StatusCodeEnum.client_error_not_found,
                           StatusCodeEnum.client_error_gone,
                           StatusCodeEnum.client_error_request_entity_too_large,
                           StatusCodeEnum.client_error_request_value_too_long,
                           StatusCodeEnum.client_error_document_format_not_supported,
                           StatusCodeEnum.client_error_attributes_or_values_not_supported,
                           StatusCodeEnum.client_error_uri_scheme_not_supported,
                           StatusCodeEnum.client_error_charset_not_supported,
                           StatusCodeEnum.client_error_conflicting_attributes,
                           StatusCodeEnum.client_error_compression_not_supported,
                           StatusCodeEnum.client_error_compression_error,
                           StatusCodeEnum.client_error_document_format_error,
                           StatusCodeEnum.client_error_document_access_error]:
            return HTTPStatus.BAD_REQUEST
        
        # 服务器错误状态码 - Server error status codes
        else:
            return HTTPStatus.INTERNAL_SERVER_ERROR

    def handle_one_request(self):
        try:
            return http.server.BaseHTTPRequestHandler.handle_one_request(self)
        except Exception as e:
            logging.error(t('unhandled_error_in_request', error=str(e)))
            self.close_connection = True
            return False


import struct


class IPPServer(socketserver.ThreadingTCPServer):
    """完整的IPP服务器，仅在有效证书时支持SSL/TLS - Complete IPP server, SSL/TLS support only with valid certificates"""
    
    allow_reuse_address = True
    request_queue_size = 128
    
    def __init__(self, address, request_handler, behaviour, ssl_enabled=False):
        self.behaviour = behaviour
        self.ssl_enabled = ssl_enabled
        self.ssl_context = None
        
        # 如果要求启用SSL，检查证书有效性 - If SSL is requested, check certificate validity
        if ssl_enabled:
            if check_ssl_certificate_valid():
                self.ssl_context = self._create_ssl_context()
                if self.ssl_context is None:
                    self.ssl_enabled = False
                    logging.warning(t('ssl_tls_failed'))
            else:
                self.ssl_enabled = False
                logging.warning(t('certificate_validation_failed'))
        
        super().__init__(address, request_handler)
        
    def _create_ssl_context(self):
        """创建SSL上下文 - 仅使用有效的配置证书 - Create SSL context - only using valid configured certificates"""
        try:
            # 再次验证证书 - Verify certificate again
            if not check_ssl_certificate_valid():
                logging.error(t('certificate_validation_failed'))
                return None
            
            # 创建SSL上下文 - Create SSL context
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            
            # 设置TLS版本 - 使用TLS 1.2作为最低版本 - Set TLS version - use TLS 1.2 as minimum
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            
            # 设置密码套件 - Set cipher suites
            context.set_ciphers(
                'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:'
                'ECDHE+AES256:ECDHE+AES128:DHE+AES256:DHE+AES128'
            )
            
            # 禁用不安全的协议 - Disable insecure protocols
            context.options |= ssl.OP_NO_SSLv2
            context.options |= ssl.OP_NO_SSLv3
            context.options |= ssl.OP_NO_TLSv1
            
            # 启用证书验证（如果需要）- Enable certificate verification (if needed)
            context.verify_mode = ssl.CERT_NONE  # 不验证客户端证书 - Do not verify client certificates
            
            # 加载证书 - Load certificates
            if self._load_certificates(context):
                logging.info(t('ssl_context_created'))
                return context
            else:
                logging.error(t('certificate_loading_failed'))
                return None
                
        except Exception as e:
            logging.error(t('ssl_tls_failed', error=e))
            return None
    
    def _load_certificates(self, context):
        """加载证书和私钥 - Load certificates and private key"""
        try:
            # 创建临时文件 - Create temporary files
            cert_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pem')
            key_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.key')
            
            try:
                # 写入证书和私钥 - Write certificates and private key
                cert_file.write(ssl_config.SSL_CERTIFICATE)
                key_file.write(ssl_config.SSL_PRIVATE_KEY)
                
                cert_file.close()
                key_file.close()
                
                # 加载证书链 - Load certificate chain
                context.load_cert_chain(cert_file.name, key_file.name)
                
                # 验证加载成功 - Verify successful loading
                logging.info(t('ssl_certificates_loaded'))
                return True
                
            except ssl.SSLError as e:
                logging.error(t('ssl_error_loading_certificates', error=e))
                return False
            except Exception as e:
                logging.error(t('certificate_loading_failed', error=e))
                return False
            finally:
                # 清理临时文件 - Clean up temporary files
                try:
                    os.unlink(cert_file.name)
                except:
                    pass
                try:
                    os.unlink(key_file.name)
                except:
                    pass
                
        except Exception as e:
            logging.error(t('failed_to_create_certificate_files', error=e))
            return False
    
    def server_bind(self):
        """重写server_bind以支持SSL - Override server_bind to support SSL"""
        super().server_bind()
        
        if self.ssl_enabled and self.ssl_context:
            try:
                # 包装socket为SSL socket - Wrap socket as SSL socket
                self.socket = self.ssl_context.wrap_socket(
                    self.socket,
                    server_side=True,
                    do_handshake_on_connect=False  # 延迟握手 - Delay handshake
                )
                self.socket.settimeout(30.0)  # 设置超时 - Set timeout
                logging.info(t('ssl_tls_enabled', address=self.server_address))
            except Exception as e:
                logging.error(t('ssl_tls_failed', error=e))
                # 关闭SSL - Disable SSL
                self.ssl_enabled = False
                self.ssl_context = None
                
                # 重新绑定到普通socket - Rebind to regular socket
                self.socket.close()
                self.socket = socket.socket(self.address_family, self.socket_type)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_bind()
                logging.info(t('ssl_disabled_fallback', address=self.server_address))
    
    def get_request(self):
        """重写get_request以处理SSL握手 - Override get_request to handle SSL handshake"""
        sock, addr = super().get_request()
        
        if self.ssl_enabled and isinstance(sock, ssl.SSLSocket):
            try:
                # 执行SSL握手 - Perform SSL handshake
                sock.do_handshake()
                logging.debug(t('ssl_handshake_completed', address=addr))
            except ssl.SSLError as e:
                logging.warning(t('ssl_handshake_failed', address=addr, error=e))
                sock.close()
                raise ConnectionError(t('ssl_handshake_failed', error=e))
            except socket.timeout:
                logging.warning(t('ssl_handshake_timeout', address=addr))
                sock.close()
                raise
            except Exception as e:
                logging.error(t('ssl_handshake_failed', address=addr, error=e))
                sock.close()
                raise
        
        return sock, addr
    
    def handle_error(self, request, client_address):
        """处理连接错误 - Handle connection errors"""
        # 记录错误但不退出 - Log error but don't exit
        logging.error(t('connection_error', address=client_address), exc_info=True)
    
    def shutdown(self):
        """关闭服务器 - Shutdown server"""
        super().shutdown()


class DualModeServer:
    """支持HTTP和HTTPS双模式的服务端，仅在有效证书时启用HTTPS - Server supporting both HTTP and HTTPS dual mode, HTTPS only enabled with valid certificates"""
    
    def __init__(self, host, http_port, https_port, request_handler, behaviour):
        self.host = host
        self.http_port = http_port
        self.https_port = https_port
        self.request_handler = request_handler
        self.behaviour = behaviour
        
        self.http_server = None
        self.https_server = None
        self.https_available = False
        
    def start(self):
        """启动HTTP和HTTPS服务器 - Start HTTP and HTTPS servers"""
        # 首先检查证书有效性 - First check certificate validity
        if check_ssl_certificate_valid():
            logging.info(t('dual_server_starting_https'))
            
            # 尝试启动HTTPS服务器 - Try to start HTTPS server
            try:
                self.https_server = IPPServer(
                    (self.host, self.https_port),
                    self.request_handler,
                    self.behaviour,
                    ssl_enabled=True
                )
                
                # 检查HTTPS是否成功启用 - Check if HTTPS successfully enabled
                if self.https_server.ssl_enabled:
                    https_thread = threading.Thread(
                        target=self.https_server.serve_forever,
                        daemon=True,
                        name=f"HTTPS-Server-{self.https_port}"
                    )
                    https_thread.start()
                    self.https_available = True
                    logging.info(t('dual_server_https_started', host=self.host, port=self.https_port))
                else:
                    logging.warning(t('dual_server_https_failed'))
                    self.https_server = None
                    
            except Exception as e:
                logging.error(t('dual_server_https_failed', error=e))
                self.https_available = False
        else:
            logging.warning(t('certificate_validation_failed'))
            self.https_available = False
        
        # 启动HTTP服务器 - Start HTTP server
        try:
            self.http_server = IPPServer(
                (self.host, self.http_port),
                self.request_handler,
                self.behaviour,
                ssl_enabled=False
            )
            
            http_thread = threading.Thread(
                target=self.http_server.serve_forever,
                daemon=True,
                name=f"HTTP-Server-{self.http_port}"
            )
            http_thread.start()
            
            if self.https_available:
                logging.info(t('dual_server_http_started', host=self.host, port=self.http_port))
                logging.info(t('use_https_for_secure_printing', host=self.host, port=self.https_port))
            else:
                logging.info(t('dual_server_http_started', host=self.host, port=self.http_port))
                logging.info(t('https_unavailable_http_only'))
                
        except Exception as e:
            logging.error(t('dual_server_http_failed', error=e))
            raise
    
    def shutdown(self):
        """关闭服务器 - Shutdown servers"""
        logging.info(t('shutting_down_servers'))
        if self.http_server:
            self.http_server.shutdown()
            logging.info(t('http_server_stopped'))
        if self.https_server:
            self.https_server.shutdown()
            logging.info(t('https_server_stopped'))
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()


def wait_until_ctrl_c():
    try:
        while True:
            time.sleep(300)
    except KeyboardInterrupt:
        return


def run_server(server):
    logging.info(t('listening_on', address=server.server_address))
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    wait_until_ctrl_c()
    logging.info(t('ready_to_shut_down'))
    server.shutdown()


def run_dual_mode_server(dual_server):
    """运行双模式服务器 - Run dual mode server"""
    dual_server.start()
    wait_until_ctrl_c()
    logging.info(t('ready_to_shut_down'))
    dual_server.shutdown()