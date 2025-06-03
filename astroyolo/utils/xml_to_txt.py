# -*- coding: utf-8 -*-
# @Author  : argus
# @File    : xml_to_txt.py
# @Software: PyCharm

import os
import xml.etree.ElementTree as ET
import random
from sklearn.model_selection import KFold
import numpy as np

# VOC标注和图片路径
ANNOTATION_PATH = os.path.join('dataset', 'VOCdevkit', 'VOC2007', 'Annotations')
IMAGE_PATH = os.path.join('dataset', 'VOCdevkit', 'VOC2007', 'JPEGImages')
TXT_SAVE_PATH = os.path.join('dataset', 'txt')
os.makedirs(TXT_SAVE_PATH, exist_ok=True)

def _main():
    xmlfilepath = "cocodata/COCO2017_train\VOCdevkit\VOC2007\Annotations/"
    total_xml = os.listdir(xmlfilepath)

    num = len(total_xml)
    list = range(num)

    ftrainval = open(
        "cocodata/COCO2017_train\VOCdevkit\VOC2007/ImageSets/Main/trainval.txt",
        "w",
    )

    for i in list:
        name = total_xml[i][:-4] + "\n"
        ftrainval.write(name)

    ftrainval.close()


def parse_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        filename = root.find('filename').text
        img_path = os.path.join(IMAGE_PATH, filename.replace('.png', '.npy').replace('.jpg', '.npy'))
        objects = root.findall('object')
        bboxes = []
        for obj in objects:
            cls = 0
            bbox = obj.find('bndbox')
            try:
                x1 = int(float(bbox.find('xmin').text))
                y1 = int(float(bbox.find('ymin').text))
                x2 = int(float(bbox.find('xmax').text))
                y2 = int(float(bbox.find('ymax').text))
                bboxes.append(f"{x1},{y1},{x2},{y2},{cls}")
            except Exception as e:
                print(f"[警告] 坐标解析失败，已跳过：{xml_file}，内容：{ET.tostring(bbox, encoding='unicode')}，错误：{e}")
        return img_path, bboxes
    except Exception as e:
        print(f"[警告] 解析xml失败，已跳过：{xml_file}，错误：{e}")
        return None, []

def write_txt(file_list, save_txt):
    with open(save_txt, 'w') as f:
        for xml_name in file_list:
            xml_path = os.path.join(ANNOTATION_PATH, xml_name)
            img_path, bboxes = parse_xml(xml_path)
            for bbox in bboxes:
                f.write(f"{img_path} {bbox}\n")

