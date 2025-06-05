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
        self.spectrum_length = spectrum_length
        self.class_names = class_names
        self.spectrum_suffix = spectrum_suffix

        # self.data_dir (assigned from the data_dir parameter) is the full path to a label.csv file.
        # Example: E:\...\kfold_0\train\label\label.csv
        # os.path.dirname(self.data_dir) is E:\...\kfold_0\train\label
        # os.path.dirname(os.path.dirname(self.data_dir)) is E:\...\kfold_0\train
        self.spectrum_files_base_dir = os.path.join(os.path.dirname(os.path.dirname(self.data_dir)), "spectrum")

        # Print info about the label file and spectrum directory
        print(f"正在处理标签文件: {self.data_dir}")
        print(f"标签文件是否存在: {os.path.exists(self.data_dir)}")
        print(f"光谱文件实际目录: {self.spectrum_files_base_dir}")
        if not (os.path.exists(self.spectrum_files_base_dir) and os.path.isdir(self.spectrum_files_base_dir)):
            print(f"警告: 光谱文件目录 {self.spectrum_files_base_dir} 不存在或不是一个目录。")

        # Load the label CSV file directly
        self.label = pd.read_csv(self.data_dir)


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
        print(f'dataset: {os.path.basename(os.path.dirname(self.spectrum_files_base_dir))}')
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
                    self.spectrum_files_base_dir,
                    self.label["basename"].values[index] + self.spectrum_suffix,
                ),
                delimiter=",",
                dtype="float32",
            )
        elif self.spectrum_suffix == ".npy":
            spec = np.load(
                os.path.join(
                    self.spectrum_files_base_dir,
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
