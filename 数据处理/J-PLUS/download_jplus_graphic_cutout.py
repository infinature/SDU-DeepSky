import requests
import os
import csv

# J-PLUS DR3 Graphic Cutout Image 文件下载的基础URL
BASE_URL = "https://archive.cefca.es/catalogues/vo/siap/jplus-dr3/get_graphic_cutout"

def get_file_extension_from_content_type(content_type):
    """根据Content-Type推断文件扩展名"""
    if not content_type:
        return ".png" # 默认 PNG as per user request context
    if "png" in content_type:
        return ".png"
    if "jpeg" in content_type or "jpg" in content_type:
        return ".jpg"
    if "gif" in content_type:
        return ".gif"
    return ".png" # 默认回退 PNG

def download_jplus_graphic_cutout(session, ra, dec, filter_code, output_directory=".", 
                                  band="RGB", angular_width=0.1, angular_height=0.1, 
                                  pixel_sizex=128, pixel_sizey=128):
    """
    从 J-PLUS DR3 存档下载指定的图形PNG图像切割。

    参数:
    session (requests.Session): 用于发出请求的会话对象。
    ra (str or float): 切图中心的赤经。
    dec (str or float): 切图中心的赤纬。
    filter_code (str or int): 滤光片的编号或代码。
    output_directory (str): 下载文件保存的目录。
    band (str): 波段，默认为RGB。
    angular_width (float): 切图的角宽度 (天空中的大小，例如度)。
    angular_height (float): 切图的角高度。
    pixel_sizex (int): 输出图像的像素宽度。
    pixel_sizey (int): 输出图像的像素高度。
    """
    params = {
        "band": band,
        "ra": ra,
        "dec": dec,
        "width": angular_width,
        "height": angular_height,
        "sizex": pixel_sizex,
        "sizey": pixel_sizey,
        "filter": filter_code
    }
    response = None
    try:
        response = session.get(BASE_URL, params=params, stream=True, timeout=(10, 60)) 
        response.raise_for_status()

        content_type = response.headers.get('content-type')
        extension = get_file_extension_from_content_type(content_type)
        
        # 清理RA和DEC用于文件名
        ra_fn = str(ra).replace('.', 'p')
        dec_fn = str(dec).replace('.', 'p').replace('-', 'm')

        filename = f"jplus_graphic_cutout_ra{ra_fn}_dec{dec_fn}_filter{filter_code}_size{pixel_sizex}x{pixel_sizey}_{band}{extension}"
        filepath = os.path.join(output_directory, filename)

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return filepath

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误下载 Graphic Cutout (RA {ra}, Dec {dec}, Filter {filter_code}): {http_err}")
        if response is not None:
             print(f"  请求URL: {response.url}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求错误下载 Graphic Cutout (RA {ra}, Dec {dec}, Filter {filter_code}): {req_err}")
    except Exception as e:
        print(f"下载 Graphic Cutout (RA {ra}, Dec {dec}, Filter {filter_code}) 时发生未知错误: {e}")
    finally:
        if response:
            response.close()
    return None

if __name__ == "__main__":
    csv_file_path = "object.csv"
    download_directory = "jplus_graphic_cutouts_data" 
    
    print(f"准备从 {csv_file_path} 读取参数，下载128x128 RGB图形PNG图像切割至 {download_directory}/")

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

            required_cols = ["RA", "DEC", "FILTER_ID"] # TILE_ID is not in the example URL for this service
            missing_cols = [col for col in required_cols if col not in headers]
            if missing_cols:
                print(f"错误: 表头中缺少下载所需的关键列: {missing_cols}。脚本将退出。")
                exit()

            print("\n开始下载RGB图形PNG图像切割...")
            for row_number, data_row in enumerate(reader, 1):
                total_data_rows_read += 1

                if len(data_row) != len(headers):
                    print(f"警告 (数据行 {row_number}): 字段数 ({len(data_row)}) 与表头字段数 ({len(headers)}) 不匹配。跳过此行。")
                    failed_downloads +=1
                    continue

                try:
                    row_dict = dict(zip(headers, data_row))
                    ra_val = row_dict.get("RA")
                    dec_val = row_dict.get("DEC")
                    filter_id_val = row_dict.get("FILTER_ID")
                                        
                    if not all([ra_val, dec_val, filter_id_val]):
                        print(f"警告 (数据行 {row_number}): 缺少 RA, DEC, 或 FILTER_ID 中的一个或多个值。跳过此行。")
                        failed_downloads +=1
                        continue
                    
                    print(f"处理行 {row_number}: 下载 Graphic Cutout RA={ra_val}, Dec={dec_val}, Filter={filter_id_val}")
                                        
                    # 使用默认参数调用下载函数: band="RGB", angular_width=0.1, angular_height=0.1, pixel_sizex=128, pixel_sizey=128
                    downloaded_file = download_jplus_graphic_cutout(
                        session, 
                        ra_val,
                        dec_val,
                        filter_id_val,
                        output_directory=download_directory
                    )

                    if downloaded_file:
                        print(f"  成功: {os.path.basename(downloaded_file)}")
                        successful_downloads += 1
                    else:
                        print(f"  失败: Graphic Cutout RA={ra_val}, Dec={dec_val}, Filter={filter_id_val}")
                        failed_downloads += 1

                except Exception as e_proc:
                    print(f"处理数据行 {row_number} 时发生错误: {e_proc}。跳过此行。")
                    failed_downloads +=1
            
            print("\n--- 图形PNG图像切割下载摘要 ---")
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