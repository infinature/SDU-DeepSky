import requests
import os
import csv

# J-PLUS DR3 Graphic Image 文件下载的基础URL
BASE_URL = "https://archive.cefca.es/catalogues/vo/siap/jplus-dr3/get_graphic_image"

def get_file_extension_from_content_type(content_type):
    """根据Content-Type推断文件扩展名"""
    if not content_type:
        return ".jpg" # 默认
    if "jpeg" in content_type or "jpg" in content_type:
        return ".jpg"
    if "png" in content_type:
        return ".png"
    if "gif" in content_type:
        return ".gif"
    # 可以根据需要添加更多类型
    return ".jpg" # 默认回退

def download_jplus_graphic_image(session, image_id, output_directory="."):
    """
    从 J-PLUS DR3 存档下载指定的图形图像。

    参数:
    session (requests.Session): 用于发出请求的会话对象。
    image_id (str or int): 图像的唯一ID (对应URL中的id参数，即TILE_ID)。
    output_directory (str): 下载文件保存的目录。默认为当前目录。
    """
    params = {
        "id": image_id,
        "band": "RGB" # 固定参数
    }
    response = None
    try:
        response = session.get(BASE_URL, params=params, stream=True, timeout=(10, 60)) 
        response.raise_for_status()

        content_type = response.headers.get('content-type')
        extension = get_file_extension_from_content_type(content_type)
        
        filename = f"jplus_graphic_id{image_id}_RGB{extension}"
        filepath = os.path.join(output_directory, filename)

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return filepath

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误下载 Graphic Image ID {image_id}: {http_err}")
        if response is not None:
             print(f"  请求URL: {response.url}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求错误下载 Graphic Image ID {image_id}: {req_err}")
    except Exception as e:
        print(f"下载 Graphic Image ID {image_id} 时发生未知错误: {e}")
    finally:
        if response:
            response.close()
    return None

if __name__ == "__main__":
    csv_file_path = "object.csv"
    download_directory = "jplus_graphic_images" 
    
    print(f"准备从 {csv_file_path} 读取TILE_ID列表，下载RGB图形图像至 {download_directory}/")

    headers = []
    total_data_rows_read = 0
    successful_downloads = 0
    failed_downloads = 0
    
    session = requests.Session()

    try:
        with open(csv_file_path, mode='r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)

            try:
                header_row_from_reader = next(reader)
                headers = [header.strip().strip('"').strip() for header in header_row_from_reader]
                if not headers:
                    print("错误: 解析后的表头为空。脚本将退出。")
                    exit()
                print(f"CSV 表头解析完成，共 {len(headers)} 个字段。")
            except StopIteration:
                print(f"错误: CSV文件 {csv_file_path} 为空或无法读取表头行。脚本将退出。")
                exit()
            except Exception as e:
                print(f"读取或解析表头时发生错误: {e}。脚本将退出。")
                exit()

            required_col = "TILE_ID"
            if required_col not in headers:
                print(f"错误: 表头中缺少下载所需的关键列: '{required_col}'。脚本将退出。")
                exit()

            print("\n开始下载RGB图形图像...")
            for row_number, data_row in enumerate(reader, 1):
                total_data_rows_read += 1

                if len(data_row) != len(headers):
                    print(f"警告 (数据行 {row_number}): 字段数 ({len(data_row)}) 与表头字段数 ({len(headers)}) 不匹配。跳过此行。")
                    failed_downloads +=1
                    continue

                try:
                    row_dict = dict(zip(headers, data_row))
                    tile_id = row_dict.get(required_col)
                                        
                    if not tile_id:
                        print(f"警告 (数据行 {row_number}): 关键列 '{required_col}' 的值为空。跳过此行。")
                        failed_downloads +=1
                        continue
                    
                    print(f"处理行 {row_number}: 下载 Graphic Image for TILE_ID={tile_id}, band=RGB")
                                        
                    downloaded_file = download_jplus_graphic_image(
                        session, 
                        tile_id, 
                        output_directory=download_directory
                    )

                    if downloaded_file:
                        print(f"  成功: {os.path.basename(downloaded_file)}")
                        successful_downloads += 1
                    else:
                        print(f"  失败: Graphic Image for TILE_ID={tile_id}, band=RGB")
                        failed_downloads += 1

                except Exception as e_proc:
                    print(f"处理数据行 {row_number} (TILE_ID={row_dict.get(required_col, 'N/A')}) 时发生错误: {e_proc}。跳过此行。")
                    failed_downloads +=1
            
            print("\n--- 图形图像下载摘要 ---")
            print(f"总共处理的数据行数: {total_data_rows_read}")
            print(f"成功下载的文件数: {successful_downloads}")
            print(f"失败/跳过的下载数: {failed_downloads}")

    except FileNotFoundError:
        print(f"错误: CSV文件 {csv_file_path} 未找到。")
    except Exception as e:
        print(f"处理CSV或下载过程中发生未知错误: {e}")
    finally:
        if session:
            session.close()

    print("\n脚本执行完毕。") 