#!/usr/bin/env python3

import argparse
import logging
import importlib
import sys
import os.path

# 添加父目录到路径 - Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ippserver import behaviour
from ippserver.pc2paper import Pc2Paper
from ippserver.server import run_server, IPPServer, IPPRequestHandler, DualModeServer, run_dual_mode_server, check_ssl_certificate_valid
from ippserver.mdns import MDNSBroadcaster

# 导入默认配置 - Import default configuration
from ippserver import (
    DEFAULT_PRINTER_NAME, DEFAULT_PRINTER_DESCRIPTION, DEFAULT_PRINTER_LOCATION,
    DEFAULT_PRINTER_URI, DEFAULT_PRINTER_UUID, DEFAULT_HOST, DEFAULT_PORT,
    DEFAULT_SSL_PORT, DEFAULT_MANUFACTURER, DEFAULT_MODEL, DEFAULT_SERIAL_NUMBER
)

# 导入翻译模块 - Import translation module
try:
    from ippserver.translations import t, set_language, LANG_ZH, LANG_EN # type: ignore
except ImportError:
    # 如果翻译模块不存在，创建一个简单的替代函数 - If translation module doesn't exist, create a simple fallback
    def t(key, **kwargs):
        return key
    def set_language(lang_code):
        pass
    LANG_ZH = 'zh'
    LANG_EN = 'en'


def filter_printer_info(printer_info):
    """过滤打印机信息，只保留需要的字段 - Filter printer information, keep only necessary fields"""
    return {k: v for k, v in printer_info.items() 
            if k in ['uri', 'name', 'description', 'location', 'printer_uuid']}


