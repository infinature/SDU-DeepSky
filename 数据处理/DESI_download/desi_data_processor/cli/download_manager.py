"""
DESI数据批量下载管理工具

这个命令行工具允许用户通过CSV文件配置下载DESI官方的各类数据。
支持多种下载方式，包括HTTP直接下载、wget、AWS S3等。
"""

import os
import sys
import argparse
import pandas as pd
import logging
from pathlib import Path

# 将父目录添加到系统路径，确保能够导入desi_data_processor模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 导入下载工具
from desi_data_processor.utils.bulk_downloader import DESIBulkDownloader
try:
    from desi_data_processor.utils.aws_downloader import DESIS3Downloader
    aws_available = True
except ImportError:
    aws_available = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('desi_download_manager')


def parse_arguments():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        description='DESI数据批量下载管理工具',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='子命令', required=True)
    
    # 创建模板命令
    template_parser = subparsers.add_parser('create-template', help='创建CSV下载模板')
    template_parser.add_argument(
        '-o', '--output', 
        default='desi_download_template.csv',
        help='CSV模板输出路径'
    )
    
    # 下载命令
    download_parser = subparsers.add_parser('download', help='从CSV文件下载数据')
    download_parser.add_argument(
        '-c', '--csv', 
        required=True,
        help='CSV下载配置文件路径'
    )
    download_parser.add_argument(
        '-o', '--output-dir', 
        default='./desi_data',
        help='数据下载输出目录'
    )
    download_parser.add_argument(
        '-r', '--release', 
        default='dr1',
        help='DESI数据发布版本，如dr1、edr等'
    )
    download_parser.add_argument(
        '-w', '--workers', 
        type=int, 
        default=5,
        help='并行下载的最大工作线程数'
    )
    download_parser.add_argument(
        '--overwrite', 
        action='store_true',
        help='是否覆盖已存在的文件'
    )
    download_parser.add_argument(
        '--aws', 
        action='store_true',
        help='优先使用AWS S3下载（需要安装boto3）'
    )
    
    # 查询命令
    if aws_available:
        query_parser = subparsers.add_parser('query', help='查询DESI S3数据内容 (需要AWS支持)')
        query_parser.add_argument(
            '-p', '--prefix', 
            required=True,
            help='S3路径前缀，例如: spectro/redux/iron/zcatalog/'
        )
        query_parser.add_argument(
            '-r', '--release', 
            default='dr1',
            help='DESI数据发布版本，如dr1、edr等'
        )
        query_parser.add_argument(
            '-o', '--output', 
            help='将查询结果保存为CSV文件（可选）'
        )
    
    return parser.parse_args()


def create_template_command(args):
    """
    处理 'create-template' 命令
    """
    downloader = DESIBulkDownloader()
    downloader.create_csv_template(args.output)
    logger.info(f"CSV模板已创建: {args.output}")


def download_command(args):
    """
    处理 'download' 命令
    """
    if not os.path.exists(args.csv):
        logger.error(f"找不到CSV文件: {args.csv}")
        return 1
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.aws:
        if not aws_available:
            logger.error("AWS S3支持不可用，请安装boto3: pip install boto3")
            return 1
        logger.info("使用AWS S3下载数据")
        s3_downloader = DESIS3Downloader(data_release=args.release, output_dir=args.output_dir)
        if not s3_downloader.is_available():
            logger.error("AWS S3客户端初始化失败，请检查boto3安装和配置")
            return 1
        
        try:
            df = pd.read_csv(args.csv)
            success_count = 0
            fail_count = 0
            skipped_count = 0

            for _, row in tqdm(df.iterrows(), total=len(df), desc="AWS S3 下载进度"):
                s3_path = row['path']
                output_path_suffix = row.get('output_path', s3_path)
                full_output_path = os.path.join(args.output_dir, output_path_suffix)
                
                if os.path.exists(full_output_path) and not args.overwrite:
                    logger.info(f"文件已存在，跳过: {full_output_path}")
                    skipped_count += 1
                    continue

                success = s3_downloader.download_file(s3_path, full_output_path, overwrite=args.overwrite)
                if success:
                    success_count += 1
                else:
                    fail_count += 1
            
            logger.info(f"AWS S3下载完成: 成功 {success_count}, 失败 {fail_count}, 跳过 {skipped_count}")
            return 0 if fail_count == 0 else 1
        except Exception as e:
            logger.error(f"AWS S3下载过程中出错: {e}")
            return 1
    else:
        logger.info("使用HTTP/wget下载数据")
        downloader = DESIBulkDownloader(
            data_release=args.release,
            output_dir=args.output_dir,
            max_workers=args.workers
        )
        try:
            tasks = downloader.process_csv(args.csv)
            logger.info(f"从CSV文件中读取了 {len(tasks)} 个下载任务")
            results = downloader.download_all(tasks, overwrite=args.overwrite)
            if results['failed'] > 0:
                logger.warning(f"部分下载失败: {results['failed']} 个文件下载失败")
                return 1
            return 0
        except Exception as e:
            logger.error(f"HTTP/wget下载过程中出错: {e}")
            return 1


