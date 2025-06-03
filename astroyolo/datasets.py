import os
import sys

sys.path.append("..")
sys.path.append("../utils")
import torch
from torch.utils.data import Dataset, DataLoader
import config.model_config as cfg
import numpy as np
import random

import utils.data_augment as dataAug
import utils.tools as tools


class BuildDataset(Dataset):
    def __init__(self, anno_file_type, img_size=416, anno_txt_path=None):
        self.img_size = img_size
        self.classes = cfg.Customer_DATA["CLASSES"]
        self.num_classes = len(self.classes)
        self.class_to_id = dict(zip(self.classes, range(self.num_classes)))
        self.__annotations = self.__load_annotations(anno_file_type, anno_txt_path)

    def __len__(self):
        return len(self.__annotations)

    def __getitem__(self, item):
        assert item <= len(self), "index range error"

        img_org, bboxes_org = self.__parse_annotation(self.__annotations[item])
        # 确保图像形状为 (H, W, 3) 再进行转置
        if len(img_org.shape) == 3 and img_org.shape[2] == 3:
            img_org = img_org.transpose(2, 0, 1)  # HWC->CHW
        else:
            print(f"警告: img_org形状异常 {img_org.shape}，尝试修正")
            # 尝试创建一个正确形状的图像
            corrected_img = np.zeros((3, self.img_size, self.img_size), dtype=img_org.dtype)
            
            # 对于形状不匹配的情况，我们需要特殊处理
            if img_org.shape == (3, 64, 3):
                # 复制数据到目标数组的左上角
                corrected_img[:, :64, :3] = img_org
                # 填充其余部分（可以用均值或重复现有数据）
                for c in range(3):
                    # 水平方向填充
                    for i in range(64, self.img_size):
                        corrected_img[c, i, :3] = corrected_img[c, 63, :3]
                    # 垂直方向填充
                    for j in range(3, self.img_size):
                        corrected_img[c, :, j] = corrected_img[c, :, 2]
            else:
                # 如果形状出乎意料，我们至少确保数据不为空
                print(f"警告: 意外的图像形状 {img_org.shape}, 使用简单填充")
                # 简单地将所有可用数据复制到目标数组
                h = min(img_org.shape[1], corrected_img.shape[1])
                w = min(img_org.shape[2], corrected_img.shape[2])
                corrected_img[:, :h, :w] = img_org[:, :h, :w]
            
            img_org = corrected_img

        item_mix = random.randint(0, len(self.__annotations) - 1)
        img_mix, bboxes_mix = self.__parse_annotation(
            self.__annotations[item_mix]
        )
        # 同样确保img_mix形状正确
        if len(img_mix.shape) == 3 and img_mix.shape[2] == 3:
            img_mix = img_mix.transpose(2, 0, 1)  # HWC->CHW
        else:
            print(f"警告: img_mix形状异常 {img_mix.shape}，尝试修正")
            # 尝试创建一个正确形状的图像
            corrected_img = np.zeros((3, self.img_size, self.img_size), dtype=img_mix.dtype)
            
            # 对于形状不匹配的情况，我们需要特殊处理
            if img_mix.shape == (3, 64, 3):
                # 复制数据到目标数组的左上角
                corrected_img[:, :64, :3] = img_mix
                # 填充其余部分
                for c in range(3):
                    # 水平方向填充
                    for i in range(64, self.img_size):
                        corrected_img[c, i, :3] = corrected_img[c, 63, :3]
                    # 垂直方向填充
                    for j in range(3, self.img_size):
                        corrected_img[c, :, j] = corrected_img[c, :, 2]
            else:
                # 如果形状出乎意料，我们至少确保数据不为空
                print(f"警告: 意外的图像形状 {img_mix.shape}, 使用简单填充")
                # 简单地将所有可用数据复制到目标数组
                h = min(img_mix.shape[1], corrected_img.shape[1])
                w = min(img_mix.shape[2], corrected_img.shape[2])
                corrected_img[:, :h, :w] = img_mix[:, :h, :w]
            
            img_mix = corrected_img

        # Mixup 前检查
        print(f"Before Mixup - img_org shape: {img_org.shape}, img_mix shape: {img_mix.shape}") # Debug print
        if np.isnan(img_org).any() or np.isinf(img_org).any():
            print(f"[Mixup前] img_org 存在 NaN/Inf, item={item}")
        if np.isnan(img_mix).any() or np.isinf(img_mix).any():
            print(f"[Mixup前] img_mix 存在 NaN/Inf, item_mix={item_mix}")
            
        # 确保两个图像的尺寸一致，以便进行 Mixup 操作
        target_shape = (3, self.img_size, self.img_size)  # 目标形状
        
        # 调整 img_org 的形状（如果需要）
        if img_org.shape != target_shape:
            print(f"调整 img_org 的形状从 {img_org.shape} 到 {target_shape}")
            # 使用numpy进行调整
            # 创建目标尺寸的空数组
            resized_img = np.zeros(target_shape, dtype=img_org.dtype)
            
            # 对于形状不匹配的情况，我们需要特殊处理
            if img_org.shape == (3, 64, 3):
                # 复制数据到目标数组的左上角
                resized_img[:, :64, :3] = img_org
                # 填充其余部分（可以用均值或重复现有数据）
                for c in range(3):
                    # 水平方向填充
                    for i in range(64, self.img_size):
                        resized_img[c, i, :3] = resized_img[c, 63, :3]
                    # 垂直方向填充
                    for j in range(3, self.img_size):
                        resized_img[c, :, j] = resized_img[c, :, 2]
            else:
                # 如果形状出乎意料，我们至少确保数据不为空
                print(f"警告: 意外的图像形状 {img_org.shape}, 使用简单填充")
                # 简单地将所有可用数据复制到目标数组
                h = min(img_org.shape[1], target_shape[1])
                w = min(img_org.shape[2], target_shape[2])
                resized_img[:, :h, :w] = img_org[:, :h, :w]
            
            img_org = resized_img
            
        # 调整 img_mix 的形状（如果需要）
        if img_mix.shape != target_shape:
            print(f"调整 img_mix 的形状从 {img_mix.shape} 到 {target_shape}")
            # 使用numpy进行调整
            # 创建目标尺寸的空数组
            resized_img = np.zeros(target_shape, dtype=img_mix.dtype)
            
            # 对于形状不匹配的情况，我们需要特殊处理
            if img_mix.shape == (3, 64, 3):
                # 复制数据到目标数组的左上角
                resized_img[:, :64, :3] = img_mix
                # 填充其余部分
                for c in range(3):
                    # 水平方向填充
                    for i in range(64, self.img_size):
                        resized_img[c, i, :3] = resized_img[c, 63, :3]
                    # 垂直方向填充
                    for j in range(3, self.img_size):
                        resized_img[c, :, j] = resized_img[c, :, 2]
            else:
                # 如果形状出乎意料，我们至少确保数据不为空
                print(f"警告: 意外的图像形状 {img_mix.shape}, 使用简单填充")
                # 简单地将所有可用数据复制到目标数组
                h = min(img_mix.shape[1], target_shape[1])
                w = min(img_mix.shape[2], target_shape[2])
                resized_img[:, :h, :w] = img_mix[:, :h, :w]
            
            img_mix = resized_img
            
        # 再次检查形状
        print(f"调整后 - img_org shape: {img_org.shape}, img_mix shape: {img_mix.shape}")

        img, bboxes = dataAug.Mixup()(img_org, bboxes_org, img_mix, bboxes_mix)

        # Mixup 后检查
        if np.isnan(img).any() or np.isinf(img).any():
            print(f"[Mixup后] img 存在 NaN/Inf, item={item}")

        del img_org, bboxes_org, img_mix, bboxes_mix

        (
            label_sbbox,
            label_mbbox,
            label_lbbox,
            sbboxes,
            mbboxes,
            lbboxes,
        ) = self.__creat_label(bboxes)

        # 标签生成后检查
        for name, arr in zip(
            ['label_sbbox', 'label_mbbox', 'label_lbbox', 'sbboxes', 'mbboxes', 'lbboxes'],
            [label_sbbox, label_mbbox, label_lbbox, sbboxes, mbboxes, lbboxes]
        ):
            if np.isnan(arr).any() or np.isinf(arr).any():
                print(f"[标签生成] {name} 存在 NaN/Inf, item={item}")

        img = torch.from_numpy(img).float()
        label_sbbox = torch.from_numpy(label_sbbox).float()
        label_mbbox = torch.from_numpy(label_mbbox).float()
        label_lbbox = torch.from_numpy(label_lbbox).float()
        sbboxes = torch.from_numpy(sbboxes).float()
        mbboxes = torch.from_numpy(mbboxes).float()
        lbboxes = torch.from_numpy(lbboxes).float()

        # === 自动NaN/Inf检查 ===
        def check_nan_inf(tensor, name):
            if torch.isnan(tensor).any() or torch.isinf(tensor).any():
                print(f"[数据异常] {name} 存在 NaN 或 Inf，item={item}")
        check_nan_inf(img, 'img')
        check_nan_inf(label_sbbox, 'label_sbbox')
        check_nan_inf(label_mbbox, 'label_mbbox')
        check_nan_inf(label_lbbox, 'label_lbbox')
        # ======================

        return (
            img,
            label_sbbox,
            label_mbbox,
            label_lbbox,
            sbboxes,
            mbboxes,
            lbboxes,
        )

    def __load_annotations(self, anno_type, anno_txt_path=None):
        # 优先使用自定义txt路径
        if anno_txt_path is not None:
            assert os.path.exists(anno_txt_path), f"{anno_txt_path} 不存在！"
            with open(anno_txt_path, "r") as f:
                annotations = list(filter(lambda x: len(x.strip()) > 0, f.readlines()))
            assert len(annotations) > 0, f"{anno_txt_path} 没有可用样本！"
            return annotations
        # 否则按原有逻辑
        assert anno_type in [
            "train",
            "test",
        ], "You must choice one of the 'train' or 'test' for anno_type parameter"
        anno_path = os.path.join(
            cfg.DATA_PATH, anno_type + "_annotation.txt"
        )
        with open(anno_path, "r") as f:
            annotations = list(filter(lambda x: len(x.strip()) > 0, f.readlines()))
        assert len(annotations) > 0, "No images found in {}".format(anno_path)
        return annotations


    def __parse_annotation(self, annotation):
        """
        Data augument.
        :param annotation: Image' path and bboxes' coordinates, categories.
        ex. [image_path xmin,ymin,xmax,ymax,class_ind xmin,ymin,xmax,ymax,class_ind ...]
        :return: Return the enhanced image and bboxes. bbox'shape is [xmin, ymin, xmax, ymax, class_ind]
        """
        anno = annotation.strip().split(" ")

        # 获取图片路径
        img_path = anno[0]
        
        # 尝试多种路径匹配方式
        valid_path = None
        
        # 可能的路径列表
        possible_paths = [
            img_path,  # 原始路径
            img_path + '.npy' if not img_path.endswith('.npy') else img_path,  # 添加.npy后缀
            os.path.join(cfg.VOC_IMGS_PATH, os.path.basename(img_path)),  # 直接使用文件名
            os.path.join(cfg.VOC_IMGS_PATH, os.path.basename(img_path) + '.npy') if not img_path.endswith('.npy') else os.path.join(cfg.VOC_IMGS_PATH, os.path.basename(img_path)),  # 使用文件名加.npy
            os.path.join(cfg.VOC_IMGS_PATH, 'SDSS_' + os.path.basename(img_path)),  # 添加SDSS_前缀
            os.path.join(cfg.VOC_IMGS_PATH, 'SDSS_' + os.path.basename(img_path) + '.npy') if not img_path.endswith('.npy') else os.path.join(cfg.VOC_IMGS_PATH, 'SDSS_' + os.path.basename(img_path)),  # 添加SDSS_前缀和.npy后缀
        ]
        
        # 如果是纯数字ID，尝试转换为科学计数法格式
        if img_path.isdigit():
            try:
                sci_id_full = f"{float(img_path):.16e}"
                sci_id_trim = sci_id_full.split('e+')[0].rstrip('0').rstrip('.') + 'e+' + sci_id_full.split('e+')[-1]
                possible_paths.extend([
                    os.path.join(cfg.VOC_IMGS_PATH, sci_id_full + '.npy'),
                    os.path.join(cfg.VOC_IMGS_PATH, 'SDSS_' + sci_id_full + '.npy'),
                    os.path.join(cfg.VOC_IMGS_PATH, sci_id_trim + '.npy'),
                    os.path.join(cfg.VOC_IMGS_PATH, 'SDSS_' + sci_id_trim + '.npy'),
                ])
            except Exception:
                pass
        
        # 测试每个路径
        for path in possible_paths:
            if os.path.exists(path):
                valid_path = path
                print(f"成功找到图片: {valid_path} (原路径: {img_path})")
                break
        
        # 如果不能找到有效路径，尝试查找所有.npy文件并进行模糊匹配
        if valid_path is None:
            # 裁剪可能的完整ID
            img_id = os.path.basename(img_path).replace('.npy', '')
            print(f"尝试模糊匹配 ID: {img_id}")
            
            # 同时准备科学计数法形式（若可能）
            sci_id_variants = []
            if img_id.isdigit():
                try:
                    sci_full = f"{float(img_id):.16e}"
                    sci_trim = sci_full.split('e+')[0].rstrip('0').rstrip('.') + 'e+' + sci_full.split('e+')[-1]
                    sci_15 = f"{float(img_id):.15e}"
                    sci_15_trim = sci_15.split('e+')[0].rstrip('0').rstrip('.') + 'e+' + sci_15.split('e+')[-1]
                    sci_id_variants = [sci_full, sci_trim, sci_15, sci_15_trim]
                except Exception:
                    pass
            
            for filename in os.listdir(cfg.VOC_IMGS_PATH):
                if filename.endswith('.npy'):
                    match = False
                    if img_id in filename:
                        match = True
                    else:
                        for sci_variant in sci_id_variants:
                            if sci_variant and sci_variant in filename:
                                match = True
                                break
                    if match:
                        valid_path = os.path.join(cfg.VOC_IMGS_PATH, filename)
                        print(f"模糊匹配成功: {valid_path}")
                        break
        
        # 如果仍然找不到，抛出错误
        if valid_path is None:
            raise FileNotFoundError(f"找不到图像文件: {img_path}, 请检查数据集目录和文件名格式")
        
        # 使用有效路径
        img_path = valid_path
        
        # 加载图像数据并初始化边界框
        bboxes = np.empty((0, 5), dtype=np.float32)
        
        try:
            # 加载图像数据
            img_data = np.load(img_path)
            
            # 处理图像形状
            if len(img_data.shape) == 3:
                # 检查图像格式: (C,H,W) 或 (H,W,C)
                if img_data.shape[0] == 3:  # 假设是(C,H,W)格式
                    # 转为(H,W,C)格式用于处理
                    img = img_data.transpose(1, 2, 0)
                elif img_data.shape[2] == 3:  # 已经是(H,W,C)格式
                    img = img_data
                else:
                    # 处理异常情况，确保图像形状正确
                    raise ValueError(f"图像通道数异常: {img_data.shape}")
            else:
                raise ValueError(f"不支持的图像维度: {img_data.shape}")
            
            # 记录原始尺寸并判断是否需要resize
            original_size = img.shape[:2]  # (h, w)
            need_resize = (original_size[0] != self.img_size) or (original_size[1] != self.img_size)
            
            # 处理边界框
            if len(anno) > 1 and anno[1].strip():
                # 文本中直接包含了边界框信息
                bboxes = np.array([list(map(float, box.split(","))) for box in anno[1:]])
            else:
                # 如果文本中没有边界框信息，尝试从XML文件获取
                # 从图像路径推断XML文件路径
                img_id = os.path.splitext(os.path.basename(img_path))[0]
                xml_path = os.path.join(cfg.DATA_PATH, 'VOCdevkit/VOC2007/Annotations', f"{img_id}.xml")
                
                if os.path.exists(xml_path):
                    # 解析XML文件获取边界框信息
                    import xml.etree.ElementTree as ET
                    tree = ET.parse(xml_path)
                    root = tree.getroot()
                    
                    # 获取图像尺寸
                    size = root.find('size')
                    width = int(size.find('width').text)
                    height = int(size.find('height').text)
                    
                    # 收集所有目标的边界框
                    temp_bboxes = []
                    for obj in root.findall('object'):
                        cls_name = obj.find('name').text
                        if cls_name in self.class_to_id:
                            cls_id = self.class_to_id[cls_name]
                            bbox = obj.find('bndbox')
                            xmin = float(bbox.find('xmin').text)
                            ymin = float(bbox.find('ymin').text)
                            xmax = float(bbox.find('xmax').text)
                            ymax = float(bbox.find('ymax').text)
                            temp_bboxes.append([xmin, ymin, xmax, ymax, cls_id])
                    
                    if temp_bboxes:
                        bboxes = np.array(temp_bboxes, dtype=np.float32)
            # 如果仍未找到任何边界框，打印提示
            if bboxes.shape[0] == 0:
                print(f"没有边界框: {img_path}")
            # === 保证图像尺寸一致 ===
            # 无论原始尺寸如何，都将图像缩放（或 LetterBox）到 (self.img_size, self.img_size)，并同步调整边界框坐标。
            img, bboxes = dataAug.Resize((self.img_size, self.img_size), True)(np.copy(img), np.copy(bboxes))
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            # 如果加载失败，返回空的图像和边界框
            # 创建一个空的占位图像
            img = np.zeros((self.img_size, self.img_size, 3), dtype=np.uint8)
            print(f"使用空白图像代替加载失败的图像: {img_path}")
            bboxes = np.empty((0, 5), dtype=np.float32)
        # img = cv2.imread(img_path)  # H*W*C and C=BGR
        assert img is not None, "File Not Found " + img_path
        # 边界框在try块中已处理过，此处不再重复处理

        # img, bboxes = dataAug.RandomHorizontalFilp()(
        #     np.copy(img), np.copy(bboxes), img_path
        # )
        # img, bboxes = dataAug.RandomCrop()(np.copy(img), np.copy(bboxes))
        # img, bboxes = dataAug.RandomAffine()(np.copy(img), np.copy(bboxes))
        # img, bboxes = dataAug.Resize((self.img_size, self.img_size), True)(
        #     np.copy(img), np.copy(bboxes)
        # )

        return img, bboxes

    def __creat_label(self, bboxes):
        """
        Label assignment. For a single picture all GT box bboxes are assigned anchor.
        1、Select a bbox in order, convert its coordinates("xyxy") to "xywh"; and scale bbox'
           xywh by the strides.
        2、Calculate the iou between the each detection layer'anchors and the bbox in turn, and select the largest
            anchor to predict the bbox.If the ious of all detection layers are smaller than 0.3, select the largest
            of all detection layers' anchors to predict the bbox.

        Note :
        1、The same GT may be assigned to multiple anchors. And the anchors may be on the same or different layer.
        2、The total number of bboxes may be more than it is, because the same GT may be assigned to multiple layers
        of detection.

        """

        anchors = np.array(cfg.MODEL["ANCHORS"])
        strides = np.array(cfg.MODEL["STRIDES"])
        train_output_size = self.img_size / strides
        anchors_per_scale = cfg.MODEL["ANCHORS_PER_SCLAE"]

        label = [
            np.zeros(
                (
                    int(train_output_size[i]),
                    int(train_output_size[i]),
                    anchors_per_scale,
                    6 + self.num_classes,
                )
            )
            for i in range(3)
        ]
        for i in range(3):
            label[i][..., 5] = 1.0

        bboxes_xywh = [
            np.zeros((150, 4)) for _ in range(3)
        ]  # Darknet the max_num is 30
        bbox_count = np.zeros((3,))

        for bbox in bboxes:
            bbox_coor = bbox[:4]
            bbox_class_ind = int(bbox[4])
            bbox_mix = bbox[5]

            # onehot
            one_hot = np.zeros(self.num_classes, dtype=np.float32)
            one_hot[bbox_class_ind] = 1.0
            one_hot_smooth = dataAug.LabelSmooth()(one_hot, self.num_classes)

            # convert "xyxy" to "xywh"
            bbox_xywh = np.concatenate(
                [
                    (bbox_coor[2:] + bbox_coor[:2]) * 0.5,
                    bbox_coor[2:] - bbox_coor[:2],
                ],
                axis=-1,
            )
            # print("bbox_xywh: ", bbox_xywh)
            for j in range(len(bbox_xywh)):
                if int(bbox_xywh[j]) >= self.img_size:
                    differ = bbox_xywh[j] - float(self.img_size) + 1.
                    bbox_xywh[j] -= differ
            bbox_xywh_scaled = (
                    1.0 * bbox_xywh[np.newaxis, :] / strides[:, np.newaxis]
            )

            iou = []
            exist_positive = False
            for i in range(3):
                anchors_xywh = np.zeros((anchors_per_scale, 4))
                anchors_xywh[:, 0:2] = (
                        np.floor(bbox_xywh_scaled[i, 0:2]).astype(np.int32) + 0.5
                )  # 0.5 for compensation
                anchors_xywh[:, 2:4] = anchors[i]

                iou_scale = tools.iou_xywh_numpy(
                    bbox_xywh_scaled[i][np.newaxis, :], anchors_xywh
                )
                iou.append(iou_scale)
                iou_mask = iou_scale > 0.3

                if np.any(iou_mask):
                    xind, yind = np.floor(bbox_xywh_scaled[i, 0:2]).astype(
                        np.int32
                    )

                    # Bug : 当多个bbox对应同一个anchor时，默认将该anchor分配给最后一个bbox
                    label[i][yind, xind, iou_mask, 0:4] = bbox_xywh
                    label[i][yind, xind, iou_mask, 4:5] = 1.0
                    label[i][yind, xind, iou_mask, 5:6] = bbox_mix
                    label[i][yind, xind, iou_mask, 6:] = one_hot_smooth

                    bbox_ind = int(bbox_count[i] % 150)  # BUG : 150为一个先验值,内存消耗大
                    bboxes_xywh[i][bbox_ind, :4] = bbox_xywh
                    bbox_count[i] += 1

                    exist_positive = True

            if not exist_positive:
                best_anchor_ind = np.argmax(np.array(iou).reshape(-1), axis=-1)
                best_detect = int(best_anchor_ind / anchors_per_scale)
                best_anchor = int(best_anchor_ind % anchors_per_scale)

                xind, yind = np.floor(
                    bbox_xywh_scaled[best_detect, 0:2]
                ).astype(np.int32)

                label[best_detect][yind, xind, best_anchor, 0:4] = bbox_xywh
                label[best_detect][yind, xind, best_anchor, 4:5] = 1.0
                label[best_detect][yind, xind, best_anchor, 5:6] = bbox_mix
                label[best_detect][yind, xind, best_anchor, 6:] = one_hot_smooth

                bbox_ind = int(bbox_count[best_detect] % 150)
                bboxes_xywh[best_detect][bbox_ind, :4] = bbox_xywh
                bbox_count[best_detect] += 1

        label_sbbox, label_mbbox, label_lbbox = label
        sbboxes, mbboxes, lbboxes = bboxes_xywh

        return label_sbbox, label_mbbox, label_lbbox, sbboxes, mbboxes, lbboxes


