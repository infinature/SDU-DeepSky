from fastapi import FastAPI, File, UploadFile, Form, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool # 导入 run_in_threadpool
import os
import torch
from astropy.io import fits
from PIL import Image
import numpy as np
from pathlib import Path
import csv # 导入 csv 模块
import traceback # 新增导入
from typing import List, Dict, Any, Tuple, Union, Optional # 新增类型提示

# 尝试导入 pandas，如果失败则标记，以便后续优雅处理
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# 从 model.py 导入 FusionModel 类
try:
    from model import FusionModel
except ImportError:
    # 定义一个简单的FusionModel类以避免导入错误
    class FusionModel(torch.nn.Module):
        def __init__(self):
            super(FusionModel, self).__init__()
        
        def forward(self, x1, x2):
            # 实际部署时会用真正的模型替代
            return torch.zeros(1, 5), torch.zeros(1, 5)

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
CHECKPOINTS_DIR = BASE_DIR / "checkpoints"
SPECTRA_DIR = BASE_DIR / "spectra"
IMAGES_DIR = BASE_DIR / "images"
CSV_FILE_PATH = BASE_DIR / "Skyserver_Radial5_9_2025 5_12_34 AM.csv"

# 定义允许的源列表
origins = [
    "http://localhost:8080",  # Quasar 前端开发服务器地址
    "http://localhost:8082",  # MSTAR 前端开发服务器地址
    "http://localhost:5002",  # 后端自身地址
    "*",                      # 临时允许所有源（仅开发环境使用）
    # 如果您有生产环境的前端地址，也需要加到这里
    # "https://your.production-frontend.com",
]

# 允许前端跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 新增：挂载静态文件目录
# 前端可以通过 /static/images/<subclass>/<image_file_name> 访问图像
# 前端可以通过 /static/spectra/<subclass>/<spectrum_file_name> 访问光谱文件
if IMAGES_DIR.exists():
    app.mount("/static/images", StaticFiles(directory=IMAGES_DIR), name="static_images")
if SPECTRA_DIR.exists():
    app.mount("/static/spectra", StaticFiles(directory=SPECTRA_DIR), name="static_spectra")

