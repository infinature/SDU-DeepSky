import requests
import os
import csv

# J-PLUS DR3 PSF by Position 文件下载的基础URL
BASE_URL = "https://archive.cefca.es/catalogues/vo/siap/jplus-dr3/get_psf_by_position"


def download_jplus_psf_by_position(session, image_id, ra, dec, filter_code, output_directory="."):
    """
    从 J-PLUS DR3 存档下载指定位置的PSF文件。

    参数:
    session (requests.Session): 用于发出请求的会话对象。
    image_id (str or int): 图像的唯一ID (对应URL中的id参数，即TILE_ID)。
    ra (str or float): PSF计算位置的赤经 (对应URL中的ra参数)。
    dec (str or float): PSF计算位置的赤纬 (对应URL中的dec参数)。
    filter_code (str or int): 滤光片的编号或代码 (对应URL中的filter参数)。
    output_directory (str): 下载文件保存的目录。默认为当前目录。
    """
    params = {
        "id": image_id,
        "ra": ra,
        "dec": dec,
        "filter": filter_code
    }
    response = None
    try:
        response = session.get(BASE_URL, params=params, stream=True, timeout=(10, 60))
        response.raise_for_status()

        # 清理RA和DEC用于文件名，替换点号
        ra_fn = str(ra).replace('.', 'p')
        dec_fn = str(dec).replace('.', 'p').replace('-', 'm')  # 处理负号
        filename = f"jplus_psf_pos_id{image_id}_ra{ra_fn}_dec{dec_fn}_filter{filter_code}.psf"
        filepath = os.path.join(output_directory, filename)

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return filepath

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误下载 PSF by Pos (ID {image_id}, RA {ra}, Dec {dec}, Filter {filter_code}): {http_err}")
        if response is not None:
            print(f"  请求URL: {response.url}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求错误下载 PSF by Pos (ID {image_id}, RA {ra}, Dec {dec}, Filter {filter_code}): {req_err}")
    except Exception as e:
        print(f"下载 PSF by Pos (ID {image_id}, RA {ra}, Dec {dec}, Filter {filter_code}) 时发生未知错误: {e}")
    finally:
        if response:
            response.close()
    return None


if __name__ == "__main__":
    csv_file_path = "test2.csv"
    download_directory = "jplus_psf_by_position_data"

    print(f"准备从 {csv_file_path} 读取参数，下载PSF by Position文件至 {download_directory}/")

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

            required_cols = ["TILE_ID", "RA", "DEC", "FILTER_ID"]
            missing_cols = [col for col in required_cols if col not in headers]
            if missing_cols:
                print(f"错误: 表头中缺少下载所需的关键列: {missing_cols}。脚本将退出。")
                exit()

            print("\n开始下载PSF by Position文件...")
            for row_number, data_row in enumerate(reader, 1):
                total_data_rows_read += 1

                if len(data_row) != len(headers):
                    print(
                        f"警告 (数据行 {row_number}): 字段数 ({len(data_row)}) 与表头字段数 ({len(headers)}) 不匹配。跳过此行。")
                    failed_downloads += 1
                    continue

                try:
                    row_dict = dict(zip(headers, data_row))
                    tile_id = row_dict.get("TILE_ID")
                    ra_val = row_dict.get("RA")
                    dec_val = row_dict.get("DEC")
                    filter_id_val = row_dict.get("FILTER_ID")

                    if not all([tile_id, ra_val, dec_val, filter_id_val]):
                        print(
                            f"警告 (数据行 {row_number}): 缺少 TILE_ID, RA, DEC, 或 FILTER_ID 中的一个或多个值。跳过此行。")
                        failed_downloads += 1
                        continue

                    print(
                        f"处理行 {row_number}: 下载 PSF for TILE_ID={tile_id}, RA={ra_val}, Dec={dec_val}, Filter={filter_id_val}")

                    downloaded_file = download_jplus_psf_by_position(
                        session,
                        tile_id,
                        ra_val,
                        dec_val,
                        filter_id_val,
                        output_directory=download_directory
                    )

                    if downloaded_file:
                        print(f"  成功: {os.path.basename(downloaded_file)}")
                        successful_downloads += 1
                    else:
                        print(f"  失败: PSF for TILE_ID={tile_id}, RA={ra_val}, Dec={dec_val}, Filter={filter_id_val}")
                        failed_downloads += 1

                except Exception as e_proc:
                    print(f"处理数据行 {row_number} 时发生错误: {e_proc}。跳过此行。")
                    failed_downloads += 1

            print("\n--- PSF by Position 文件下载摘要 ---")
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