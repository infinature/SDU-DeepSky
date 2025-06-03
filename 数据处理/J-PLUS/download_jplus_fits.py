import requests
import os
import csv

# J-PLUS DR3 FITS图像下载的基础URL
BASE_URL = "https://archive.cefca.es/catalogues/vo/siap/jplus-dr3/get_fits"

def download_jplus_fits(session, image_id, filter_code, output_directory="."):
    """
    从 J-PLUS DR3 存档下载指定的FITS图像。

    参数:
    session (requests.Session): 用于发出请求的会话对象。
    image_id (str or int): 图像的唯一ID。
    filter_code (str or int): 滤光片的编号或代码。
    output_directory (str): 下载文件保存的目录。默认为当前目录。
    """
    params = {
        "id": image_id,
        "filter": filter_code
    }
    response = None # 初始化response变量
    try:
        # 为请求添加超时 (例如：连接超时10秒，读取超时30秒)
        response = session.get(BASE_URL, params=params, stream=True, timeout=(10, 30))
        response.raise_for_status()  # 如果发生HTTP错误 (4xx or 5xx)，则抛出异常

        filename = f"jplus_id{image_id}_filter{filter_code}.fits"
        filepath = os.path.join(output_directory, filename)

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            print(f"创建目录: {output_directory}")

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"成功下载图像: {filepath}")
        return filepath

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误: {http_err}")
        print(f"请求URL: {response.url if response else BASE_URL}")
        if response is not None:
            print(f"响应内容: {response.text[:500]}...")
    except requests.exceptions.RequestException as req_err:
        print(f"请求错误: {req_err}")
    except Exception as e:
        print(f"发生未知错误: {e}")
    finally:
        if response:
            response.close() # 显式关闭response流
    return None

if __name__ == "__main__":
    csv_file_path = "object.csv"
    download_directory = "jplus_data_from_csv"

    print(f"准备从 {csv_file_path} 读取列表以下载FITS文件...") # 更新打印信息

    session = requests.Session() # 创建Session对象
    try:
        with open(csv_file_path, mode='r', newline='', encoding='utf-8-sig') as csvfile:
            header_line = csvfile.readline().strip()
            if not header_line:
                print(f"错误: CSV文件 {csv_file_path} 为空或表头行无法读取。")
                exit()
            
            headers = [header.strip().strip('"').strip() for header in header_line.split(',')]

            if "TILE_ID" not in headers or "FILTER_ID" not in headers:
                print(f"错误: 表头必须包含 'TILE_ID' 和 'FILTER_ID'。检测到的表头: {headers}")
                exit()

            reader = csv.reader(csvfile)
            data_rows_read = 0
            successful_downloads = 0
            for row_number, data_row in enumerate(reader, 1):
                data_rows_read += 1
                if len(data_row) == len(headers):
                    row_dict = dict(zip(headers, data_row))
                    tile_id = row_dict.get("TILE_ID")
                    filter_id = row_dict.get("FILTER_ID")

                    if not tile_id or not filter_id:
                        print(f"跳过数据行 {row_number}: TILE_ID 或 FILTER_ID 为空或无效。TILE_ID='{tile_id}', FILTER_ID='{filter_id}'")
                        continue
                    
                    print(f"\n准备下载FITS图像 TILE_ID: {tile_id}, FILTER_ID: {filter_id} (来自CSV数据行 {row_number})") # 更新打印信息
                    downloaded_file = download_jplus_fits(session, tile_id, filter_id, download_directory) # 传递session
                    if downloaded_file:
                        print(f"文件已保存至: {os.path.abspath(downloaded_file)}")
                        successful_downloads +=1
                    else:
                        print(f"下载FITS TILE_ID: {tile_id}, FILTER_ID: {filter_id} 失败。") # 更新打印信息
                else:
                    print(f"警告: CSV数据行 {row_number} 的字段数 ({len(data_row)}) 与表头字段数 ({len(headers)}) 不匹配。跳过此行: {data_row}")
            
            if data_rows_read == 0:
                print("未从CSV文件中读取到任何数据行 (表头之后)。")
            elif successful_downloads > 0 :
                 print(f"\n成功下载 {successful_downloads} 个FITS文件。") # 更新打印信息
            else:
                print("\n没有FITS文件被成功下载。") # 更新打印信息

    except FileNotFoundError:
        print(f"错误: CSV文件 {csv_file_path} 未找到。")
    except Exception as e:
        print(f"处理CSV文件时发生错误: {e}")
    finally:
        if session: # 确保在脚本末尾关闭session
            print("正在关闭网络会话...")
            session.close()

    print("\n脚本执行完毕。") 