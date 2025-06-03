import subprocess

import torch

if torch.cuda.is_available():
    print(f"可用 GPU 数量: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"GPU 索引 {i}: {torch.cuda.get_device_name(i)}")
else:
    print("没有可用的 CUDA 设备")

import torch

# 模拟预测值和标签（错误类型）
pred = torch.randn(2, 5).cuda()  # [batch_size=2, num_classes=5]
label = torch.tensor([1, 0], dtype=torch.int32).cuda()  # Int 类型

# 尝试计算损失（会报错）
try:
    loss = torch.nn.CrossEntropyLoss()(pred, label)
except Exception as e:
    print("错误触发:", e)

# 修复后（转为 Long）
label_fixed = label.long()
loss = torch.nn.CrossEntropyLoss()(pred, label_fixed)
print("运行成功！Loss值:", loss.item())

subprocess.run(["python", "-c", "import sys; print(sys.executable)"])