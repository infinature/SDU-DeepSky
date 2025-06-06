# Classification of Astronomical Spectra Based on Multiscale Partial Convolution

![Network Structure](./img/model.png)

## Environment

> - Ubuntu Server 22.04 LTS
> - Python 3.10.8
> - CUDA 11.7
> - CUDNN 8.5

Create a new conda environment and install the required packages:

```shell
conda create -n mspc python=3.10
conda activate mspc
conda install pytorch torchvision torchaudio pytorch-cuda=11.7 -c pytorch -c nvidia
pip3 install opencv-python matplotlib scipy scikit-learn tqdm tensorboard tensorboardX torchinfo
```

Before training, check the `cfg/cfg.py` file to set your training configuration.

## Data Download

All data can be downloaded from the [SDSS](http://cas.sdss.org/dr18/) and [LAMOST](http://www.lamost.org/public/?locale=en) official websites according to the fields in the data folder.

## Dataset Directory Structure

Support K-fold cross-validation.

```
├── DATASET
│   ├── fold 1
│   │   ├── train
│   │   │   ├── xxx 1.csv
│   │   │   ├── xxx 2.csv
│   │   │   └── ...
│   │   ├── val
│   │   │   ├── yyy 1.csv
│   │   │   ├── yyy 2.csv
│   │   │   └── ...
│   │   ├── test
│   │   │   ├── zzz 1.csv
│   │   │   ├── zzz 2.csv
│   │   │   └── ...
│   ├── fold 2
│   │   ├── ...
│   ├── fold 3
│   │   ├── ...
└── ...
```

## Training on other sky surveys

Please modify the read_other_fits function in data_preprocess/spec_preprecess.py to preprocess the data and build a dataset, and then modify cfg/cfg.py to fine-tune the model structure


## Citation

```
@article{article,
author = {Wu, Jingjing and He, Yuchen and Wang, Wenyu and Qu, Meixia and Jiang, Bin and Zhang, Yanxia},
year = {2024},
month = {05},
pages = {260},
title = {Classification of Astronomical Spectra Based on Multiscale Partial Convolution},
volume = {167},
journal = {The Astronomical Journal},
doi = {10.3847/1538-3881/ad38ae}
}
```
