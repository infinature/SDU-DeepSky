import os
import numpy as np
import torch
import cv2
import base64
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import time
import json
from PIL import Image
import io

# 导入模型和工具
import config.model_config as cfg
from model.model import BuildModel
import utils.gpu as gpu
from utils.fits_operator import save_bbox_img

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # 允许跨域请求

# 全局变量
MODEL = None
DEVICE = None
OUTPUT_DIR = 'detection_results'
UPLOAD_FOLDER = 'uploads'
SAMPLE_DATA_DIR = 'sample_datasets' # 新增：存放预定义数据集的目录
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SAMPLE_DATA_DIR, exist_ok=True) # 新增：创建数据集目录

def load_model(weight_path, device):
    """加载预训练模型"""
    print(f"正在加载模型权重: {weight_path}")
    model = BuildModel().to(device)
    # 加载权重
    if weight_path.endswith('.pt'):
        try:
            model_weights = torch.load(weight_path, map_location=device)
            if isinstance(model_weights, dict) and 'model' in model_weights:
                # 从检查点加载模型部分
                model.load_state_dict(model_weights['model'])
                print(f"从检查点加载模型成功，Epoch: {model_weights.get('epoch', 'unknown')}")
            else:
                # 直接加载整个模型
                model.load_state_dict(model_weights)
                print("加载模型权重成功")
        except Exception as e:
            print(f"加载模型权重失败: {str(e)}")
            raise
    
    model.eval()  # 设置为评估模式
    return model