def generate_k_fold_cross_validation(k=5, seed=42):
    """
    生成k折交叉验证的训练、验证、测试集
    
    Args:
        k: 折数
        seed: 随机种子
    
    Returns:
        None, 直接写入文件
    """
    print(f"开始生成{k}折交叉验证数据集...")
    
    # 设置随机种子保证结果可重现
    random.seed(seed)
    np.random.seed(seed)
    
    # 获取所有xml文件
    xml_files = [f for f in os.listdir(ANNOTATION_PATH) if f.endswith('.xml')]
    random.shuffle(xml_files)  # 随机打乱文件列表
    file_stems = [os.path.splitext(f)[0] for f in xml_files]
    
    # 创建保存目录
    image_sets_main_dir = os.path.join('dataset', 'VOCdevkit', 'VOC2007', 'ImageSets', 'Main')
    os.makedirs(image_sets_main_dir, exist_ok=True)
    
    # 按照7:1:2的比例划分数据集
    total = len(file_stems)
    train_ratio = 0.7
    valid_ratio = 0.1
    test_ratio = 0.2
    
    # 记录统计信息
    fold_stats = []
    
    # 对每一折进行处理
    for fold_idx in range(k):
        # 为这一折创建一个新的索引排列
        fold_indices = list(range(total))
        random.shuffle(fold_indices)
        
        # 按照比例准确划分数据
        valid_size = int(total * valid_ratio)
        test_size = int(total * test_ratio)
        train_size = total - test_size - valid_size
        
        # 划分索引
        valid_indices = fold_indices[:valid_size]
        test_indices = fold_indices[valid_size:valid_size+test_size]
        train_indices = fold_indices[valid_size+test_size:]
        
        # 获取训练、验证和测试数据的文件名
        train_files = [file_stems[i] for i in train_indices]
        valid_files = [file_stems[i] for i in valid_indices]
        test_files = [file_stems[i] for i in test_indices]
        
        # 保存到文件
        train_file = os.path.join(image_sets_main_dir, f'fold{fold_idx}_train.txt')
        valid_file = os.path.join(image_sets_main_dir, f'fold{fold_idx}_valid.txt')
        test_file = os.path.join(image_sets_main_dir, f'fold{fold_idx}_test.txt')
        
        with open(train_file, 'w') as f:
            f.write('\n'.join(train_files))
        
        with open(valid_file, 'w') as f:
            f.write('\n'.join(valid_files))
        
        with open(test_file, 'w') as f:
            f.write('\n'.join(test_files))
        
        # 统计信息
        fold_stats.append({
            'fold': fold_idx,
            'train': len(train_files),
            'valid': len(valid_files),
            'test': len(test_files)
        })
        
        print(f"第{fold_idx}折: 训练集 {len(train_files)}个 ({len(train_files)/total*100:.1f}%), 验证集 {len(valid_files)}个 ({len(valid_files)/total*100:.1f}%), 测试集 {len(test_files)}个 ({len(test_files)/total*100:.1f}%)")
    
    # 输出整体统计
    print("\n五折交叉验证数据集生成完成！")
    print(f"总文件数: {len(file_stems)}")
    print(f"平均训练集大小: {sum(stats['train'] for stats in fold_stats) / k}")
    print(f"平均验证集大小: {sum(stats['valid'] for stats in fold_stats) / k}")
    print(f"平均测试集大小: {sum(stats['test'] for stats in fold_stats) / k}")
    print(f"划分比例: 训练集 {train_ratio*100:.0f}%, 验证集 {valid_ratio*100:.0f}%, 测试集 {test_ratio*100:.0f}%")
    
    # 使用第一折的划分来创建标准格式文件
    with open(os.path.join(image_sets_main_dir, 'train.txt'), 'w') as f:
        f.write('\n'.join(train_files))
    
    with open(os.path.join(image_sets_main_dir, 'valid.txt'), 'w') as f:
        f.write('\n'.join(valid_files))
    
    with open(os.path.join(image_sets_main_dir, 'test.txt'), 'w') as f:
        f.write('\n'.join(test_files))
    
    # 为旧版本兼容性创建trainval文件
    with open(os.path.join(image_sets_main_dir, 'trainval.txt'), 'w') as f:
        f.write('\n'.join(train_files + valid_files))
        
    # 生成折叠的训练标注文本文件
    for fold_idx in range(k):
        # 读取相应的文件列表
        train_file = os.path.join(image_sets_main_dir, f'fold{fold_idx}_train.txt')
        valid_file = os.path.join(image_sets_main_dir, f'fold{fold_idx}_valid.txt')
        test_file = os.path.join(image_sets_main_dir, f'fold{fold_idx}_test.txt')
        
        with open(train_file, 'r') as f:
            train_files = [line.strip() + '.xml' for line in f if line.strip()]
            
        with open(valid_file, 'r') as f:
            valid_files = [line.strip() + '.xml' for line in f if line.strip()]
            
        with open(test_file, 'r') as f:
            test_files = [line.strip() + '.xml' for line in f if line.strip()]
        
        # 创建标注文件
        os.makedirs(TXT_SAVE_PATH, exist_ok=True)
        write_txt(train_files, os.path.join(TXT_SAVE_PATH, f'fold{fold_idx}_train.txt'))
        write_txt(valid_files, os.path.join(TXT_SAVE_PATH, f'fold{fold_idx}_valid.txt'))
        write_txt(test_files, os.path.join(TXT_SAVE_PATH, f'fold{fold_idx}_test.txt'))

if __name__ == "__main__":
    # 生成五折交叉验证数据集
    generate_k_fold_cross_validation(k=5, seed=42)
    print(f"已生成五折交叉验证数据集，详情请查看 {os.path.join('dataset', 'VOCdevkit', 'VOC2007', 'ImageSets', 'Main')} 目录")
