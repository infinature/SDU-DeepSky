from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os, subprocess, threading, time, json, re, signal

app = Flask(__name__)
CORS(app)

# 自动识别当前python环境
import sys
PYTHON_EXEC = sys.executable
# PYTHON_EXEC = "D:/Desktop/ide/github_repository/recurrence/.venv/Scripts/python.exe"

# 导入用于处理路径的模块
import os
from pathlib import Path

# 获取当前文件所在目录
BASE_DIR = Path(__file__).resolve().parent
# 获取项目根目录
PROJECT_ROOT = BASE_DIR.parent
# MSPC-Net-main目录
MSPC_NET_DIR = PROJECT_ROOT / "MSPC-Net-main"

# 本地配置路径
UPLOAD_FOLDER = os.path.join(BASE_DIR, "temp")
CKPT_FOLDER = os.path.join(BASE_DIR, "temp", "weights")
# 用于记录并传入到前端来实现实时显示日志
LOG_FILE = os.path.join(BASE_DIR, "temp", "training.log")
CFG_FILE = os.path.join(MSPC_NET_DIR, "cfg", "cfg.py")
TRAIN_SCRIPT = os.path.join(MSPC_NET_DIR, "train.py")
PREDICT_SCRIPT = os.path.join(MSPC_NET_DIR, "predict_one_csv_local.py")

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CKPT_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs("../MSPC-Net-main/cfg/logs", exist_ok=True)

train_process = None  # 记录训练进程

# ========== 训练 ==========
@app.route('/train', methods=['POST'])
def train():
    global train_process
    data = request.json
    data_dir = data.get("data_dir")
    params = data.get("parameters")

    if not data_dir or not params:
        return jsonify({"error": "缺少 data_dir 或 parameters 参数"}), 400

    try:
        # 更新 cfg.py 中相关字段
        with open(CFG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        updated_lines = []
        for line in lines:
            if '"data_dir"' in line:
                updated_lines.append(f'    "data_dir": "{data_dir}",\n')
            elif '"lr"' in line:
                updated_lines.append(f'    "lr": {params["lr"]},\n')
            elif '"batch_size"' in line:
                updated_lines.append(f'    "batch_size": {params["batch_size"]},\n')
            elif '"epochs"' in line:
                updated_lines.append(f'    "epochs": {params["epochs"]},\n')
            elif '"class_names"' in line:
                updated_lines.append(f'    "class_names": "{params["class_names"]}",\n')
            elif '"num_classes"' in line:
                updated_lines.append(f'    "num_classes": {params["num_classes"]},\n')
            elif '"spectrum_length"' in line:
                updated_lines.append(f'    "spectrum_length": {params["spectrum_length"]},\n')
            elif '"device_list"' in line:
                updated_lines.append(f'    "device_list": {params["device_list"]},\n')
            elif '"num_workers"' in line:
                updated_lines.append(f'    "num_workers": {params["num_workers"]},\n')
            else:
                updated_lines.append(line)

        with open(CFG_FILE, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)

        # 启动训练进程
        with open(LOG_FILE, "w", encoding="utf-8") as log:
            train_process = subprocess.Popen(
                [PYTHON_EXEC, TRAIN_SCRIPT],
                stdout=log,
                stderr=log,
                text=True
            )

        return jsonify({"status": "started"}), 200

    except Exception as e:
        print("后端训练出错：", e)
        return jsonify({"error": str(e)}), 500


@app.route('/train/log')
def stream_log():
    def generate():
        try:
            while not os.path.exists(LOG_FILE):
                time.sleep(1)
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                f.seek(0, 2)
                while True:
                    line = f.readline()
                    if line:
                        yield f"data: {line.strip()}\n\n"
                        if "test_acc" in line and "test_" in line:
                            break
                    else:
                        time.sleep(0.5)

                # 提取最终指标
                f.seek(0)
                content = f.read()
                metrics = {}
                for key in ["test_acc", "test_f1", "test_loss", "test_precision", "test_recall"]:
                    match = re.search(rf"{key}\s*[:=]?\s*([0-9.]+)", content)
                    if match:
                        metrics[key.replace("test_", "")] = round(float(match.group(1)) * 100, 2)

                yield f"data: {json.dumps(metrics)}\n\n"
        except Exception as e:
            yield f"data: 日志流错误: {str(e)}\n\n"

    return Response(generate(), mimetype='text/event-stream')


@app.route('/train/stop', methods=['POST'])
def stop_train():
    global train_process
    if train_process:
        train_process.terminate()
        train_process = None
        return jsonify({"message": "训练终止"}), 200
    return jsonify({"message": "无活跃训练进程"}), 400

@app.route("/predict", methods=["POST"])
def predict():
    files = request.files.getlist("files")
    selected_file = request.form.get("selected_file")
    ckpt_file = request.files.get("ckpt")

    results = []
    filenames = []

    # 处理上传的 CSV 文件
    for file in files:
        local_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(local_path)
        filenames.append(file.filename)

    # 处理权重文件
    ckpt_path = None
    if ckpt_file:
        ckpt_path = os.path.join(CKPT_FOLDER, ckpt_file.filename)
        ckpt_file.save(ckpt_path)
        print(f"保存权重文件到: {ckpt_path}")  # 调试路径
        print(f"DEBUG - 完整路径: {repr(ckpt_path)}")  # 显示原始字符串

    # 预测处理（循环所有文件）
    try:
        for fname in filenames or [selected_file]:
            result = local_predict(fname, ckpt_path)
            results.append(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"results": results})


def local_predict(filename, ckpt_path=None):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    # 使用conda环境运行Python脚本
    activate_cmd = "conda activate astroyolo && "
    python_cmd = "python " + PREDICT_SCRIPT + " " + filepath
    if ckpt_path:
        python_cmd += " " + ckpt_path
    
    full_cmd = activate_cmd + python_cmd
    print("== 完整命令 ==", full_cmd)  # 调试输出
    
    # 在Windows上使用cmd.exe执行conda命令
    proc = subprocess.run(
        ["cmd.exe", "/c", full_cmd], 
        capture_output=True, 
        text=True, 
        encoding="utf-8"
    )
    output = proc.stdout + proc.stderr
    print("== 预测输出 ==\n", output)

    label, conf = "未知", 0.0
    for line in output.splitlines():
        if "预测种类" in line:
            label = line.split("：")[-1].strip()
        elif "置信度" in line:
            conf = float(line.split("：")[-1].strip())

    return {
        "filename": filename,
        "class": label,
        "confidence": conf
    }


if __name__ == "__main__":
    # 把 use_reloader=False 明确加上，阻止 Flask 热重载。
    app.run(debug=True, use_reloader=False, port=5001)