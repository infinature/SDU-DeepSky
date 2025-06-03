import torch
import pandas as pd
import numpy as np
import os
import sys
from model.model_pl import BaselinePl
from cfg.cfg_predict import cfg

def load_spectrum_csv(csv_path, spectrum_length):
    df = pd.read_csv(csv_path, header=None)
    flux = df.iloc[:, 1].values.astype(np.float32)

    # 补零或截断
    if len(flux) < spectrum_length:
        left = (spectrum_length - len(flux)) // 2
        right = spectrum_length - len(flux) - left
        flux = np.pad(flux, (left, right), mode='constant')
    else:
        flux = flux[:spectrum_length]

    tensor = torch.tensor(flux).unsqueeze(0).unsqueeze(0).float()  # shape: [1,1,L]
    return tensor

def predict_one_spectrum(csv_path, ckpt_path=None):
    # 权重路径优先使用命令行参数，其次为cfg
    ckpt_path = ckpt_path or cfg.get("predict_ckpt_path", "")
    print(f"[调试] 尝试使用权重文件: {ckpt_path}")
    if not os.path.exists(ckpt_path):
        error_msg = f"[错误] 权重文件不存在: {ckpt_path}"
        print(error_msg)
        raise FileNotFoundError(error_msg)

    # 加载模型
    model = BaselinePl.load_from_checkpoint(ckpt_path, cfg=cfg)
    model.eval().to("cuda" if torch.cuda.is_available() else "cpu")

    # 加载光谱数据
    if not os.path.exists(csv_path):
        print(f"[错误] 光谱文件不存在: {csv_path}")
        return

    x = load_spectrum_csv(csv_path, cfg["spectrum_length"]).to(model.device)

    # 预测
    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)
        pred_idx = torch.argmax(probs).item()
        conf = probs[0, pred_idx].item()
        pred_label = cfg["class_names"].split(",")[pred_idx]

    print(f"预测光谱文件：{os.path.basename(csv_path)}")
    print(f"预测种类：{pred_label}")
    print(f"预测索引：{pred_idx}")
    print(f"所有类别：{cfg['class_names']}")
    print(f"置信度：{conf:.4f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python predict_one_csv.py 光谱.csv [可选：权重.ckpt]")
    else:
        csv_path = sys.argv[1]
        ckpt_path = sys.argv[2] if len(sys.argv) > 2 else None
        predict_one_spectrum(csv_path, ckpt_path)