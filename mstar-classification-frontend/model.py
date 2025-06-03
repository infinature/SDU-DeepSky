import torch
from torch import nn
from torchvision import models
# Removed: from transformers import ViltConfig, ViltModel

# --- 使用标准 PyTorch Transformer 实现 --- #
from torch.nn import TransformerEncoder, TransformerEncoderLayer


# 图像编码器类，用于从测光图像中提取特征
class ImageEncoder(nn.Module):
    # 初始化图像编码器
    def __init__(self):
        super(ImageEncoder, self).__init__()
        # 加载预训练的 ResNet-152 模型
        model = models.resnet152()
        # 去除 ResNet 的最后两层（全局平均池化层和全连接层）
        modules = list(model.children())[:-2]
        self.model = nn.Sequential(*modules)
        # 添加自适应平均池化层，生成 (4, 1) 大小的输出，用于序列特征
        self.pool1 = nn.AdaptiveAvgPool2d(output_size=(4,1))
        # 添加自适应平均池化层，生成 (1, 1) 大小的输出，用于全局特征
        self.pool2 = nn.AdaptiveAvgPool2d(output_size=(1,1))
        # 全连接层，将特征维度映射到 512
        self.fc = nn.Linear(2048, 512)

    # 定义图像编码器的前向传播过程
    def forward(self, x):
        # 通过 ResNet 提取特征
        x = self.model(x)
        # 应用第一个池化层获取序列特征图
        x_pooled1 = self.pool1(x)

        # 将特征图展平成序列，并调整维度顺序 (batch, seq_len, hidden_size)
        img_embeds = torch.flatten(x_pooled1, start_dim=2)
        img_embeds = img_embeds.transpose(1, 2).contiguous()
        # 通过全连接层处理序列特征
        img_embeds = self.fc(img_embeds)

        # 应用第二个池化层获取全局特征图
        img_v_pooled = self.pool2(x)
        # 将全局特征图展平成向量
        img_v = torch.flatten(img_v_pooled, 1)
        # 通过全连接层处理全局特征
        img_v = self.fc(img_v)

        # 返回全局特征向量和序列特征嵌入
        return img_v, img_embeds


# 光谱编码器类，用于从光谱数据中提取特征
class SpecEncoder(nn.Module):
    # 初始化光谱编码器
    def __init__(self):
        super(SpecEncoder, self).__init__()
        # 定义一系列一维卷积层
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=32, kernel_size=4)
        self.conv2 = nn.Conv1d(in_channels=32, out_channels=64, kernel_size=4)
        self.conv3 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=4)
        self.conv4 = nn.Conv1d(in_channels=128, out_channels=256, kernel_size=4)
        self.conv5 = nn.Conv1d(in_channels=256, out_channels=512, kernel_size=4)

        # 定义最大池化层
        self.pool = nn.MaxPool1d(kernel_size=4)
        # 定义自适应平均池化层，生成固定长度 32 的序列输出
        self.advpool1 = nn.AdaptiveAvgPool1d(output_size=32)
        # 定义自适应平均池化层，生成长度为 1 的全局输出
        self.advpool2 = nn.AdaptiveAvgPool1d(output_size=1)
        # 全连接层，将特征维度映射到 512
        self.fc = nn.Linear(512, 512)


    # 定义光谱编码器的前向传播过程
    def forward(self, x):
        # 增加一个通道维度以适应 Conv1d 输入要求 (batch, channels, length)
        x = x.unsqueeze(dim = 1)
        # 依次通过卷积层和池化层
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.pool(x)
        x = self.conv3(x)
        x = self.conv4(x)
        x = self.pool(x)
        x = self.conv5(x)

        # 应用自适应池化层获取序列特征
        spec_embeds = self.advpool1(x)
        # 调整维度顺序 (batch, seq_len, hidden_size)
        spec_embeds = spec_embeds.transpose(1, 2).contiguous()

        # 应用自适应池化层获取全局特征
        spec_v = self.advpool2(x) # Shape: (batch, 512, 1)
        # 明确指定只 squeeze 最后一个维度，确保输出是 (batch, 512)
        spec_v = torch.squeeze(spec_v, dim=-1)
        # 通过全连接层处理全局特征
        spec_v = self.fc(spec_v)

        # 返回全局特征向量和序列特征嵌入
        return spec_v, spec_embeds


