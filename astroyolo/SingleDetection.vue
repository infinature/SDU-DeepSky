
<template>
  <q-page padding>
    <div class="row justify-center">
      <div class="col-12 col-md-10">
        <div class="text-h5 q-mb-md">单图检测</div>
        
        <!-- 检测参数卡片 -->
        <q-card flat bordered class="q-mb-md">
          <q-card-section>
            <div class="text-subtitle1">检测参数</div>
          </q-card-section>
          
          <q-card-section>
            <div class="row q-col-gutter-md">
              <div class="col-12 col-md-6">
                <q-select
                  v-model="imageType"
                  :options="imageTypes"
                  label="图像类型"
                  outlined
                  dense
                >
                  <template v-slot:prepend>
                    <q-icon name="photo_filter" />
                  </template>
                </q-select>
              </div>
              <div class="col-12 col-md-6">
                <q-slider
                  v-model="confidenceThreshold"
                  :min="0"
                  :max="1"
                  :step="0.01"
                  label
                  label-always
                  color="primary"
                  class="q-mt-lg"
                >
                  <template v-slot:thumb-label>
                    置信度: {{ confidenceThreshold.toFixed(2) }}
                  </template>
                </q-slider>
              </div>
            </div>
          </q-card-section>
        </q-card>
        
        <!-- 文件上传区域 -->
        <q-card flat bordered class="q-my-md">
          <q-card-section>
            <div class="text-subtitle1 q-mb-sm">上传图片</div>
            <p class="text-caption">支持JPG、PNG、TIFF等常见天文图像格式</p>
            
            <q-file
              v-model="selectedFile"
              outlined
              accept="image/*"
              label="选择文件"
              class="q-my-md"
            >
              <template v-slot:prepend>
                <q-icon name="attach_file" />
              </template>
              <template v-slot:hint>
                或者将文件拖放到这里
              </template>
            </q-file>
            
            <!-- 示例选择 -->
            <div class="q-mt-md">
              <div class="text-subtitle2 q-mb-sm">或选择示例图片:</div>
              <div class="row q-col-gutter-md">
                <div 
                  v-for="(sample, index) in sampleImages" 
                  :key="index"
                  class="col-6 col-sm-4 col-md-3"
                >
                  <q-card 
                    class="cursor-pointer" 
                    bordered
                    flat
                    @click="loadSampleImage(index + 1)"
                  >
                    <q-card-section>
                      <div class="text-subtitle2">{{ index === 0 ? '星系示例' : '星云示例' }}</div>
                      <div class="text-caption">点击加载示例图片</div>
                    </q-card-section>
                  </q-card>
                </div>
              </div>
            </div>
          </q-card-section>
          
          <!-- 操作按钮 -->
          <q-card-section>
            <div class="row justify-center q-mt-md">
              <q-btn 
                label="开始检测"
                color="primary"
                icon="search"
                :disable="!selectedFile && !currentSampleImage"
                @click="startDetection()"
                class="q-px-md"
              />            
            </div>
          </q-card-section>
        </q-card>

        <!-- 检测结果区域 -->
        <q-card v-if="detectionResult && !isLoading" flat bordered class="q-mt-md">
          <q-card-section>
            <div class="text-subtitle1 flex items-center">
              <q-icon name="check_circle" class="q-mr-sm" />
              <span>检测结果</span>
              <q-space />
              <q-btn flat round dense icon="close" @click="detectionResult = null" />
            </div>
          </q-card-section>

          <!-- 错误信息 -->
          <q-card-section v-if="detectionError" class="bg-red-1 text-negative">
            <div class="flex items-center">
              <q-icon name="error" size="sm" class="q-mr-sm" />
              <span>{{ detectionError }}</span>
            </div>
          </q-card-section>
          
          <!-- 结果信息 -->
          <q-card-section v-else>
            <div class="row q-col-gutter-md">
              <div class="col-12 col-md-8 q-mb-md">
                <q-img 
                  :src="resultImage" 
                  v-if="resultImage"
                  fit="contain"
                  style="max-height: 400px"
                />
              </div>
              
              <div class="col-12 col-md-4">
                <div class="text-subtitle2 q-mb-sm">检测结果信息</div>
                <q-list bordered separator>
                  <q-item>
                    <q-item-section>
                      <q-item-label>检测数量</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-chip color="primary" text-color="white" size="sm">{{ detectionCount }}</q-chip>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label>置信度阈值</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-chip color="primary" text-color="white" size="sm">{{ confidenceThreshold.toFixed(2) }}</q-chip>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
            </div>
          </q-card-section>
        
          <!-- 检测结果表格 -->
          <q-card-section v-if="detectionBoxes.length > 0" class="q-mt-md">
            <div class="text-subtitle2 q-mb-sm">识别结果</div>
            <q-table
              :rows="detectionBoxes"
              :columns="boxesColumns"
              row-key="id"
              flat
              bordered
              class="q-mb-md"
              :pagination="{rowsPerPage: 5}"
            />
          </q-card-section>
          
          <!-- 操作按钮 -->
          <q-card-actions align="right">
            <q-btn flat label="新的检测" color="primary" @click="detectionResult = null" />
            <q-btn flat label="保存结果" color="primary" @click="saveResult" v-if="resultImage" />
          </q-card-actions>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from 'vue';
