#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @file spectrum.py
# @author: wujiangu
# @date: 2023-06-01 21:11
# @description: spectrum dataset

import os

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset


class SpectrumDataset(Dataset):
    def __init__(
        self,
        data_dir: str,
        spectrum_length: int,
        class_names: list = ["A", "F", "G", "K", "M"],
        spectrum_suffix: str = ".csv",
    ) -> None:
        """spec and img dataset
        @param data_dir: data dir(include (specturm|photometric|label)/(*.csv|*.jpg|label.csv))
        @param spectrum_length: spectrum length
        @param class_names: class names
        @param spectrum_suffix: spectrum suffix
        """
        super().__init__()
        self.data_dir = data_dir
        # 调整路径以适应实际数据结构
        self.spectrum_length = spectrum_length
        self.class_names = class_names
        self.spectrum_suffix = spectrum_suffix
        
        # 检查数据目录中的文件
        print(f"正在检查数据目录: {data_dir}")
        print(f"当前工作目录: {os.getcwd()}")
        print(f"路径是否存在: {os.path.exists(data_dir)}")
        print(f"路径是目录: {os.path.isdir(data_dir)}")
        
        # 尝试规范化路径
        data_dir = os.path.abspath(data_dir)
        print(f"规范化后的路径: {data_dir}")
        
        files = os.listdir(data_dir)
        print(f"发现文件: {files}")
        
        # 使用第一个fold文件作为数据源
        fold_file = None
        for file in files:
            if file.startswith("fold_") and file.endswith(".csv"):
                fold_file = file
                break
        
        if fold_file is None:
            raise FileNotFoundError(f"在 {data_dir} 中没有找到fold_*.csv文件")
            
        print(f"使用数据文件: {fold_file}")
        # 加载第一个fold文件
        self.label = pd.read_csv(os.path.join(data_dir, fold_file))
        
        # 确保label列存在
        if "label" not in self.label.columns:
            # 如果没有label列，尝试创建一个
            if len(self.label.columns) >= 2:
                # 假设第二列是标签
                self.label.columns = ["basename", "label"] + list(self.label.columns[2:])
            else:
                raise ValueError(f"CSV文件格式不符合预期: {self.label.columns}")
        
        # 确保basename列存在
        if "basename" not in self.label.columns:
            if len(self.label.columns) >= 1:
                # 假设第一列是basename
                self.label.columns = ["basename"] + list(self.label.columns[1:])
            else:
                raise ValueError(f"CSV文件格式不符合预期: {self.label.columns}")
        

        print("=" * 20)
        print(f'dataset: {data_dir.split("/")[-1]}')
        for label in self.class_names:
            label_count = len(self.label[self.label["label"] == label])
            print(f"{label}: {label_count}")
        print("=" * 20)

    def __len__(self) -> int:
        return len(self.label)

    def __getitem__(self, index: int) -> dict:
        """get item
        @param index: index
        @return ret: dict include spec, label
        """

        # read spectrum
        if self.spectrum_suffix == ".csv":
            spec = np.loadtxt(
                os.path.join(
                    self.spectrum_dir,
                    self.label["basename"].values[index] + self.spectrum_suffix,
                ),
                delimiter=",",
                dtype="float32",
            )
        elif self.spectrum_suffix == ".npy":
            spec = np.load(
                os.path.join(
                    self.spectrum_dir,
                    self.label["basename"].values[index] + self.spectrum_suffix,
                )
            )

        # read label
        label = self.label["label"].values[index]
        # label to long
        label = np.array(self.class_names.index(label), dtype="long")
        # to torch tensor
        label = torch.from_numpy(label)

        # spec to torch tensor
        spec = torch.from_numpy(spec)[:, 1]
        if len(spec) < self.spectrum_length:
            left_num = (self.spectrum_length - len(spec)) // 2
            right_num = self.spectrum_length - len(spec) - left_num
            spec = torch.cat(
                [
                    torch.zeros(left_num, dtype=torch.float32),
                    spec,
                    torch.zeros(right_num, dtype=torch.float32),
                ],
                dim=0,
            )

        spec = spec.unsqueeze(0)

        ret = {"spec": spec, "label": label}
        return ret
