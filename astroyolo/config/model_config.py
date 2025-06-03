import os.path as osp
import os

PROJECT_PATH = osp.abspath(osp.join(osp.dirname(__file__), '..'))
# 使用绝对路径指向数据集
DATA_PATH = osp.join(PROJECT_PATH, 'dataset')  # 使用绝对路径
# 添加VOC数据集的图像路径
VOC_IMGS_PATH = osp.join(DATA_PATH, 'VOCdevkit', 'VOC2007', 'JPEGImages')

# train
TRAIN = {
    'amp': True,  # use amp or not
    'TRAIN_IMG_SIZE': 352,  # training image size
    'BATCH_SIZE': 4,  # 批大小，自动调整为4以避免显存溢出
    'IOU_THRESHOLD_LOSS': 0.5,  # iou threshold for loss
    'YOLO_EPOCHS': 50,  # 总训练轮数
    'NUMBER_WORKERS': 8,  # 数据加载线程数
    'MOMENTUM': 0.9,  # SGD momentum
    'WEIGHT_DECAY': 0.0005,  # 权重衰减
    'LR_INIT': 1e-3,  # initial learning rate
    'LR_END': 1e-6,  # 最终学习率
    'WARMUP_EPOCHS': 2,  # 预热轮数
}

# val
VAL = {
    'EVAL_EPOCH': 5,  # 每隔多少轮进行评估
    # 确保测试图像尺寸与训练图像尺寸保持一致，避免临时转换
    'TEST_IMG_SIZE': TRAIN['TRAIN_IMG_SIZE'],  # 直接引用训练图像尺寸，始终保持一致
    'BATCH_SIZE': 4,  # 验证批大小，自动调整为4以避免显存溢出
    'NUMBER_WORKERS': 8,  # 数据加载线程数
    'CONF_THRESH': 0.05,  # 降低置信度阈值
    'NMS_THRESH': 0.45,  # 保持NMS阈值
    'MULTI_SCALE_VAL': False,
    'FLIP_VAL': False,
}

Customer_DATA = {
    'NUM': 1,  # your dataset number
    'CLASSES': ['bhb'],  # 类别
}

# model
MODEL = {
    'ANCHORS': [  # anchors for three scale, be careful to change it!!!
        [
            (1.25, 1.625),
            (2.0, 3.75),
            (4.125, 2.875),
        ],  # Anchors for small obj(12,16),(19,36),(40,28)
        [
            (1.875, 3.8125),
            (3.875, 2.8125),
            (3.6875, 7.4375),
        ],  # Anchors for medium obj(36,75),(76,55),(72,146)
        [(3.625, 2.8125), (4.875, 6.1875), (11.65625, 10.1875)],
    ],  # Anchors for big obj(142,110),(192,243),(459,401)
    'STRIDES': [8, 16, 32],
    'ANCHORS_PER_SCLAE': 3,
    'TRANSFORMER_BLOCKS': 3,  # 堆叠层数，主实验用3
    'TRANSFORMER_HEADS': 8,  # 多头数，必须能整除hidden_feature
}

# 在训练过程中使用预训练权重
PRETRAIN = {
    'BACKBONE_PRETRAINED': True,  # 是否使用预训练的骨干网络
    'PRETRAINED_PATH': os.path.join('weights', 'darknet53_448.weights'),  # 预训练权重路径
}

# 创建配置类，将所有配置封装到一个对象中供导入使用
class _ModelConfig:
    def __init__(self):
        self.PROJECT_PATH = PROJECT_PATH
        self.DATA_PATH = DATA_PATH
        self.VOC_IMGS_PATH = VOC_IMGS_PATH
        self.TRAIN = TRAIN
        self.VAL = VAL
        self.Customer_DATA = Customer_DATA
        self.MODEL = MODEL
        self.PRETRAIN = PRETRAIN

# 创建可导入的全局配置对象
cfg = _ModelConfig()