def initialize_model(weight_path=None):
    """初始化模型"""
    global MODEL, DEVICE
    
    # 使用GPU如果可用
    device_id = 0  # 使用第一个可用的GPU (通常是0)
    device = gpu.select_device(device_id)
    DEVICE = device
    
    # 加载模型
    if weight_path is None or not os.path.exists(weight_path):
        # 默认使用上层目录的best.pt模型文件
        weight_path = '../best.pt'  
        if not os.path.exists(weight_path):
            # 尝试使用当前目录
            weight_path = 'best.pt'
            if not os.path.exists(weight_path):
                # 尝试使用绝对路径
                weight_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'best.pt')
                if not os.path.exists(weight_path):
                    print(f"错误：未找到默认权重文件 'best.pt'")
                    return False
    
    try:
        print(f"正在加载权重文件: {weight_path}")
        MODEL = load_model(weight_path, device)
        print("模型初始化完成")
        return True
    except Exception as e:
        print(f"加载模型出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def preprocess_image(image_data, image_type='npy'):
    """预处理图像数据"""
    img_data = None
    if image_type == 'npy':
        if isinstance(image_data, str) and image_data.endswith('.npy'):
            img_data = np.load(image_data, allow_pickle=True)
        elif isinstance(image_data, bytes):
            img_data = np.load(io.BytesIO(image_data), allow_pickle=True)
        elif isinstance(image_data, np.ndarray):
            img_data = image_data
        else:
            raise ValueError("NPY image_data is not a file path, bytes, or numpy array.")

        if not isinstance(img_data, np.ndarray):
            raise ValueError("NPY data could not be loaded as a NumPy array.")

        if len(img_data.shape) == 3 and img_data.shape[0] in [1, 3]:
            img_data = np.transpose(img_data, (1, 2, 0))
        elif len(img_data.shape) == 2:
            img_data = np.expand_dims(img_data, axis=-1)
        
        if img_data.dtype != np.uint8:
            img_data = img_data.astype(np.float32)
            min_val = np.min(img_data)
            max_val = np.max(img_data)
            if max_val > min_val:
                img_data = (img_data - min_val) / (max_val - min_val) * 255.0
            elif max_val == min_val and max_val > 1.0:
                 img_data = np.full_like(img_data, 128.0 if max_val > 0 else 0.0)
            elif max_val == min_val and max_val <=1.0 and max_val >=0:
                 img_data = img_data * 255.0
            else: 
                img_data = np.zeros_like(img_data)
            img_data = np.clip(img_data, 0, 255)
            img_data = img_data.astype(np.uint8)

        if img_data.ndim == 2 or img_data.shape[2] == 1:
            original_img_bgr = cv2.cvtColor(img_data, cv2.COLOR_GRAY2BGR)
        elif img_data.shape[2] == 3:
            original_img_bgr = cv2.cvtColor(img_data, cv2.COLOR_RGB2BGR)
        else:
            raise ValueError(f"NPY image has unsupported shape for BGR conversion: {img_data.shape}")

    elif image_type in ['jpg', 'jpeg', 'png']:
        if isinstance(image_data, str):
            original_img_bgr = cv2.imread(image_data)
            if original_img_bgr is None:
                raise ValueError(f"Could not read image file: {image_data}")
        elif isinstance(image_data, bytes):
            nparr = np.frombuffer(image_data, np.uint8)
            original_img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if original_img_bgr is None:
                raise ValueError("Could not decode image from bytes.")
        else:
            raise ValueError("Unsupported image_data type for JPG/PNG.")
    else:
        raise ValueError(f"Unsupported image_type: {image_type}")
    
    original_shape = original_img_bgr.shape[:2]
    
    input_size = cfg.VAL["TEST_IMG_SIZE"]
    resized_img_bgr = cv2.resize(original_img_bgr, (input_size, input_size), interpolation=cv2.INTER_LINEAR)
    resized_img_rgb_for_model = cv2.cvtColor(resized_img_bgr, cv2.COLOR_BGR2RGB)
    
    return original_img_bgr, resized_img_rgb_for_model, original_shape

def detect(model, image, conf_thresh=0.3, device='cuda'):
    """使用模型检测图像中的目标"""
    # 转换为PyTorch张量
    img = torch.from_numpy(image).permute(2, 0, 1).float().div(255.0).unsqueeze(0)
    img = img.to(device)
    
    # 进行预测
    with torch.no_grad():
        outputs, _ = model(img)
    
    # 定义锚点盒和步长 (从模型配置中获取)
    import config.model_config as cfg
    anchors = cfg.MODEL['ANCHORS']
    strides = cfg.MODEL['STRIDES']
    input_size = cfg.VAL["TEST_IMG_SIZE"]
    
    # 处理预测结果
    predictions = []
    
    try:
        # 直接使用YOLO模型输出进行解码和坐标转换
        # 遇到的问题是坐标转换，可能导致边界框不准确
        for i, output in enumerate(outputs):
            # 获取参数
            anchors_scale = anchors[i]
            stride = strides[i]
            
            # 获取输出形状
            batch_size, grid_h, grid_w, num_anchors, box_attrs = output.shape
            
            # 将预测展平用于处理
            pred = output.reshape(batch_size, -1, box_attrs)[0]  # 取第一个批次
            
            # 使用sigmoid对置信度和类别预测进行激活
            pred_conf = torch.sigmoid(pred[:, 4])
            pred_cls = torch.sigmoid(pred[:, 5:6])  # 只有一个类别
            
            # 获取高置信度预测
            mask = pred_conf > conf_thresh
            
            # 如果没有高置信度预测，继续下一个尺度
            if not torch.any(mask):
                continue
                
            # 提取高置信度预测
            pred_boxes = pred[mask][:, :4]  # 所有高置信度的盒子预测值
            pred_conf_filtered = pred_conf[mask]
            pred_cls_filtered = pred_cls[mask]
            
            # 计算网格索引和锚点索引
            grid_indices = torch.arange(grid_h * grid_w * num_anchors, device=output.device)
            grid_indices = grid_indices[mask]
            
            # 将索引转换为网格坐标和锚点索引
            anchor_indices = grid_indices % num_anchors
            grid_indices = grid_indices // num_anchors
            grid_x = grid_indices % grid_w
            grid_y = grid_indices // grid_w
            
            # 获取当前尺度的锚点盒
            anchors_tensor = torch.tensor(anchors_scale, device=output.device)
            anchors_w = anchors_tensor[anchor_indices, 0]
            anchors_h = anchors_tensor[anchor_indices, 1]
            
            # YOLO坐标解码：将预测值转换为实际坐标
            # 系数变换，注意这里是根据训练数据进行调整
            # bx = sigmoid(tx) + cx
            # by = sigmoid(ty) + cy
            # bw = pw * exp(tw)
            # bh = ph * exp(th)
            x_center = (torch.sigmoid(pred_boxes[:, 0]) + grid_x.float()) * stride
            y_center = (torch.sigmoid(pred_boxes[:, 1]) + grid_y.float()) * stride
            w = torch.exp(pred_boxes[:, 2]) * anchors_w * stride
            h = torch.exp(pred_boxes[:, 3]) * anchors_h * stride
            
            # 转换为左上角和右下角坐标
            x1 = x_center - w / 2
            y1 = y_center - h / 2
            x2 = x_center + w / 2
            y2 = y_center + h / 2
            
            # 转换为 numpy 数组用于后续处理
            boxes_np = torch.stack([x1, y1, x2, y2], dim=1).cpu().numpy()
            scores_np = pred_conf_filtered.cpu().numpy()
            labels_np = torch.argmax(pred_cls_filtered, dim=1).cpu().numpy()
            
            # 将检测框添加到 predictions 列表中
            for j in range(len(boxes_np)):
                x1, y1, x2, y2 = boxes_np[j]
                # 确保坐标在图像范围内
                x1 = max(0, min(input_size, x1))
                y1 = max(0, min(input_size, y1))
                x2 = max(0, min(input_size, x2))
                y2 = max(0, min(input_size, y2))
                
                # 确保边界框大小合理
                if x2 - x1 > 0 and y2 - y1 > 0:
                    score = scores_np[j]
                    label = labels_np[j]
                    predictions.append([float(x1), float(y1), float(x2), float(y2), float(score), int(label)])
        
        print(f"YOLO模型检测到 {len(predictions)} 个目标")
        
        # 如果模型没有检测到目标，使用辅助检测方法
        if len(predictions) == 0:
            print("未找到,请使用更优的权重文件")
    
    except Exception as e:
        print(f"检测失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 如果没有检测到任何目标，直接返回空列表
    if len(predictions) == 0:
        print("未检测到目标")
        return predictions
    
    # 去除重复框
    if len(predictions) > 1:
        # 使用NMS合并重叠框，但使用高IoU阈值，只移除非常相似的框
        predictions = apply_nms(predictions, iou_thresh=0.9)  # 使用高阈值只合并非常相似的框
    
    # 输出每个框的信息用于调试
    for i, box in enumerate(predictions):
        print(f"绘制框 {i+1}: ({int(box[0])},{int(box[1])},{int(box[2])},{int(box[3])}) score={box[4]:.2f}")
    
    print(f"保留 {len(predictions)} 个检测框")
    return predictions


def apply_nms(boxes, iou_thresh=0.5):
    """应用非极大值抑制(NMS)算法合并重叠框"""
    if len(boxes) <= 1:
        return boxes
    
    # 提取置信度和坐标
    scores = np.array([box[4] for box in boxes])
    coords = np.array([[box[0], box[1], box[2], box[3]] for box in boxes])
    classes = np.array([box[5] for box in boxes])
    
    # 按置信度降序排序
    order = scores.argsort()[::-1]
    keep = []
    
    # 工具函数：计算IoU
    def calc_iou(box1, box2):
        # 计算交集区域
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        # 计算交集区域面积
        inter_area = max(0, x2 - x1) * max(0, y2 - y1)
        
        # 计算两个框的面积
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        
        # 计算IoU
        iou = inter_area / (box1_area + box2_area - inter_area + 1e-8)
        return iou
    
    while len(order) > 0:
        # 选取当前置信度最高的框
        i = order[0]
        keep.append(i)
        
        # 计算与其他框的IoU
        ious = np.array([calc_iou(coords[i], coords[order[j]]) for j in range(1, len(order))])
        
        # 保留IoU低于阈值的框
        keep_indices = np.where(ious < iou_thresh)[0] + 1
        order = order[keep_indices]
    
    # 根据保留的索引重建检测框列表
    nms_boxes = [boxes[i] for i in keep]
    return nms_boxes


# 移除中心优先函数

def scale_boxes(boxes, original_shape, input_shape):
    """将检测框从模型输入尺寸缩放回原始图像尺寸"""
    # 计算缩放比例
    h_scale = original_shape[0] / input_shape
    w_scale = original_shape[1] / input_shape
    
    # 应用缩放
    scaled_boxes = []
    for box in boxes:
        x1, y1, x2, y2, score, class_id = box
        x1 *= w_scale
        x2 *= w_scale
        y1 *= h_scale
        y2 *= h_scale
        scaled_boxes.append([float(x1), float(y1), float(x2), float(y2), float(score), int(class_id)])
    
    return scaled_boxes

def draw_boxes(image, boxes, class_names=None):
    """在图像上绘制检测框"""
    # 如果没有类别名称，使用默认类别
    if class_names is None:
        class_names = ["bhb"]
    
    # 准备绘制树的图像副本
    image_with_boxes = image.copy()
    
    # 生成不同颜色用于不同类别
    colors = [(0, 255, 0)]  # 初始颜色为绿色
    
    # 遍历每个框并绘制
    print(f"绘制 {len(boxes)} 个检测框")
    for i, box in enumerate(boxes):
        # 解包框信息
        x1, y1, x2, y2, score, class_id = box
        
        # 转换为整数坐标
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        class_id = int(class_id)
        
        # 确保类别索引在范围内
        if class_id < 0:
            class_id = 0
        if class_id >= len(class_names):
            class_id = len(class_names) - 1
        
        # 检查坐标是否有效
        if x1 >= x2 or y1 >= y2 or x1 < 0 or y1 < 0 or x2 >= image.shape[1] or y2 >= image.shape[0]:
            print(f"跳过无效边界框: {x1},{y1},{x2},{y2}")
            continue
            
        # 绘制矩形框
        line_thickness = 2
        cv2.rectangle(image_with_boxes, (x1, y1), (x2, y2), colors[0], line_thickness)
        
        # 将标签简化为只显示类别名
        label = class_names[class_id]
        
        # 计算文本尺寸，根据边界框的大小调整字体大小
        box_width = x2 - x1
        box_height = y2 - y1
        
        # 动态调整字体大小 - 更小的字体
        # 对于小盒子使用小字体，大盒子使用适中字体
        font_size_factor = min(box_width, box_height) / 40.0  # 根据边界框大小动态调整
        font_scale = max(0.3, min(0.5, font_size_factor))  # 限制字体大小范围
        font_thickness = 1  # 减小线条宽度
        
        # 参数设置
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # 获取文本大小
        (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, font_thickness)
        
        # 计算文本背景区域，使它刚好合适
        text_offset_x = x1
        text_offset_y = y1 - 2
        
        # 确保文本在图像范围内
        if text_offset_y < text_height:
            text_offset_y = y1 + text_height + 2
        
        # 绘制文本背景
        cv2.rectangle(image_with_boxes, (text_offset_x, text_offset_y - text_height), 
                     (text_offset_x + text_width, text_offset_y), colors[0], -1)
        
        # 绘制文本
        cv2.putText(image_with_boxes, label, (text_offset_x, text_offset_y), 
                   font, font_scale, (0, 0, 0), font_thickness)
    
    return image_with_boxes

def process_single_image(image_data, image_type='jpg', confidence=0.3):
    """处理单张图像并返回检测结果"""
    global MODEL, DEVICE
    
    if MODEL is None:
        if not initialize_model():
             return {
                'status': 'error',
                'message': '模型初始化失败',
                'boxes': [],
                'original_image': None,
                'result_image': None,
                'detection_count': 0
            }
            
    original_img_bgr = None
    original_img_base64 = None

    try:
        try:
            original_img_bgr, resized_img_rgb_for_model, original_shape = preprocess_image(image_data, image_type)
            _, buffer_orig = cv2.imencode('.png', original_img_bgr)
            original_img_base64 = base64.b64encode(buffer_orig).decode('utf-8')
        except Exception as e_preprocess:
            print(f"图像预处理错误: {str(e_preprocess)}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'message': f'图像预处理失败: {str(e_preprocess)}',
                'boxes': [],
                'original_image': None,
                'result_image': None,
                'detection_count': 0
            }

        boxes = detect(MODEL, resized_img_rgb_for_model, conf_thresh=confidence, device=DEVICE)
        
        input_size = cfg.VAL["TEST_IMG_SIZE"]
        scaled_boxes = scale_boxes(boxes, original_shape, input_size)
        
        class_names = cfg.Customer_DATA["CLASSES"]
        result_img_with_boxes_bgr = draw_boxes(original_img_bgr.copy(), scaled_boxes, class_names)
        
        _, buffer_result = cv2.imencode('.png', result_img_with_boxes_bgr)
        result_img_base64 = base64.b64encode(buffer_result).decode('utf-8')
        
        formatted_boxes = []
        for i, box_data in enumerate(scaled_boxes):
            x1, y1, x2, y2, conf, class_id_val = box_data
            formatted_boxes.append({
                'id': i + 1,
                'confidence': float(conf),
                'x1': float(x1),
                'y1': float(y1),
                'x2': float(x2),
                'y2': float(y2),
                'class_id': int(class_id_val)
            })
        
        print(f"返回检测框格式化结果: {formatted_boxes}")
        
        return {
            'status': 'success',
            'boxes': formatted_boxes,
            'original_image': original_img_base64,
            'result_image': result_img_base64,
            'detection_count': len(scaled_boxes)
        }
    
    except Exception as e_process:
        print(f"处理图像时出错 (检测/绘制阶段): {str(e_process)}")
        import traceback
        traceback.print_exc()
        return {
            'status': 'error',
            'message': f'图像处理失败 (检测/绘制阶段): {str(e_process)}',
            'boxes': [],
            'original_image': original_img_base64,
            'result_image': original_img_base64,
            'detection_count': 0
        }

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/single_detect')
def single_detect_page():
    """单图检测页面"""
    return render_template('single_detect.html')

@app.route('/batch_detect')
def batch_detect_page():
    """批量检测页面"""
    return render_template('batch_detect.html')

@app.route('/results')
def results_page():
    """结果查看页面"""
    return render_template('results.html')

@app.route('/api/detect', methods=['POST'])
def api_detect():
    """单图检测API端点"""
    print("接收到检测请求")
    print(f"请求类型: {request.content_type}")
    print(f"请求表单数据: {request.form}")
    print(f"请求文件: {request.files}")
    
    # 处理权重文件（如果有的话）
    custom_weight_path = None
    if 'weight_file' in request.files:
        weight_file = request.files['weight_file']
        if weight_file.filename != '':
            # 创建临时目录来存储上传的权重文件
            weights_dir = os.path.join(UPLOAD_FOLDER, 'weights')
            os.makedirs(weights_dir, exist_ok=True)
            
            # 保存权重文件
            weight_filename = secure_filename(weight_file.filename)
            custom_weight_path = os.path.join(weights_dir, weight_filename)
            weight_file.save(custom_weight_path)
            print(f"权重文件已保存至: {custom_weight_path}")
            
            # 加载自定义权重模型
            if not initialize_model(custom_weight_path):
                return jsonify({
                    'status': 'error',
                    'message': '加载自定义权重文件失败'
                }), 400
    
    # 处理application/x-www-form-urlencoded格式的请求（示例图片请求）
    if request.content_type and 'application/x-www-form-urlencoded' in request.content_type:
        print("处理表单编码的请求")
        # 获取示例图片路径
        sample_path = request.form.get('sample_path')
        if not sample_path:
            return jsonify({'error': '请求中没有指定图片路径'}), 400
            
        # 获取参数
        image_type = request.form.get('image_type', 'jpg')
        try:
            confidence = float(request.form.get('confidence', 0.3))
        except:
            confidence = 0.3
            
        print(f"处理示例图片: {sample_path}, 类型: {image_type}, 置信度: {confidence}")
        
        # 验证文件路径存在
        actual_path = sample_path
        if not os.path.exists(actual_path) and sample_path.startswith('/'):
            # 尝试使用应用根路径作为基准
            actual_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), sample_path.lstrip('/'))
            print(f"尝试访问绝对路径: {actual_path}")
        
        if not os.path.exists(actual_path):
            return jsonify({'status': 'error', 'message': f'文件不存在: {sample_path}'}), 400
            
        # 根据图片类型处理
        try:
            if image_type == 'npy':
                try:
                    result = process_single_image(actual_path, 'npy', confidence)
                except Exception as e:
                    print(f"NPY处理错误: {str(e)}")
                    # 尝试直接加载文件内容
                    with open(actual_path, 'rb') as f:
                        npy_bytes = f.read()
                    result = process_single_image(npy_bytes, 'npy', confidence)
            else:
                try:
                    with open(actual_path, 'rb') as f:
                        image_bytes = f.read()
                    result = process_single_image(image_bytes, 'jpg', confidence)
                except Exception as e:
                    print(f"读取图片文件错误: {str(e)}")
                    # 尝试直接传递路径
                    result = process_single_image(actual_path, 'jpg', confidence)
            
            return jsonify(result)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"处理示例图片错误: {str(e)}")
            return jsonify({'status': 'error', 'message': f'处理图片错误: {str(e)}'}), 400
            
    # 处理multipart/form-data格式的请求
    elif request.content_type and 'multipart/form-data' in request.content_type:
        # 先检查是否有file_path参数（用于模板文件或静态文件）
        if 'file_path' in request.form:
            file_path = request.form.get('file_path')
            file_name = request.form.get('file_name', '')
            print(f"处理文件路径: {file_path}, 文件名: {file_name}")
            
            # 获取参数
            image_type = request.form.get('image_type', 'jpg')
            try:
                confidence = float(request.form.get('confidence', 0.3))
            except:
                confidence = 0.3
                
            # 验证文件路径存在 - 改进的路径处理逻辑
            # 尝试定位到真实样本文件
            
            # 准备真实样本文件名
            # 如果文件名同 file_X 这样的模式，使用真实的样本文件
            sample_files = [
                'SDSS_1.2376611256069e+18_rgb.jpg',
                'SDSS_1.2376618718633e+18_rgb.jpg',
                'SDSS_1.2376546407598e+18_rgb.jpg',
                'SDSS_1237648673968291868_rgb.jpg',
                'SDSS_1237668572011365559.npy',
                'SDSS_1237668572011429966.npy',
                'SDSS_1237668572011626616.npy',
                'SDSS_1237668572011757764.npy'
            ]
            
            use_real_sample = False
            file_base_name = os.path.basename(file_path)
            file_number = -1
            
            # 如果是 file_1, file_2 这样的文件名，尝试用真实样本替换
            if file_base_name.startswith('file_') and file_base_name[5:].isdigit():
                try:
                    file_number = int(file_base_name[5:]) - 1  # 替换为真实样本索引
                    if 0 <= file_number < len(sample_files):
                        use_real_sample = True
                        print(f"将照样模式文件 {file_base_name} 替换为真实样本 {sample_files[file_number]}")
                except ValueError:
                    pass
            
            if use_real_sample:
                # 尝试找到真实样本文件
                real_sample_name = sample_files[file_number]
                real_sample_paths = [
                    os.path.join('sample_images', real_sample_name),
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_images', real_sample_name)
                ]
                
                for path in real_sample_paths:
                    print(f"尝试真实样本路径: {path}")
                    if os.path.exists(path):
                        actual_path = path
                        print(f"成功找到真实样本文件: {actual_path}")
                        break
            
            # 如果没有找到真实样本，继续尝试常规路径
            if not use_real_sample or not actual_path:
                # 尝试多种可能的路径
                possible_paths = [
                    file_path,  # 原始路径
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path),  # 应用根目录 + 路径
                    os.path.join('static', file_path) if not file_path.startswith('static') else file_path,  # static + 路径
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', file_path) if not file_path.startswith('static') else os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path),  # 应用根目录 + static + 路径
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path.lstrip('/')),  # 应用根目录 + 去除开头斜杠的路径
                    os.path.join('sample_images', os.path.basename(file_path)),  # sample_images + 文件名
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_images', os.path.basename(file_path))  # 应用根目录 + sample_images + 文件名
                ]
                
                # 尝试每一个可能的路径
                for path in possible_paths:
                    print(f"尝试目录: {path}")
                    if os.path.exists(path):
                        actual_path = path
                        print(f"找到有效路径: {actual_path}")
                        break
            
            # 如果所有尝试都失败，使用默认样本
            if not actual_path:
                # 使用一个默认的样本文件
                fallback_sample = 'SDSS_1.2376611256069e+18_rgb.jpg'  # 默认样本
                default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_images', fallback_sample)
                
                if os.path.exists(default_path):
                    print(f"使用默认样本文件: {default_path}")
                    actual_path = default_path
                else:
                    # 如果连默认样本都找不到，返回错误
                    return jsonify({'status': 'error', 'message': f'无法找到有效的样本文件: {file_path}'}), 400
                
            try:
                # 读取文件内容
                with open(actual_path, 'rb') as f:
                    file_content = f.read()
                    
                # 处理图片
                result = process_single_image(file_content, image_type, confidence)
                return jsonify(result)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"处理文件路径错误: {str(e)}")
                return jsonify({'status': 'error', 'message': f'处理文件错误: {str(e)}'}), 400
                
        # 检查是否有文件上传
        elif 'file' not in request.files:
            return jsonify({'error': '请求中没有文件或文件路径'}), 400
            
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({'error': '无效的文件名'}), 400
            
        # 获取参数
        image_type = request.form.get('image_type', 'jpg')
        if file.filename.lower().endswith('.npy'):
            image_type = 'npy'
            
        try:
            confidence = float(request.form.get('confidence', 0.3))
        except:
            confidence = 0.3
            
        # 读取文件内容
        file_content = file.read()
            
        try:
            # 处理图片
            result = process_single_image(file_content, image_type, confidence)
            return jsonify(result)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"处理上传文件错误: {str(e)}")
            return jsonify({'status': 'error', 'message': f'处理文件错误: {str(e)}'}), 400
            
    # 处理JSON格式的请求
    elif request.is_json:
        # 检查请求
        if 'image' not in request.json and 'image_path' not in request.json:
            return jsonify({'error': '请求中没有图像数据'}), 400
        
        # 获取参数
        image_type = request.json.get('image_type', 'jpg')
        confidence = float(request.json.get('confidence', 0.3))
        
        # 处理示例图片路径
        if 'image_path' in request.json:
            image_path = request.json.get('image_path')
            print(f"处理示例图片: {image_path}")
            
            # 验证文件路径存在
            if not os.path.exists(image_path):
                # 尝试使用应用根路径作为基准
                actual_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), image_path.lstrip('/'))
                print(f"尝试访问绝对路径: {actual_path}")
                
                if not os.path.exists(actual_path):
                    return jsonify({'status': 'error', 'message': f'文件不存在: {image_path}'}), 400
                else:
                    image_path = actual_path
            
            # 根据图片类型处理
            try:
                print(f"准备处理图片: {image_path}, 类型: {image_type}")
                
                if image_type == 'npy':
                    try:
                        result = process_single_image(image_path, 'npy', confidence)
                    except Exception as e:
                        print(f"NPY处理错误: {str(e)}")
                        # 尝试直接加载文件内容
                        with open(image_path, 'rb') as f:
                            npy_bytes = f.read()
                        result = process_single_image(npy_bytes, 'npy', confidence)
                else:
                    try:
                        with open(image_path, 'rb') as f:
                            image_bytes = f.read()
                        result = process_single_image(image_bytes, 'jpg', confidence)
                    except Exception as e:
                        print(f"读取图片文件错误: {str(e)}")
                        # 尝试直接传递路径
                        result = process_single_image(image_path, 'jpg', confidence)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"处理示例图片错误: {str(e)}")
                return jsonify({'status': 'error', 'message': f'处理图片错误: {str(e)}'}), 400
        
        # 处理上传的图片
        elif 'image' in request.json:
            image_data = request.json.get('image')
            
            # 处理BASE64编码的图像
            if isinstance(image_data, str) and image_data.startswith('data:'):
                # 从DATA URI中提取BASE64数据
                image_data = image_data.split(',')[1]
            
            # 解码BASE64数据
            try:
                image_bytes = base64.b64decode(image_data)
                result = process_single_image(image_bytes, image_type, confidence)
            except Exception as e:
                print(f"解码图片错误: {str(e)}")
                return jsonify({'status': 'error', 'message': f'图片解码错误: {str(e)}'}), 400
        
        return jsonify(result)
    
    # 不支持的请求类型
    return jsonify({'error': '不支持的请求格式'}), 415