if __name__ == "__main__":

    voc_dataset = BuildDataset(anno_file_type="train", img_size=352)
    dataloader = DataLoader(
        voc_dataset, shuffle=True, batch_size=32, num_workers=0
    )

    for i, (
            img,
            label_sbbox,
            label_mbbox,
            label_lbbox,
            sbboxes,
            mbboxes,
            lbboxes,
    ) in enumerate(dataloader):
        if i == 0:
            print(img.shape)
            print(label_sbbox.shape)
            print(label_mbbox.shape)
            print(label_lbbox.shape)
            print(sbboxes.shape)
            print(mbboxes.shape)
            print(lbboxes.shape)

            if img.shape[0] == 1:
                labels = np.concatenate(
                    [
                        label_sbbox.reshape(-1, 26),
                        label_mbbox.reshape(-1, 26),
                        label_lbbox.reshape(-1, 26),
                    ],
                    axis=0,
                )
                labels_mask = labels[..., 4] > 0
                labels = np.concatenate(
                    [
                        labels[labels_mask][..., :4],
                        np.argmax(
                            labels[labels_mask][..., 6:], axis=-1
                        ).reshape(-1, 1),
                    ],
                    axis=-1,
                )

                print(labels.shape)
                tools.plot_box(labels, img, id=1)