def query_s3_command(args):
    """
    处理 'query' 命令
    """
    if not aws_available:
        logger.error("AWS S3支持不可用，请安装boto3: pip install boto3")
        return 1
    
    s3_downloader = DESIS3Downloader(data_release=args.release)
    if not s3_downloader.is_available():
        logger.error("AWS S3客户端初始化失败，请检查boto3安装和配置")
        return 1
    
    logger.info(f"正在查询S3路径前缀: {args.prefix} (数据版本: {args.release})")
    objects = s3_downloader.list_objects(args.prefix)
    
    if not objects:
        logger.warning(f"在S3中未找到匹配前缀的对象: {args.prefix}")
        return 1
    
    print(f"在S3中找到 {len(objects)} 个对象 (最多显示前20个):")
    for i, obj in enumerate(objects[:20]):
        print(f"  {i+1}. {obj['key']} (大小: {obj['size']} bytes, 修改时间: {obj['last_modified']})")
    
    if len(objects) > 20:
        print(f"  ... 还有 {len(objects) - 20} 个对象未显示")
    
    if args.output:
        df_data = []
        for obj in objects:
            # 尝试从路径猜测数据类型
            path_parts = obj['key'].split('/')
            data_type = 'unknown'
            if 'zcatalog' in path_parts or 'zall' in obj['key']:
                data_type = 'zcat'
            elif 'spectra' in path_parts:
                data_type = 'spectra'
            elif 'healpix' in path_parts:
                data_type = 'healpix'
            elif 'tiles' in path_parts:
                data_type = 'tile'
            elif 'target' in path_parts:
                 data_type = 'target'
            elif 'redux' in path_parts and 'exposures' in path_parts:
                data_type = 'exposure'
            
            df_data.append({
                'data_type': data_type,
                'path': obj['key'], # S3路径，相对于DR
                'output_path': obj['key'], # 建议的本地相对路径
                'download_method': 'aws', # 建议使用AWS下载
                'size_bytes': obj['size'],
                'last_modified': obj['last_modified']
            })
        
        df = pd.DataFrame(df_data)
        try:
            df.to_csv(args.output, index=False)
            logger.info(f"查询结果已保存到CSV文件: {args.output}")
            print(f"\n提示: 您可以将此CSV文件用于 'download' 命令 (可能需要调整 'data_type' 和 'output_path')")
        except Exception as e:
            logger.error(f"保存查询结果到CSV时出错: {e}")
            return 1
    
    return 0


def main():
    """
    主函数，解析参数并执行相应命令
    """
    args = parse_arguments()
    
    if args.command == 'create-template':
        return create_template_command(args)
    elif args.command == 'download':
        return download_command(args)
    elif args.command == 'query':
        if not aws_available:
             logger.error("查询功能需要AWS支持，但boto3未安装或不可用。")
             print("请尝试 'pip install boto3' 并确保AWS凭证已配置。")
             return 1
        return query_s3_command(args)
    else:
        # argparse的required=True应该能处理未指定命令的情况
        # 但为了保险起见，保留一个默认的错误处理
        logger.error("无效的命令。请使用 --help 查看可用命令。")
        return 1

if __name__ == '__main__':
    # 确保脚本从项目根目录运行时，desi_data_processor能被正确导入
    # (已在文件顶部通过sys.path.insert处理)
    sys.exit(main())