# --- 替换 ViltModel 的新多模态模型类 --- #
class FusionModel(nn.Module):
    def __init__(self, num_classes=5, hidden_size=512, num_heads=8, num_layers=8, dropout=0.1):
        super(FusionModel, self).__init__()
        self.hidden_size = hidden_size

        # 实例化编码器
        self.image_encoder = ImageEncoder()
        self.spec_encoder = SpecEncoder()

        # 定义可学习的 [CLS] token
        self.cls_token = nn.Parameter(torch.zeros(1, 1, hidden_size))

        # 定义 Token 类型嵌入 (光谱=0, 图像=1)
        self.token_type_embeddings = nn.Embedding(2, hidden_size)

        # 定义位置嵌入
        # 最大序列长度 = 1 (CLS) + 32 (光谱) + 4 (图像) = 37
        self.max_position_embeddings = 37
        self.position_embeddings = nn.Embedding(self.max_position_embeddings, hidden_size)
        # 或者使用 Parameter: self.position_embeddings = nn.Parameter(torch.zeros(1, self.max_position_embeddings, hidden_size))

        # 定义 Transformer Encoder
        encoder_layer = TransformerEncoderLayer(
            d_model=hidden_size,
            nhead=num_heads,
            dim_feedforward=hidden_size * 4, # 通常是 hidden_size 的 4 倍
            dropout=dropout,
            batch_first=True # 输入形状为 (batch, seq, feature)
        )
        self.transformer_encoder = TransformerEncoder(encoder_layer, num_layers=num_layers)

        # 定义最终的分类器
        self.classifier = nn.Linear(hidden_size, num_classes)

        # 定义对比损失中的温度参数 T
        self.t = 0.07

    def forward(self, specs, imgs):
        # 1. 获取编码器输出
        imgs_v, imgs_embeds = self.image_encoder(imgs) # imgs_embeds: (batch, 4, hidden_size)
        specs_v, specs_embeds = self.spec_encoder(specs) # specs_embeds: (batch, 32, hidden_size)

        # 2. L2 归一化全局特征 (用于对比损失)
        imgs_v = imgs_v / imgs_v.norm(p=2, dim=-1, keepdim=True)
        specs_v = specs_v / specs_v.norm(p=2, dim=-1, keepdim=True)

        # 3. 准备 Transformer 输入
        batch_size = imgs_embeds.shape[0]
        spec_seq_len = specs_embeds.shape[1] # 32
        img_seq_len = imgs_embeds.shape[1]  # 4

        # 添加 CLS token
        cls_token = self.cls_token.expand(batch_size, -1, -1) # (batch, 1, hidden_size)
        specs_embeds_with_cls = torch.cat((cls_token, specs_embeds), dim=1) # (batch, 33, hidden_size)
        cls_spec_seq_len = specs_embeds_with_cls.shape[1] # 33

        # 拼接光谱和图像嵌入
        fused_embeds = torch.cat([specs_embeds_with_cls, imgs_embeds], dim=1) # (batch, 37, hidden_size)

        # 创建 token type ids (光谱+CLS=0, 图像=1)
        spec_type_ids = torch.zeros(batch_size, cls_spec_seq_len, dtype=torch.long, device=fused_embeds.device)
        img_type_ids = torch.ones(batch_size, img_seq_len, dtype=torch.long, device=fused_embeds.device)
        token_type_ids = torch.cat([spec_type_ids, img_type_ids], dim=1) # (batch, 37)

        # 创建 position ids (0 到 36)
        position_ids = torch.arange(self.max_position_embeddings, dtype=torch.long, device=fused_embeds.device)
        position_ids = position_ids.unsqueeze(0).expand(batch_size, -1) # (batch, 37)

        # 获取并添加嵌入
        token_type_embeds = self.token_type_embeddings(token_type_ids)
        position_embeds = self.position_embeddings(position_ids)

        input_embeds = fused_embeds + token_type_embeds + position_embeds

        # (可选) 添加 LayerNorm 和 Dropout，通常在 Transformer 内部完成，但有时也在外部添加
        # input_embeds = self.layer_norm(input_embeds) # 如果需要的话
        # input_embeds = self.dropout(input_embeds)   # 如果需要的话

        # 4. 通过 Transformer Encoder
        # 注意：标准的 nn.TransformerEncoder 不直接处理 padding mask，
        # 如果你的输入序列长度可能变化，需要提供 mask。
        # 在这里，我们的序列长度固定为 37，所以不需要 mask。
        transformer_output = self.transformer_encoder(input_embeds)
        # transformer_output shape: (batch, 37, hidden_size)

        # 5. 提取 CLS token 输出用于分类
        cls_output = transformer_output[:, 0, :] # 取第一个 token (CLS) 的输出

        # 6. 通过分类器
        fuse_logits = self.classifier(cls_output)

        # 7. 计算对比损失所需的对齐 Logits
        align_logits = torch.div(torch.matmul(imgs_v, specs_v.mT), self.t)

        return align_logits , fuse_logits

# --- 保留原始 Model 类定义 (以防万一，或者可以删除) --- #
# class Model(nn.Module):
#     # ... (旧的基于 ViltModel 的代码) ...

# --- 在 train.py 中使用时，需要将 Model() 替换为 FusionModel() --- #