import { Notify as QNotify } from 'quasar';
import axios from 'axios';

defineOptions({
  name: 'SingleDetection'
});

// 参数设置
const selectedFile = ref(null);
const weightFile = ref(null); // 添加权重文件引用
const confidenceThreshold = ref(0.6);
const imageType = ref({ label: 'JPG图像', value: 'jpg' });
const imageTypes = [
  { label: 'JPG图像', value: 'jpg' },
  { label: 'PNG图像', value: 'png' },
  { label: 'TIFF图像', value: 'tiff' },
  { label: 'NPY数据', value: 'npy' }
];

// 状态变量
const isLoading = ref(false);
// 不再使用showResult变量控制弹出框，直接使用detectionResult判断是否显示结果
const detectionResult = ref(null); // 新增整个检测结果对象
const resultImage = ref('');
const detectionCount = ref(0);
const detectionBoxes = ref([]);
const detectionError = ref('');

// 表格列定义
const boxesColumns = [
  { name: 'id', label: '序号', field: 'id', align: 'left' },
  { name: 'confidence', label: '置信度', field: 'confidence', format: val => Number(val).toFixed(4), align: 'center' },
  { name: 'x1', label: 'X1', field: 'x1', format: val => Number(val).toFixed(2), align: 'right' },
  { name: 'y1', label: 'Y1', field: 'y1', format: val => Number(val).toFixed(2), align: 'right' },
  { name: 'x2', label: 'X2', field: 'x2', format: val => Number(val).toFixed(2), align: 'right' },
  { name: 'y2', label: 'Y2', field: 'y2', format: val => Number(val).toFixed(2), align: 'right' }
];

// API基础URL
const apiBaseUrl = ref(process.env.API_URL || 'http://localhost:5000');

// 示例图片数据
// 直接使用真实的示例图片路径
const sampleImages = ref([
  { id: 1, name: '星系示例', path: '/sample_images/SDSS_1.2376611256069e+18_rgb.jpg', type: 'jpg', thumbnail: '/sample_images/SDSS_1.2376611256069e+18_rgb_thumb.jpg' },
  { id: 2, name: '星云示例', path: '/sample_images/SDSS_1.2376618718633e+18_rgb.jpg', type: 'jpg', thumbnail: '/sample_images/SDSS_1.2376618718633e+18_rgb_thumb.jpg' },
  { id: 3, name: 'NPY数据示例', path: '/sample_images/SDSS_1237668572011365559.npy', type: 'npy', thumbnail: '/sample_images/SDSS_1237668572011365559_thumb.jpg' }
]);

// 不再使用异步请求获取示例图片列表
const fetchSamples = () => {
  console.log('使用本地示例图片');
  // sampleImages变量已预先设置好了数据
};

// 仍然调用fetchSamples以保持代码结构一致性
fetchSamples();

