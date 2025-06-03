import requests
import os
import csv

# J-PLUS DR3 FITS CUTOUT图像下载的基础URL
BASE_URL = "https://archive.cefca.es/catalogues/vo/siap/jplus-dr3/get_fits_cutout"

def download_jplus_cutout(session, image_id, ra, dec, filter_code, 
                            output_directory=".", cutout_width=0.1, cutout_height=0.1, include_weight=0):
    """
    从 J-PLUS DR3 存档下载指定的FITS CUTOUT图像。

    参数:
    session (requests.Session): 用于发出请求的会话对象。
    image_id (str or int): 图像的唯一ID (对应URL中的id参数)。
    ra (str or float): 切图中心的赤经 (对应URL中的ra参数)。
    dec (str or float): 切图中心的赤纬 (对应URL中的dec参数)。
    filter_code (str or int): 滤光片的编号或代码 (对应URL中的filter参数)。
    output_directory (str): 下载文件保存的目录。默认为当前目录。
    cutout_width (float): 切图宽度 (对应URL中的width参数，默认为0.1度)。
    cutout_height (float): 切图高度 (对应URL中的height参数，默认为0.1度)。
    include_weight (int): 是否包含权重图 (对应URL中的weight参数，0为false, 1为true，默认为0)。
    """
    params = {
        "id": image_id,
        "ra": ra,
        "dec": dec,
        "width": cutout_width,
        "height": cutout_height,
        "filter": filter_code,
        "weight": include_weight
    }
    response = None 
    try:
        # 增加读取超时到60秒, 连接超时10秒
        response = session.get(BASE_URL, params=params, stream=True, timeout=(10, 60)) 
        response.raise_for_status()  

        # 清理RA和DEC用于文件名，替换点号
        ra_fn = str(ra).replace('.', 'p')
        dec_fn = str(dec).replace('.', 'p').replace('-', 'm') # 处理负号
        filename = f"jplus_cutout_id{image_id}_ra{ra_fn}_dec{dec_fn}_filter{filter_code}_w{str(cutout_width).replace('.','p')}_h{str(cutout_height).replace('.','p')}.fits"
        filepath = os.path.join(output_directory, filename)

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            # print(f"创建目录: {output_directory}") # 可以按需取消注释

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # print(f"成功下载CUTOUT图像: {filepath}") # 更改为更简洁的成功信息
        return filepath

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误下载 ID {image_id}, RA {ra}, DEC {dec}: {http_err}")
        if response is not None:
             print(f"  请求URL: {response.url}")
             # print(f"响应内容: {response.text[:200]}...") # 按需调试
    except requests.exceptions.RequestException as req_err:
        print(f"请求错误下载 ID {image_id}, RA {ra}, DEC {dec}: {req_err}")
    except Exception as e:
        print(f"下载 ID {image_id}, RA {ra}, DEC {dec} 时发生未知错误: {e}")
    finally:
        if response:
            response.close() 
    return None

if __name__ == "__main__":
    csv_file_path = "object.csv"
    download_directory = "jplus_cutout_data" # 指定下载子目录
    
    print(f"准备从 {csv_file_path} 读取下载列表，保存至 {download_directory}/")

    headers = []
    total_data_rows_read = 0
    successful_downloads = 0
    failed_downloads = 0
    
    session = requests.Session() # 在循环外创建Session

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

            required_cols_for_download = ["TILE_ID", "FILTER_ID", "RA", "DEC"]
            missing_required_cols = [col for col in required_cols_for_download if col not in headers]
            if missing_required_cols:
                print(f"错误: 表头中缺少下载所需的关键列: {missing_required_cols}。脚本将退出。")
                exit()

            print("\n开始下载...")
            for row_number, data_row in enumerate(reader, 1):
                total_data_rows_read += 1

                if len(data_row) != len(headers):
                    print(f"警告 (数据行 {row_number}): 字段数 ({len(data_row)}) 与表头字段数 ({len(headers)}) 不匹配。跳过此行。")
                    failed_downloads +=1
                    continue

                try:
                    row_dict = dict(zip(headers, data_row))
                    tile_id = row_dict.get("TILE_ID")
                    filter_id = row_dict.get("FILTER_ID")
                    ra_val = row_dict.get("RA")
                    dec_val = row_dict.get("DEC")
                    
                    if not all([tile_id, filter_id, ra_val, dec_val]):
                        print(f"警告 (数据行 {row_number}): 缺少 TILE_ID, FILTER_ID, RA, 或 DEC 中的一个或多个值。跳过此行。")
                        print(f"  提取的值: TILE_ID='{tile_id}', FILTER_ID='{filter_id}', RA='{ra_val}', DEC='{dec_val}'")
                        failed_downloads +=1
                        continue
                    
                    print(f"处理行 {row_number}: 下载 TILE_ID={tile_id}, RA={ra_val}, DEC={dec_val}, FILTER={filter_id}")
                    
                    # 使用默认值调用下载函数
                    downloaded_file = download_jplus_cutout(
                        session, 
                        tile_id, 
                        ra_val, 
                        dec_val, 
                        filter_id, 
                        output_directory=download_directory
                        # cutout_width, cutout_height, include_weight 使用函数定义的默认值
                    )

                    if downloaded_file:
                        print(f"  成功: {os.path.basename(downloaded_file)}")
                        successful_downloads += 1
                    else:
                        # 错误信息已在 download_jplus_cutout 函数内部打印
                        print(f"  失败: TILE_ID={tile_id}, RA={ra_val}, DEC={dec_val}, FILTER={filter_id}")
                        failed_downloads += 1

                except Exception as e_proc:
                    print(f"处理数据行 {row_number} 时发生错误: {e_proc}。跳过此行。")
                    failed_downloads +=1
            
            print("\n--- 下载摘要 ---")
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
            # print("Requests session closed.") # 可以按需取消注释

    print("\n脚本执行完毕。") 