"""
数据下载相关的辅助函数。
"""

import requests
import os
from tqdm import tqdm # 用于显示下载进度条

def download_file(url, local_path, overwrite=False):
    """
    从给定的URL下载文件到本地路径。

    参数:
        url (str): 要下载的文件的URL。
        local_path (str): 文件保存的本地路径（包括文件名）。
        overwrite (bool): 如果本地文件已存在，是否覆盖。

    返回:
        bool: 如果下载成功则返回True，否则返回False。
    """
    if os.path.exists(local_path) and not overwrite:
        print(f"文件已存在: {local_path}。跳过下载。")
        return True

    # 确保目录存在
    local_dir = os.path.dirname(local_path)
    if local_dir and not os.path.exists(local_dir):
        try:
            os.makedirs(local_dir)
            print(f"创建目录: {local_dir}")
        except OSError as e:
            print(f"创建目录失败 {local_dir}: {e}")
            return False
    
    try:
        print(f"开始下载: {url} -> {local_path}")
        response = requests.get(url, stream=True, timeout=300) # MODIFIED: Increased timeout to 300 seconds
        response.raise_for_status()  # 如果请求失败 (状态码 4xx or 5xx) 则抛出HTTPError

        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 # 1 Kilobyte

        with open(local_path, 'wb') as f, tqdm(
            desc=os.path.basename(local_path),
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=block_size):
                size = f.write(data)
                bar.update(size)
        
        if total_size != 0 and bar.n != total_size:
            print(f"错误: 下载大小与预期不符 ({bar.n} / {total_size} bytes)")
            # 可以选择删除不完整的文件
            # os.remove(local_path)
            return False
            
        print(f"下载成功: {local_path}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"下载文件失败 {url}: {e}")
        if os.path.exists(local_path): # 如果下载过程中断，可能留下不完整文件
            try:
                os.remove(local_path)
                print(f"已删除不完整的文件: {local_path}")
            except OSError as oe:
                print(f"删除不完整文件失败 {local_path}: {oe}")
        return False
    except Exception as e:
        print(f"下载过程中发生未知错误 {url}: {e}")
        return False


if __name__ == '__main__':
    print("download_utils.py 包含文件下载的辅助函数。")

    # 示例：下载一个小的测试文件
    # 注意：这个URL是一个示例，可能会失效。请替换为有效的测试文件URL。
    test_url = 'https://data.desi.lbl.gov/public/dr1/CONTRIBUTING.md' # 一个小的Markdown文件作为测试
    # test_url = 'https://data.desi.lbl.gov/public/dr1/spectro/redux/iron/zcatalog/v1/zall-pix-iron.fits' # 这个文件很大，测试会很久
    
    # 将文件保存在脚本所在目录的 'temp_downloads' 子目录中
    script_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(os.path.dirname(script_dir), 'temp_downloads') # desi_data_processor/temp_downloads
    # download_dir = os.path.join(script_dir, 'temp_downloads') # desi_data_processor/utils/temp_downloads
    
    file_name = os.path.basename(test_url)
    local_file_path = os.path.join(download_dir, file_name)

    print(f"\n测试下载 '{test_url}' 到 '{local_file_path}'")
    success = download_file(test_url, local_file_path, overwrite=True)

    if success:
        print(f"测试文件下载成功: {local_file_path}")
        # 可以选择删除测试文件
        # os.remove(local_file_path)
        # if not os.listdir(download_dir): # 如果目录为空则删除
        #     os.rmdir(download_dir)
    else:
        print(f"测试文件下载失败。")
    
    print("\n再次尝试下载 (应该会跳过，因为文件已存在且overwrite=False):")
    download_file(test_url, local_file_path, overwrite=False)