// 开始检测
const startDetection = async () => {
  if (!selectedFile.value) {
    QNotify.create({
      color: 'negative',
      message: '请选择图片文件',
      position: 'top'
    });
    return;
  }
  
  isLoading.value = true;
  detectionError.value = '';
  detectionResult.value = null; // 清空先前的结果
  
  try {
    // 准备FormData数据
    const formData = new FormData();
    formData.append('file', selectedFile.value);
    formData.append('confidence', confidenceThreshold.value);
    formData.append('image_type', imageType.value.value);
    
    // 如果用户上传了自定义权重文件，则附加到请求中
    if (weightFile.value) {
      formData.append('weight_file', weightFile.value);
    }
    
    // 发送请求到API
    const response = await axios.post(`${apiBaseUrl.value}/api/detect`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    // 处理响应
    if (response.data.status === 'success') {
      // 设置整个结果对象
      detectionResult.value = response.data;
      
      // 设置结果图片 - 注意API返回的是完整URL或base64
      if (response.data.result_image.startsWith('data:')) {
        resultImage.value = response.data.result_image;
      } else if (response.data.result_image.startsWith('/')) {
        resultImage.value = apiBaseUrl.value + response.data.result_image;
      } else {
        resultImage.value = `data:image/png;base64,${response.data.result_image}`;
      }
      
      detectionCount.value = response.data.detection_count || 0;
      
      // 处理检测框
      detectionBoxes.value = response.data.boxes || [];
      
      // 显示成功通知
      QNotify.create({
        color: 'positive',
        message: `检测完成，共发现${detectionCount.value}个目标`,
        position: 'top',
        timeout: 3000
      });
    } else {
      detectionError.value = response.data.message || '检测过程中出现错误';
      detectionResult.value = { status: 'error' }; // 设置为错误状态，使页面显示错误信息
      
      QNotify.create({
        color: 'negative',
        message: detectionError.value,
        position: 'top'
      });
    }
  } catch (error) {
    console.error('检测请求错误', error);
    detectionError.value = error.response?.data?.message || '服务器连接错误';
    detectionResult.value = { status: 'error' }; // 设置为错误状态
    
    QNotify.create({
      color: 'negative',
      message: detectionError.value,
      position: 'top'
    });
  } finally {
    isLoading.value = false;
  }
};

// 加载示例图片
const loadSampleImage = async (sampleId) => {
  const sample = sampleImages.value.find(s => s.id === sampleId);
  if (!sample) return;
  
  // 设置对应的类型
  imageType.value = imageTypes.find(t => t.value === sample.type) || imageTypes[0];
  
  isLoading.value = true;
  detectionError.value = '';
  detectionResult.value = null; // 清空先前的结果
  
  try {
    // 构建请求参数
    const params = new URLSearchParams();
    params.append('sample_path', sample.path);
    params.append('confidence', confidenceThreshold.value);
    params.append('image_type', sample.type);
    
    // 发送请求到API
    const response = await axios.post(`${apiBaseUrl.value}/api/detect`, params);
    
    // 处理响应
    if (response.data.status === 'success') {
      // 设置整个结果对象
      detectionResult.value = response.data;
      
      // 设置结果图片
      if (response.data.result_image.startsWith('data:')) {
        resultImage.value = response.data.result_image;
      } else if (response.data.result_image.startsWith('/')) {
        resultImage.value = apiBaseUrl.value + response.data.result_image;
      } else {
        resultImage.value = `data:image/png;base64,${response.data.result_image}`;
      }
      
      detectionCount.value = response.data.detection_count || 0;
      detectionBoxes.value = response.data.boxes || [];
      
      // 显示成功通知
      QNotify.create({
        color: 'positive',
        message: `示例图片检测完成，共发现${detectionCount.value}个目标`,
        position: 'top',
        timeout: 3000
      });
    } else {
      detectionError.value = response.data.message || '检测示例图片时出现错误';
      detectionResult.value = { status: 'error' }; // 设置为错误状态，使页面显示错误信息
      
      QNotify.create({
        color: 'negative',
        message: detectionError.value,
        position: 'top'
      });
    }
  } catch (error) {
    console.error('示例图片检测请求错误', error);
    detectionError.value = error.response?.data?.message || '服务器连接错误';
    detectionResult.value = { status: 'error' }; // 设置为错误状态
    
    QNotify.create({
      color: 'negative',
      message: detectionError.value,
      position: 'top'
    });
  } finally {
    isLoading.value = false;
  }
};

// 保存结果
const saveResult = () => {
  if (!resultImage.value) return;
  
  // 创建a标签并模拟点击下载
  const a = document.createElement('a');
  a.href = resultImage.value;
  a.download = `detection_result_${new Date().getTime()}.png`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
};

</script>

<style lang="scss" scoped>
// SASS color module now imported via quasar.config.js additionalData

.single-detection-page {
  padding: 32px;
  background-color: $background; // 使用与批量检测相同的纯色背景
  min-height: 100vh;
  position: relative;
}

// 页面标题样式
.page-header {
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: $on-background;
  letter-spacing: 0.5px;
  // 移除深色背景下的文本阴影
}

.page-subtitle {
  font-size: 1rem;
  letter-spacing: 0.3px;
  opacity: 0.8;
}

// 卡片样式
.detection-card {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(15px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
    transform: translateY(-2px);
  }
  
  &.content-card {
    min-height: 400px;
  }
}

// 选择器和滑块样式
.detection-select {
  .q-field__control {
    background-color: rgba(255, 255, 255, 0.05) !important;
  }
}

.light-popup {
  background-color: rgba(14, 23, 41, 0.85) !important;
  color: white !important;
  
  .q-item {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
    margin: 2px 0;
    transition: background-color 0.2s ease;
    
    &:hover {
      background-color: rgba(255, 255, 255, 0.1);
    }
    
    .q-item__label {
      color: $secondary;
    }
  }
}

// 全局修改下拉菜单样式
:deep(.q-menu) {
  background: rgba(14, 23, 41, 0.9) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

:deep(.q-virtual-scroll__content) {
  background: transparent !important;
}

// 下拉选项样式
:deep(.q-item) {
  border-radius: 4px;
  margin: 4px;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1) !important;
  }
  
  &.q-manual-focusable--focused {
    background: rgba($secondary, 0.2) !important;
  }
  
  .q-item__label {
    color: $secondary !important;
    font-weight: 500;
    // 移除深色背景下的文本阴影效果
  }
}