def parse_args(args=None):
    # 创建主解析器 - Create main parser
    parser = argparse.ArgumentParser(description='IPP服务器 - IPP Server')
    parser.add_argument('-v', '--verbose', action='count', help='添加调试信息 - Add debugging')
    
    # 语言参数 - Language parameter
    parser.add_argument('--lang', type=str, choices=['zh', 'en'], default='zh',
                       help='设置语言: zh为中文, en为英文 - Set language: zh for Chinese, en for English')
    
    # 使用__init__.py中的默认值 - Use defaults from __init__.py
    parser.add_argument('-H', '--host', type=str, default=DEFAULT_HOST, 
                       metavar='HOST', help=f'监听地址 (默认: {DEFAULT_HOST}) - Address to listen on (default: {DEFAULT_HOST})')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, 
                       metavar='PORT', help=f'HTTP监听端口 (默认: {DEFAULT_PORT}) - HTTP port to listen on (default: {DEFAULT_PORT})')
    parser.add_argument('-P', '--ssl-port', type=int, default=DEFAULT_SSL_PORT, 
                       metavar='SSL_PORT', help=f'HTTPS监听端口 (默认: {DEFAULT_SSL_PORT}) - HTTPS port to listen on (default: {DEFAULT_SSL_PORT})')
    parser.add_argument('--no-ssl', action='store_true', default=False, 
                       help='禁用SSL/TLS支持（强制使用HTTP）- Disable SSL/TLS support (force HTTP only)')
    parser.add_argument('--no-mdns', action='store_true', default=False, 
                       help='禁用mDNS广播 - Disable mDNS broadcasting')
    
    # 使用__init__.py中的打印机默认值 - Use printer defaults from __init__.py
    parser.add_argument('-i', '--uri', type=str, default=DEFAULT_PRINTER_URI, 
                       metavar='URI', help=f'打印机URI (默认: {DEFAULT_PRINTER_URI}) - Printer URI (default: {DEFAULT_PRINTER_URI})')
    parser.add_argument('-u', '--uuid', type=str, default=DEFAULT_PRINTER_UUID, 
                       metavar='UUID', help=f'打印机UUID (默认: {DEFAULT_PRINTER_UUID}) - Printer UUID (default: {DEFAULT_PRINTER_UUID})')
    parser.add_argument('-n', '--name', type=str, default=DEFAULT_PRINTER_NAME, 
                       metavar='NAME', help=f'打印机名称 (默认: {DEFAULT_PRINTER_NAME}) - Printer name (default: {DEFAULT_PRINTER_NAME})')
    parser.add_argument('-d', '--description', type=str, default=DEFAULT_PRINTER_DESCRIPTION, 
                       metavar='DESC', help=f'打印机描述 (默认: {DEFAULT_PRINTER_DESCRIPTION}) - Printer description (default: {DEFAULT_PRINTER_DESCRIPTION})')
    parser.add_argument('-l', '--location', type=str, default=DEFAULT_PRINTER_LOCATION, 
                       metavar='LOC', help=f'打印机位置 (默认: {DEFAULT_PRINTER_LOCATION}) - Printer location (default: {DEFAULT_PRINTER_LOCATION})')
    
    # 打印机硬件信息参数（新增）- Printer hardware information parameters (new)
    parser.add_argument('--manufacturer', type=str, default=DEFAULT_MANUFACTURER,
                       metavar='MANUFACTURER', help=f'打印机制造商 (默认: {DEFAULT_MANUFACTURER}) - Printer manufacturer (default: {DEFAULT_MANUFACTURER})')
    parser.add_argument('--model', type=str, default=DEFAULT_MODEL,
                       metavar='MODEL', help=f'打印机型号 (默认: {DEFAULT_MODEL}) - Printer model (default: {DEFAULT_MODEL})')
    parser.add_argument('--serial', type=str, default=DEFAULT_SERIAL_NUMBER,
                       metavar='SERIAL', help=f'打印机序列号 (默认: {DEFAULT_SERIAL_NUMBER}) - Printer serial number (default: {DEFAULT_SERIAL_NUMBER})')

    # 子命令解析器 - Subparsers for actions
    parser_action = parser.add_subparsers(help='操作 - Actions', dest='action')

    # save 命令 - save command
    parser_save = parser_action.add_parser('save', help='将打印作业保存到磁盘 - Write any print jobs to disk')
    parser_save.add_argument('directory', metavar='DIRECTORY', help='保存文件的目录 - Directory to save files into')

    # run 命令 - run command
    parser_command = parser_action.add_parser('run', help='接收到打印作业时运行命令 - Run a command when receiving a print job')
    parser_command.add_argument('command', nargs=argparse.REMAINDER, metavar='COMMAND', help='要运行的命令 - Command to run')
    parser_command.add_argument('--env', action='store_true', default=False, help="将作业属性存储在环境变量中 (IPP_JOB_ATTRIBUTES) - Store Job attributes in environment (IPP_JOB_ATTRIBUTES)")

    # saveandrun 命令 - saveandrun command
    parser_saverun = parser_action.add_parser('saveandrun', help='保存打印作业到磁盘然后运行命令 - Write any print jobs to disk and then run a command on them')
    parser_saverun.add_argument('--env', action='store_true', default=False, help="将作业属性存储在环境变量中 (IPP_JOB_ATTRIBUTES) - Store Job attributes in environment (IPP_JOB_ATTRIBUTES)")
    parser_saverun.add_argument('directory', metavar='DIRECTORY', help='保存文件的目录 - Directory to save files into')
    parser_saverun.add_argument('command', nargs=argparse.REMAINDER, metavar='COMMAND', help='要运行的命令（文件名将添加在末尾）- Command to run (the filename will be added at the end)')

    # reject 命令 - reject command
    parser_reject = parser_action.add_parser('reject', help='拒绝所有打印作业 - Respond to all print jobs with job-canceled-at-device')

    # pc2paper 命令 - pc2paper command
    parser_pc2paper = parser_action.add_parser('pc2paper', help='使用http://www.pc2paper.org/投递打印作业 - Post print jobs using http://www.pc2paper.org/')
    parser_pc2paper.add_argument('--config', metavar='CONFIG', help='包含发送地址的JSON配置文件 - File containing an address to send to, in json format')
    
    # load 命令 - load command
    parser_loader = parser_action.add_parser('load', help='加载自定义行为 - Load own behaviour')
    parser_loader.add_argument('path', nargs=1, metavar='PATH', help='实现行为的模块 - Module implementing behaviour')
    parser_loader.add_argument('command', nargs=argparse.REMAINDER, metavar='COMMAND', help='模块的参数 - Arguments for the module')

    return parser.parse_args(args)


