# predict_batch.py (服务器端运行)

import os
import torch
import pandas as pd
import numpy as np
from model.model_pl import BaselinePl
from cfg.cfg import cfg

def load_spectrum_csv(csv_path, spectrum_length):
    df = pd.read_csv(csv_path, header=None)
    flux = df.iloc[:, 1].values.astype(np.float32)
    if len(flux) < spectrum_length:
        left = (spectrum_length - len(flux)) // 2
        right = spectrum_length - len(flux) - left
        flux = np.pad(flux, (left, right), mode='constant')
    else:
        flux = flux[:spectrum_length]
    return torch.tensor(flux).unsqueeze(0).unsqueeze(0)

def predict_batch_spectra(file_list, output_path):
    ckpt_path = cfg["predict_ckpt_path"]
    model = BaselinePl.load_from_checkpoint(ckpt_path, cfg=cfg)
    model.eval().to("cuda" if torch.cuda.is_available() else "cpu")
    class_names = cfg["class_names"].split(",")
    spectrum_length = cfg["spectrum_length"]

    results = []
    for filename in file_list:
        csv_path = os.path.join(cfg["data_dir"], "predict", filename)
        x = load_spectrum_csv(csv_path, spectrum_length).to(model.device)
        with torch.no_grad():
            logits = model(x)
            probs = torch.softmax(logits, dim=1)
            pred_idx = torch.argmax(probs, dim=1).item()
            conf = torch.max(probs).item()
            results.append({
                "file": filename,
                "prediction": class_names[pred_idx],
                "confidence": round(conf, 4)
            })

    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    print(f"预测完成，保存至 {output_path}")

if __name__ == "__main__":
    # 示例用法
    test_files = ["spec-0613-52345-0363.csv", "spec-0700-53000-0012.csv"]
    predict_batch_spectra(test_files, "./predict_result.csv")
