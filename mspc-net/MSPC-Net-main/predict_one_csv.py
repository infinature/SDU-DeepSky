import torch
import pandas as pd
import numpy as np
import os
import sys

from model.model_pl import BaselinePl
from cfg.cfg_predict import cfg


def load_spectrum_csv(csv_path, spectrum_length):
    """
    读取 CSV 格式光谱，提取 flux 列，长度不足则补零，超长则截断。
    并将其转换为 shape: [1, spectrum_length] 的 tensor。
    """
    df = pd.read_csv(csv_path, header=None)
    flux = df.iloc[:, 1].values.astype(np.float32)

    # 补齐或截断
    if len(flux) < spectrum_length:
        left = (spectrum_length - len(flux)) // 2
        right = spectrum_length - len(flux) - left
        flux = np.pad(flux, (left, right), mode='constant')
    else:
        flux = flux[:spectrum_length]

    # [1, 1, spectrum_length]
    flux_tensor = torch.tensor(flux, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
    return flux_tensor


def predict_one_spectrum(csv_filename):
    # 1. 模型加载
    ckpt_path = cfg["predict_ckpt_path"]
    model = BaselinePl.load_from_checkpoint(ckpt_path, cfg=cfg)
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # 2. 加载数据
    # 这里应该是有问题的： 并不是将文件名拼接在data_dir后面，而是在这个项目下的user_uploads后面专门用来存放上传的文件（针对服务器版的问题）
    test_dir = os.path.join(cfg["data_dir"], "test", "spectrum")
    if not os.path.exists(test_dir):
        test_dir = cfg["data_dir"]  # 支持上传目录就在 data_dir 的情况

    spectrum_path = os.path.join(test_dir, csv_filename)
    if not os.path.exists(spectrum_path):
        print(f"[错误] 找不到光谱文件: {spectrum_path}")
        return

    x_tensor = load_spectrum_csv(spectrum_path, cfg["spectrum_length"]).to(device)

    # 3. 预测
    with torch.no_grad():
        logits = model(x_tensor)
        probs = torch.softmax(logits, dim=1)
        pred_idx = torch.argmax(probs, dim=1).item()
        conf = torch.max(probs).item()
        class_names = cfg["class_names"].split(",")
        pred_label = class_names[pred_idx]

    # 4. 输出结果（stdout 打印，供 SSH 后端读取）
    print(f"预测光谱文件：{csv_filename}")
    print(f"预测种类：{pred_label}")
    print(f"预测索引：{pred_idx}")
    print(f"所有类别：{cfg['class_names']}")
    print(f"置信度：{conf:.4f}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python predict_one_csv.py 文件名.csv")
    else:
        predict_one_spectrum(sys.argv[1])
