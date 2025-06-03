#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @file tools.py
# @author: wujiangu
# @date: 2023-05-17 13:49
# @description: tools for training

import argparse
import random

import lightning.pytorch as pl
import numpy as np
# 尝试导入pynvml，如果不存在则设置一个标志
try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False
    print("警告: pynvml库未安装，GPU监控功能将被禁用")
import torch


def seed_every_thing(seed: int = 42):
    """seed everything
    @param seed: random seed
    """
    # 1. torch
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    # 2. numpy
    np.random.seed(seed)
    # 3. random
    random.seed(seed)
    # 4. lightning
    pl.seed_everything(seed)
    # 5. set cudnn
    # torch.backends.cudnn.deterministic = True
    # torch.backends.cudnn.benchmark = False
    #


def get_free_gpu_index(
    device_list: list = None,
):
    """get free gpu index
    @param device_list: gpu index list
    @return: free gpu index
    """
    if device_list is None:
        device_list = [i for i in range(torch.cuda.device_count())]
    
    # 如果pynvml可用，使用它来获取GPU内存使用情况
    if PYNVML_AVAILABLE:
        try:
            pynvml.nvmlInit()
            memory = []
            for i in device_list:
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
                memory.append(meminfo.used)
            pynvml.nvmlShutdown()
            return device_list[memory.index(min(memory))]
        except Exception as e:
            print(f"GPU监控错误: {e}")
            # 如果出错，返回第一个可用的GPU
            if len(device_list) > 0:
                return device_list[0]
            return 0
    else:
        # 如果pynvml不可用，简单返回第一个可用的GPU
        if len(device_list) > 0:
            return device_list[0]
        return 0


def arg_parser(cfg):
    """arg parser
    @param cfg: config dict
    @return: config dict after arg parser
    """
    parser = argparse.ArgumentParser()
    for key, value in cfg.items():
        if type(value) == dict:
            for k, v in value.items():
                parser.add_argument(f"--cfg/{key}/{k}", type=type(v), default=v)
        else:
            parser.add_argument(f"--cfg/{key}", type=type(value), default=value)
    args = parser.parse_args()

    for key, value in cfg.items():
        if type(value) == dict:
            for k, v in value.items():
                cfg[key][k] = getattr(args, f"cfg/{key}/{k}")
        else:
            cfg[key] = getattr(args, f"cfg/{key}")

    if type(cfg["class_names"]) == str:
        cfg["class_names"] = cfg["class_names"].split(",")
        # sort class names
        cfg["class_names"].sort()
        cfg["num_classes"] = len(cfg["class_names"])

    # if eta_min > lr, exit
    if cfg["eta_min"] > cfg["lr"]:
        exit(0)
    return cfg