# 确保目录存在，如果不存在则创建
os.makedirs(CHECKPOINTS_DIR, exist_ok=True)
os.makedirs(SPECTRA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# 获取模型列表
@app.get("/api/models")
def get_models():
    models = [f for f in os.listdir(CHECKPOINTS_DIR) if f.endswith(".pth")]
    return models

# 新增：列出可用的光谱文件
@app.get("/api/available_spectra")
def list_available_spectra():
    available_files = []
    for root, _, files_in_dir in os.walk(SPECTRA_DIR):
        for file_name in files_in_dir:
            if file_name.lower().endswith(('.fit', '.fits')):
                relative_path = Path(root).relative_to(SPECTRA_DIR) / file_name
                available_files.append(str(relative_path.as_posix()))
    return sorted(available_files)

# 新增：列出可用的图像文件
@app.get("/api/available_images")
def list_available_images():
    available_files = []
    for root, _, files_in_dir in os.walk(IMAGES_DIR):
        for file_name in files_in_dir:
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                relative_path = Path(root).relative_to(IMAGES_DIR) / file_name
                available_files.append(str(relative_path.as_posix()))
    return sorted(available_files)

# 新增：解析 CSV 并关联文件，提供结构化数据
@app.get("/api/star_data")
def get_star_data():
    star_data_list = []
    if not CSV_FILE_PATH.exists():
        return JSONResponse(status_code=404, content={"detail": "Skyserver CSV file not found."})
    image_extensions = ['.jpg', '.jpeg', '.png']
    # Pandas/CSV reading logic 
    try:
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as csvfile:
            reader = None
            header = []
            for line in csvfile:
                if line.startswith('#'):
                    continue
                header = [h.strip() for h in line.strip().split(',')]
                reader = csv.DictReader(csvfile, fieldnames=header)
                break
            if reader is None:
                 return JSONResponse(status_code=500, content={"detail": "CSV file seems empty or only contains comments."})
            for row in reader:
                specobjid = str(row['specobjid']).strip()
                subclass = str(row['subclass']).strip()
                spectrum_filename_csv = f"spec-{specobjid}.fits"
                spectrum_relative_path = Path(subclass) / spectrum_filename_csv
                full_spectrum_path = SPECTRA_DIR / spectrum_relative_path
                image_found = False
                image_relative_path_str = ""
                for ext in image_extensions:
                    image_filename_csv = f"img-{specobjid}{ext}"
                    image_relative_path = Path(subclass) / image_filename_csv
                    full_image_path = IMAGES_DIR / image_relative_path
                    if full_image_path.exists() and full_image_path.is_file():
                        image_relative_path_str = str(image_relative_path.as_posix())
                        image_found = True
                        break
                if full_spectrum_path.exists() and full_spectrum_path.is_file() and image_found:
                    star_info = {k.strip(): v.strip() for k, v in row.items()}
                    star_info['spectrum_path'] = str(spectrum_relative_path.as_posix())
                    star_info['image_path'] = image_relative_path_str
                    star_data_list.append(star_info)
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error processing CSV: {str(e)}"})
    return star_data_list

# 解析FITS文件，返回光谱数据
# 修改：使其也能通过文件路径读取光谱 (可选，根据前端需求决定是否使用)
@app.post("/api/parse_spectrum")
async def parse_spectrum(spectrum_file: UploadFile = File(None), spectrum_path: str = Form(None)):
    file_to_process = None
    if spectrum_path:
        full_path = SPECTRA_DIR / spectrum_path
        if not full_path.exists() or not full_path.is_file():
            return JSONResponse(status_code=404, content={"detail": "Spectrum file not found at specified path."})
        file_to_process = full_path
    elif spectrum_file:
        file_to_process = spectrum_file.file 
    else:
        return JSONResponse(status_code=400, content={"detail": "Either spectrum_file or spectrum_path must be provided."})
    try:
        with fits.open(file_to_process) as hdul:
            data = hdul[1].data
            flux = data['flux'].tolist() if 'flux' in data.columns.names else data.field(0).tolist()
            if 'wavelength' in data.columns.names:
                wavelength = data['wavelength'].tolist()
            elif 'loglam' in data.columns.names:
                wavelength = (10 ** data['loglam']).tolist()
            else:
                wavelength = list(range(len(flux)))
        return {"wavelength": wavelength, "flux": flux}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error parsing FITS file: {str(e)}"})

# Changed back to a synchronous function
def process_single_prediction(
    model: FusionModel,
    spectrum_file_obj: Any,
    image_file_obj: Any,
    class_map: List[str]
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """处理单对光谱和图像文件的预测，返回类别概率和错误信息。"""
    try:
        # SpooledTemporaryFile.seek is synchronous
        spectrum_file_obj.seek(0) 
        image_file_obj.seek(0)

        with fits.open(spectrum_file_obj) as hdul:
            data = hdul[1].data
            flux_data = data['flux'] if 'flux' in data.columns.names else data.field(0)
            flux_data = np.array(flux_data, dtype=np.float32)
            flux_mean = np.mean(flux_data)
            flux_std = np.std(flux_data)
            if flux_std == 0:
                flux_std = 1e-8
            flux_normalized = (flux_data - flux_mean) / flux_std
            flux_tensor = torch.tensor(flux_normalized).unsqueeze(0)

        img = Image.open(image_file_obj).convert('RGB')
        img = img.resize((224, 224))
        img = np.array(img).astype(np.float32) / 255.0
        img_tensor = torch.tensor(img).permute(2, 0, 1).unsqueeze(0)

        with torch.no_grad(): # torch operations are typically CPU/GPU bound, not I/O bound for this part
            align_logits, fuse_logits = model(flux_tensor, img_tensor)
            probabilities_tensor = torch.softmax(fuse_logits, dim=1)[0]

        if len(class_map) != len(probabilities_tensor):
            return [], f"Model output size ({len(probabilities_tensor)}) does not match class_map size ({len(class_map)})."

        class_probabilities_list = []
        for i, class_name in enumerate(class_map):
            class_probabilities_list.append({
                "class_name": class_name,
                "probability": round(probabilities_tensor[i].item() * 100, 2)
            })
        return class_probabilities_list, None
    except Exception as e:
        # Log the full traceback for server-side debugging
        print(f"Error in process_single_prediction: {traceback.format_exc()}")
        return [], f"Error processing files: {str(e)}" # Return a simpler error to the client

@app.post("/api/predict")
async def predict(
    model_file: UploadFile = File(...),
    spectrum_file: UploadFile = File(...),
    image_file: UploadFile = File(...)
):
    print(f"--- New Single Prediction Request ---")
    print(f"Received model_file: {model_file.filename if model_file else 'None'}")
    print(f"Received spectrum_file: {spectrum_file.filename if spectrum_file else 'None'}")
    print(f"Received image_file: {image_file.filename if image_file else 'None'}")

    if not model_file or not model_file.filename:
        return JSONResponse(status_code=400, content={"error": "Model file is required and must have a filename."})
    if not model_file.filename.endswith(".pth"):
        return JSONResponse(status_code=400, content={"error": "Invalid model file type. Please upload a .pth file."})
    if not spectrum_file or not spectrum_file.filename:
        return JSONResponse(status_code=400, content={"error": "Spectrum file is required and must have a filename."})
    if not image_file or not image_file.filename:
        return JSONResponse(status_code=400, content={"error": "Image file is required and must have a filename."})

    class_map = ['M0', 'M1', 'M2', 'M3', 'M4']
    response_data: Dict[str, Any] = {
        "spectrum_filename": spectrum_file.filename,
        "image_filename": image_file.filename,
        "class_probabilities": None,
        "error": None
    }

    try:
        print(f"Loading model state dict from uploaded file: {model_file.filename}...")
        await model_file.seek(0) # model_file is UploadFile, its seek is async
        
        # torch.load is a CPU-bound operation, run in thread pool to not block event loop
        state_dict = await run_in_threadpool(torch.load, model_file.file, map_location='cpu')
        
        model_instance = FusionModel()
        # model_instance.load_state_dict is CPU-bound
        await run_in_threadpool(model_instance.load_state_dict, state_dict)
        
        model = model_instance
        model.eval() # This is quick, no need for threadpool
        print("Model loaded successfully.")

        # process_single_prediction contains file I/O and CPU-bound tasks (numpy, Pillow, torch tensors apart from model.eval)
        # It should be run in a thread pool.
        probabilities, error_msg = await run_in_threadpool(
            process_single_prediction, # function to run
            model,                     # args for the function
            spectrum_file.file,
            image_file.file,
            class_map
        )

        if error_msg:
            response_data["error"] = error_msg
        else:
            response_data["class_probabilities"] = probabilities

    except Exception as e:
        # Log the full traceback for server-side debugging
        print(f"Critical error in /api/predict: {traceback.format_exc()}")
        response_data["error"] = f"Server error during prediction: {str(e)}" 
        # Optionally return a 500 status code for critical errors not caught by process_single_prediction
        # return JSONResponse(status_code=500, content=response_data)

    print(f"Single prediction finished. Returning data for {spectrum_file.filename}")
    return JSONResponse(content=response_data)

# 新增：通过API端点获取文件，确保CORS策略被应用
@app.get("/api/fetch_file/{file_type}/{sub_path:path}")
async def fetch_file_for_prediction(
    file_type: str, # FastAPI 会从路径中提取
    sub_path: str   # FastAPI 会从路径中提取
):
    print(f"API Call: /api/fetch_file/{file_type}/{sub_path}")
    base_dir_to_use = None
    if file_type == "spectrum":
        base_dir_to_use = SPECTRA_DIR
    elif file_type == "image":
        base_dir_to_use = IMAGES_DIR
    else:
        print(f"Invalid file_type: {file_type}")
        return JSONResponse(status_code=400, content={"detail": "Invalid file_type. Must be 'spectrum' or 'image'"})

    # Path 安全性: 确保 sub_path 不会逃逸出 base_dir_to_use
    # os.path.abspath 将解析路径，包括 ..
    # 然后我们检查它是否仍在预期的父目录下
    prospective_path = base_dir_to_use / sub_path
    # 使用 resolve() 来规范化路径 (处理 ../, ./ 等)
    full_file_path = prospective_path.resolve()

    # 检查解析后的路径是否仍在预期的父目录下
    if base_dir_to_use.resolve() not in full_file_path.parents and full_file_path != base_dir_to_use.resolve():
        # 如果文件与基本目录相同（例如 sub_path 为空或'.'），也允许，但通常 sub_path 不会是这样
        # 主要防止目录遍历攻击，如 sub_path = ../../etc/passwd
        if not (str(full_file_path).startswith(str(base_dir_to_use.resolve()))):
             print(f"Path traversal attempt or invalid path: {sub_path} resolved to {full_file_path}")
             return JSONResponse(status_code=400, content={"detail": "Invalid file path."})

    if not full_file_path.exists() or not full_file_path.is_file():
        print(f"File not found at: {full_file_path}")
        return JSONResponse(status_code=404, content={"detail": f"File not found: {sub_path}"})
    
    file_name_for_response = full_file_path.name
    print(f"Serving file: {full_file_path} as {file_name_for_response}")
    return FileResponse(path=str(full_file_path), filename=file_name_for_response) 


# 如果直接运行此文件，启动uvicorn服务器
if __name__ == "__main__":
    import uvicorn
    port = 5002
    print(f"启动MSTAR Classification后端服务，监听端口：{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)