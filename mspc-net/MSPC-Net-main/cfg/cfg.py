#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @file cfg.py
# @author: wujiangu
# @date: 2023-05-17 13:32
# @description: config file

cfg = {
    # 新增的配置项：用于找到训练所保存的权重路径
    "predict_ckpt_path": "e:/2025-undergrad-astro-frontend-mengjunyu/mspc-net/MSPC-Net-main/logs/mspc-sc-s5/test/version_0/checkpoints/epoch=004-val_acc=0.8029.ckpt",
    # train params
    "device": "auto",
    "device_list": [0],
    "seed": 42,
    "debug": False,
    "log": False,
    "test": True,
    "precision": "16-mixed",
    "num_workers": 2,
    "patience": 25,
    "min_delta": 0.001,
    # model params
    "in_channel": 1,
    # dataset params
    "num_classes": 7,
    "data_dir": "E:\\2025-undergrad-astro-frontend-mengjunyu\\mspc-net\\kfold_0",
    "class_names": "O,B,A,F,G,K,M",
    "spectrum_length": 3584,
    # log params
    "project": "mspc-sc-s5",
    "sweep": "test",
    "log_path": "./logs",
    # hyper params
    "epochs": 10,
    "lr": 0.001,
    "eta_min": 1e-8,
    "T_0": 40,
    "T_mult": 2,
    "batch_size": 32,
    "pc": {
        "in_channel": 1,
        "embed_dim": 32,
        "depth": [1, 1, 1, 1],
        "depth_scale": 6.0,
        "mp_ratio": 1.0,
        "n_div": 8,
        "patch_conv_size": 3,
        "patch_conv_stride": 1,
        "pc_conv_size": 5,
        "pc_conv_size_scale": 9.0,
        "merge_conv_size": 3,
        "merge_conv_stride": 2,
        "head_dim": 1024,
        "drop_path_rate": 0.2,
        "norm_layer": "BN",
        "act_layer": "GELU",
        "attention": "ECA_F",
    },
}