.confidence-slider {
  height: 10px;
}

.slider-label {
  font-size: 0.9rem;
  color: $grey-5;
}

// 面板头部
.panel-header {
  margin-bottom: 1.5rem;
}

// 上传区域样式
.upload-area {
  border: 1px dashed $outline-variant;
  border-radius: 12px;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: $secondary;
  }
  
  .upload-field {
    max-width: 400px;
    margin: 0 auto;
  }
  
  .divider {
    position: relative;
    margin: 20px 0;
    font-weight: 500;
    color: $on-surface-variant;
  }
}

// 按钮样式
.model-btn {
  min-width: 120px;
  font-weight: 500;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba($secondary, 0.5);
  }
}

// 亮色背景下的强调文本效果
.glow-text {
  color: $primary;
  font-weight: 500;
}

.glow-btn {
  box-shadow: 0 2px 5px rgba($primary, 0.3);
  
  &:hover {
    box-shadow: 0 4px 8px rgba($primary, 0.4);
  }
}

// 开始检测按钮
.detection-btn {
  font-weight: 500;
  letter-spacing: 0.5px;
  border-radius: 8px;
  transition: all 0.3s ease;
  
  &:not(:disabled):hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba($secondary, 0.4);
  }
}

// 结果弹窗样式
.result-dialog {
  background: $surface-container-low;
  backdrop-filter: blur(10px);
  border: 1px solid $surface-container-highest;
  color: $on-background;
  
  .result-image {
    max-width: 100%;
    max-height: 60vh;
    border-radius: 8px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  }
  
  .result-list {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    
    .q-item {
      min-height: 48px;
    }
  }
  
  .result-table {
    .q-table__container {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 8px;
    }
    
    thead tr {
      background: rgba($secondary, 0.2);
      th {
        color: $secondary;
        font-weight: 600;
      }
    }
    
    tbody td {
      color: white;
    }
  }
}

// 动画效果
.animation-slide-up {
  animation: slideUp 0.6s ease forwards;
}

@keyframes slideUp {
  from { 
    opacity: 0; 
    transform: translateY(20px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}
</style>