@app.route('/api/batch_detect', methods=['POST'])
def api_batch_detect():
    """批量检测API端点"""
    print("接收到批量检测请求")
    print(f"请求内容键: {list(request.files.keys())}")
    print(f"表单内容键: {list(request.form.keys())}")
    
    # 处理权重文件（如果有的话）
    custom_weight_path = None
    if 'weight_file' in request.files:
        weight_file = request.files['weight_file']
        if weight_file.filename != '':
            # 创建临时目录来存储上传的权重文件
            weights_dir = os.path.join(UPLOAD_FOLDER, 'weights')
            os.makedirs(weights_dir, exist_ok=True)
            
            # 保存权重文件
            weight_filename = secure_filename(weight_file.filename)
            custom_weight_path = os.path.join(weights_dir, weight_filename)
            weight_file.save(custom_weight_path)
            print(f"权重文件已保存至: {custom_weight_path}")
            
            # 加载自定义权重模型
            if not initialize_model(custom_weight_path):
                return jsonify({
                    'status': 'error',
                    'message': '加载自定义权重文件失败'
                }), 400
    
    # 检查请求中是否有文件
    if 'images[]' not in request.files:
        print("请求中没有图像文件")
        return jsonify({'status': 'error', 'message': '请求中没有图像文件'}), 400
    
    # 获取参数
    files = request.files.getlist('images[]')
    print(f"接收到文件数量: {len(files)}")
    for i, file in enumerate(files):
        print(f"文件 {i+1}: {file.filename}, 类型: {file.content_type}")
    
    try:
        confidence = float(request.form.get('confidence', 0.3))
        print(f"置信度阈值设置为: {confidence}")
    except ValueError as e:
        print(f"置信度参数错误: {str(e)}")
        confidence = 0.3
    
    # detection_mode = request.form.get('detection_mode', 'bbox') # 根据需要处理
    # save_results = request.form.get('save_results', 'true').lower() == 'true' # 根据需要处理

    task_id = f"task_{int(time.time())}"
    task_dir = os.path.join(OUTPUT_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    results = []
    detection_count = 0
    
    # 处理每个文件
    print(f"开始处理 {len(files)} 个文件")
    for i, file in enumerate(files):
        print(f"\n处理文件 {i+1}/{len(files)}: {file.filename}")
        try:
            # 读取文件内容
            file_content = file.read()
            print(f"文件内容大小: {len(file_content)} 字节")
            
            # 确定文件类型
            filename = file.filename
            orig_image_type = 'npy' if filename.lower().endswith('.npy') else 'jpg'
            image_type = orig_image_type
            print(f"文件类型: {image_type}")
            
            # 处理图像
            try:
                print(f"开始调用process_single_image处理图像")
                result = process_single_image(file_content, image_type, confidence)
            except Exception as e:
                print(f"首次处理图像失败: {str(e)}")
                # 如果第一次处理失败，尝试切换图像类型
                image_type = 'jpg' if orig_image_type == 'npy' else 'npy'
                print(f"尝试切换图像类型为 {image_type}")
                result = process_single_image(file_content, image_type, confidence)
            
            # 如果成功，保存结果
            if result['status'] == 'success':
                # 生成结果文件名
                result_filename = f"{os.path.splitext(filename)[0]}_result.png"
                result_path = os.path.join(task_dir, result_filename)
                
                # 保存结果图像
                with open(result_path, 'wb') as f:
                    f.write(base64.b64decode(result['result_image']))
                
                # 更新检测计数
                detection_count += result['detection_count']
                
                # 添加到结果列表
                results.append({
                    'filename': filename,
                    'result_filename': result_filename,
                    'boxes': result['boxes'],
                    'detection_count': result['detection_count']
                })
        
        except Exception as e:
            print(f"处理文件 {file.filename} 时出错: {str(e)}")
            results.append({
                'filename': file.filename,
                'status': 'error',
                'message': str(e)
            })
    
    # 保存任务信息
    task_info = {
        'task_id': task_id,
        'timestamp': time.time(),
        'files_count': len(files),
        'detection_count': detection_count,
        'results': results
    }
    
    with open(os.path.join(task_dir, 'task_info.json'), 'w') as f:
        json.dump(task_info, f, indent=2)
    
    # 返回结果
    return jsonify({
        'status': 'success',
        'task_id': task_id,
        'files_count': len(files),
        'detection_count': detection_count,
        'results': results
    })

@app.route('/api/batch_detect_dataset', methods=['POST'])
def api_batch_detect_dataset():
    """批量检测服务器端数据集的API端点"""
    print("接收到数据集批量检测请求")
    print(f"表单内容键: {list(request.form.keys())}")
    if request.files:
        print(f"文件内容键: {list(request.files.keys())}")

    custom_weight_path = None
    if 'weight_file' in request.files:
        weight_file = request.files['weight_file']
        if weight_file.filename != '':
            weights_dir = os.path.join(UPLOAD_FOLDER, 'weights')
            os.makedirs(weights_dir, exist_ok=True)
            weight_filename = secure_filename(weight_file.filename)
            custom_weight_path = os.path.join(weights_dir, weight_filename)
            weight_file.save(custom_weight_path)
            print(f"权重文件已保存至: {custom_weight_path}")
            if not initialize_model(custom_weight_path):
                return jsonify({'status': 'error', 'message': '加载自定义权重文件失败'}), 400
    
    dataset_name = request.form.get('dataset')
    if not dataset_name:
        return jsonify({'status': 'error', 'message': '未提供数据集名称'}), 400

    dataset_path = os.path.join(SAMPLE_DATA_DIR, dataset_name)
    if not os.path.isdir(dataset_path):
        return jsonify({'status': 'error', 'message': f'数据集 {dataset_name} 不存在或不是一个目录'}), 404

    try:
        confidence = float(request.form.get('confidence', 0.3))
    except ValueError:
        confidence = 0.3
    
    # detection_mode = request.form.get('detection_mode', 'bbox') # 根据需要处理
    # save_results = request.form.get('save_results', 'true').lower() == 'true' # 根据需要处理

    task_id = f"task_{int(time.time())}"
    task_dir = os.path.join(OUTPUT_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    results_summary = []
    total_detection_count = 0
    processed_files_count = 0
    
    image_files_to_process = []
    for filename in os.listdir(dataset_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.fits', '.fit', '.npy')):
            image_files_to_process.append(filename)
    
    print(f"在数据集 {dataset_name} 中找到 {len(image_files_to_process)} 个图像文件进行处理")

    for filename in image_files_to_process:
        file_path = os.path.join(dataset_path, filename)
        try:
            with open(file_path, 'rb') as f_content:
                image_data = f_content.read()
            
            image_type = 'npy' if filename.lower().endswith('.npy') else 'fits' if filename.lower().endswith(('.fits', '.fit')) else 'jpg'
            
            # 调用核心处理函数
            # 注意: process_single_image 可能需要根据 image_type 处理 FITS
            # 当前 process_single_image 主要针对 'jpg' 和 'npy'
            # 如果需要FITS原生支持，process_single_image 或其调用的 preprocess_image 需要增强
            print(f"处理数据集文件: {filename} (类型: {image_type})")
            result = process_single_image(image_data, image_type, confidence)

            if result['status'] == 'success':
                result_img_filename = f"{os.path.splitext(filename)[0]}_result.png"
                result_img_path = os.path.join(task_dir, result_img_filename)
                with open(result_img_path, 'wb') as f_img:
                    f_img.write(base64.b64decode(result['result_image']))
                
                total_detection_count += result['detection_count']
                results_summary.append({
                    'filename': filename,
                    'result_filename': result_img_filename,
                    'boxes': result['boxes'],
                    'detection_count': result['detection_count']
                })
            else:
                 results_summary.append({
                    'filename': filename,
                    'status': 'error',
                    'message': result.get('message', '处理失败')
                })
            processed_files_count += 1
        except Exception as e:
            print(f"处理数据集文件 {filename} 时出错: {str(e)}")
            results_summary.append({
                'filename': filename,
                'status': 'error',
                'message': str(e)
            })
    
    task_info = {
        'task_id': task_id,
        'dataset_name': dataset_name,
        'timestamp': time.time(),
        'files_count': processed_files_count,
        'detection_count': total_detection_count,
        'results': results_summary
    }

    with open(os.path.join(task_dir, 'task_info.json'), 'w') as f_json:
        json.dump(task_info, f_json, indent=2)

    return jsonify({
        'status': 'success',
        'task_id': task_id,
        'dataset_name': dataset_name,
        'files_count': processed_files_count,
        'detection_count': total_detection_count
    })

@app.route('/api/tasks', methods=['GET'])
def api_tasks():
    """获取所有任务列表"""
    tasks = []
    
    # 遍历输出目录
    for task_dir in os.listdir(OUTPUT_DIR):
        task_path = os.path.join(OUTPUT_DIR, task_dir)
        
        # 检查是否是目录
        if os.path.isdir(task_path):
            # 尝试读取任务信息
            info_path = os.path.join(task_path, 'task_info.json')
            if os.path.exists(info_path):
                try:
                    with open(info_path, 'r') as f:
                        task_info = json.load(f)
                    tasks.append(task_info)
                except:
                    # 如果读取失败，添加基本信息
                    tasks.append({
                        'task_id': task_dir,
                        'timestamp': os.path.getctime(task_path)
                    })
            else:
                # 如果没有任务信息文件，添加基本信息
                tasks.append({
                    'task_id': task_dir,
                    'timestamp': os.path.getctime(task_path)
                })
    
    # 按时间戳排序（降序）
    tasks.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    
    return jsonify({
        'status': 'success',
        'tasks': tasks
    })

@app.route('/api/task/<task_id>', methods=['GET'])
def api_task(task_id):
    """获取指定任务的信息"""
    task_path = os.path.join(OUTPUT_DIR, task_id)
    
    # 检查任务是否存在
    if not os.path.isdir(task_path):
        return jsonify({'error': f'任务 {task_id} 不存在'}), 404
    
    # 读取任务信息
    info_path = os.path.join(task_path, 'task_info.json')
    if os.path.exists(info_path):
        try:
            with open(info_path, 'r') as f:
                task_info = json.load(f)
            return jsonify(task_info)
        except:
            return jsonify({'error': f'读取任务信息失败'}), 500
    else:
        return jsonify({'error': f'任务信息文件不存在'}), 404

@app.route('/results/<task_id>/<filename>')
def task_result(task_id, filename):
    """获取任务结果图像"""
    return send_from_directory(os.path.join(OUTPUT_DIR, task_id), filename)

@app.route('/api/samples', methods=['GET'])
def api_samples():
    """获取示例图片列表"""
    # 定义示例图片放在static目录下
    sample_dir = os.path.join(app.static_folder, 'sample_images')
    os.makedirs(sample_dir, exist_ok=True)
    
    samples = []
    
    # 检查static/sample_images目录是否存在示例图片
    if os.path.exists(sample_dir):
        for filename in os.listdir(sample_dir):
            file_path = os.path.join(sample_dir, filename)
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                file_type = 'npy' if file_ext == '.npy' else 'jpg'
                
                samples.append({
                    'id': len(samples) + 1,
                    'name': f'示例图片 {len(samples) + 1}',
                    'path': f'/static/sample_images/{filename}',
                    'type': file_type
                })
    
    # 如果没有示例图片，返回几个默认的URL
    if not samples:
        samples = [
            { 'id': 1, 'name': '星系示例', 'path': '/static/sample_images/SDSS_1.2376611256069e+18_rgb.jpg', 'type': 'jpg' },
            { 'id': 2, 'name': '星云示例', 'path': '/static/sample_images/SDSS_1.2376618718633e+18_rgb.jpg', 'type': 'jpg' },
            { 'id': 3, 'name': 'NPY数据示例', 'path': '/static/sample_images/SDSS_1237668572011365559.npy', 'type': 'npy' }
        ]
    
    return jsonify(samples)

if __name__ == '__main__':
    # 初始化模型
    initialize_model()
    # 启动服务
    app.run(debug=True, host='0.0.0.0', port=5000)