def behaviour_from_parsed_args(args):
    # 创建打印机硬件信息字典 - Create printer hardware information dictionary
    printer_info = {
        'uri': args.uri,
        'name': args.name,
        'description': args.description,
        'location': args.location,
        'printer_uuid': args.uuid,
        'manufacturer': args.manufacturer,
        'model': args.model,
        'serial_number': args.serial
    }
    
    filtered_info = filter_printer_info(printer_info)
    
    if args.action == 'save':
        return behaviour.SaveFilePrinter(
            directory=args.directory,
            **filtered_info
        )
    if args.action == 'run':
        return behaviour.RunCommandPrinter(
            command=args.command,
            use_env=args.env,
            **filtered_info
        )
    if args.action == 'saveandrun':
        return behaviour.SaveAndRunPrinter(
            command=args.command,
            use_env=args.env,
            directory=args.directory,
            **filtered_info
        )
    if args.action == 'pc2paper':
        pc2paper_config = Pc2Paper.from_config_file(args.config)
        return behaviour.PostageServicePrinter(
            service_api=pc2paper_config,
            **filtered_info
        )
    if args.action == 'load':
        module_path = args.path[0]
        if '.' in module_path:
            module_name, class_name = module_path.rsplit(".", 1)
        else:
            module_name = module_path
            class_name = "Behaviour"
        module = importlib.import_module(module_name)
        return getattr(module, class_name)(*args.command)
    if args.action == 'reject':
        return behaviour.RejectAllPrinter(
            **filtered_info
        )

    raise RuntimeError(t('unknown_action', action=args.action))


def main(args=None):
    parsed_args = parse_args(args)
    
    # 检查是否有操作被指定 - Check if an action was specified
    if not parsed_args.action:
        print("错误: 必须指定一个操作 (save, run, saveandrun, reject, pc2paper, load)")
        print("Error: An action must be specified (save, run, saveandrun, reject, pc2paper, load)")
        return 1
    
    # 设置语言 - Set language
    set_language(parsed_args.lang)
    
    log_level = logging.DEBUG if parsed_args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    behaviour_obj = behaviour_from_parsed_args(parsed_args)
    
    # 检查是否强制禁用SSL - Check if SSL is forcibly disabled
    force_no_ssl = parsed_args.no_ssl
    
    # 检查SSL证书有效性 - Check SSL certificate validity
    ssl_valid = False
    if not force_no_ssl:
        ssl_valid = check_ssl_certificate_valid()
        if ssl_valid:
            logging.info(t('ssl_certificate_valid'))
        else:
            logging.warning(t('ssl_certificate_invalid'))
    
    # 创建mDNS广播器 - Create mDNS broadcaster
    mdns_broadcaster = None
    if not parsed_args.no_mdns:
        try:
            mdns_broadcaster = MDNSBroadcaster(
                printer_name=parsed_args.name,
                port=parsed_args.port,
                ssl_port=parsed_args.ssl_port,
                host=parsed_args.host,
                description=parsed_args.description,
                location=parsed_args.location,
                printer_uuid=parsed_args.uuid,
                ssl_enabled=ssl_valid and not force_no_ssl
            )
            
            # 设置硬件信息 - Set hardware information
            mdns_broadcaster.printer_manufacturer = parsed_args.manufacturer
            mdns_broadcaster.printer_model = parsed_args.model
            mdns_broadcaster.printer_serial_number = parsed_args.serial
            
            mdns_broadcaster.start()
            logging.info(t('mdns_broadcasting_started', name=parsed_args.name))
        except Exception as e:
            logging.error(t('mdns_broadcast_failed', error=str(e)))
    
    try:
        # 根据证书有效性决定启动模式 - Determine startup mode based on certificate validity
        if force_no_ssl or not ssl_valid:
            # 只启动HTTP服务器 - Start HTTP server only
            server = IPPServer(
                (parsed_args.host, parsed_args.port),
                IPPRequestHandler,
                behaviour_obj,
                ssl_enabled=False
            )
            
            if force_no_ssl:
                logging.info(t('http_only_mode_no_ssl', host=parsed_args.host, port=parsed_args.port))
            else:
                logging.info(t('http_only_mode', host=parsed_args.host, port=parsed_args.port))
            
            run_server(server)
        else:
            # 启动双模式服务器（HTTP + HTTPS）- Start dual mode server (HTTP + HTTPS)
            logging.info(t('dual_mode'))
            dual_server = DualModeServer(
                host=parsed_args.host,
                http_port=parsed_args.port,
                https_port=parsed_args.ssl_port,
                request_handler=IPPRequestHandler,
                behaviour=behaviour_obj
            )
            
            run_dual_mode_server(dual_server)
    finally:
        # 确保mDNS广播器被正确关闭 - Ensure mDNS broadcaster is properly closed
        if mdns_broadcaster:
            mdns_broadcaster.stop()
            logging.info(t('mdns_broadcasting_stopped'))


if __name__ == "__main__":
    main()