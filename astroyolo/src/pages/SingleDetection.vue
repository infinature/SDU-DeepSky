<template>
  <div class="page-container">
    <!-- 装饰性背景 -->
    <div class="background-decoration">
      <div class="decoration-circle circle-1"></div>
      <div class="decoration-circle circle-2"></div>
      <div class="decoration-circle circle-3"></div>
    </div>

    <!-- 左侧操作面板 -->
    <div class="left-panel">
      <div class="panel-content">
        <div class="title-wrapper">
          <q-icon name="image_search" size="2.5rem" class="title-icon" />
          <div class="title-text">单图检测</div>
        </div>

        <!-- 检测参数 -->
        <div class="section-wrapper q-mb-md">
          <div class="section-title">检测参数</div>
          <q-select
            v-model="imageType"
            :options="imageTypes"
            label="图像类型"
            outlined
            dense
            class="glass-select q-mb-md"
          >
            <template v-slot:prepend>
              <q-icon name="photo_filter" />
            </template>
          </q-select>
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

        <!-- 文件上传区域 -->
        <div class="section-wrapper q-mb-md">
          <div class="section-title q-mb-sm">上传图片</div>
          <p class="text-caption text-grey-7 q-mb-sm">支持JPG、PNG、TIFF等常见天文图像格式</p>
          <q-file
            v-model="selectedFile"
            outlined
            dense
            accept="image/*"
            label="选择文件或拖拽到此"
            class="glass-uploader q-mb-xs"
            style="min-height: 48px;"
          >
            <template v-slot:prepend>
              <q-icon name="attach_file" />
            </template>
          </q-file>

          <!-- 示例选择 -->
          <div class="q-mt-md">
            <div class="text-subtitle2 q-mb-sm text-grey-8">或选择示例图片:</div>
            <div class="row q-col-gutter-sm">
              <div
                v-for="(sample, index) in sampleImages"
                :key="index"
                class="col-6 col-sm-4"
              >
                <q-card
                  class="cursor-pointer sample-card"
                  flat
                  bordered
                  @click="loadSampleImage(index + 1)"
                  :class="{ 'selected-sample': currentSampleImage && currentSampleImage.id === sample.id }"
                >
                  <q-img :src="sample.thumbnail" :ratio="16/9" >
                    <div class="absolute-bottom text-subtitle2 text-center sample-card-title">
                      {{ sample.name.split('.')[0] }}
                    </div>
                  </q-img>
                </q-card>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <q-btn
          label="开始检测"
          color="primary"
          icon="search"
          :disable="!selectedFile && !currentSampleImage"
          @click="startDetection()"
          class="predict-button full-width q-mt-lg"
          size="lg"
          unelevated
          :loading="isLoading"
        >
          <template v-slot:loading>
            <q-spinner-dots />
          </template>
        </q-btn>
      </div>
    </div>

    <!-- 右侧结果面板 -->
    <div class="right-panel">
      <div class="panel-content">
        <template v-if="detectionResult && !isLoading">
          <div class="result-header">
            <div class="result-title">
              <q-icon name="check_circle_outline" size="2rem" class="result-icon text-positive" />
              <span>检测完成</span>
            </div>
            <div class="result-actions">
              <q-btn flat label="新的检测" color="primary" @click="resetDetectionState" class="action-btn" icon="refresh"/>
              <q-btn flat label="保存结果" color="secondary" @click="saveResult" v-if="resultImage" class="action-btn" icon="save"/>
            </div>
          </div>

          <div v-if="detectionError" class="q-my-md">
            <q-banner inline-actions class="text-white bg-red rounded-borders">
              <template v-slot:avatar>
                <q-icon name="error" color="white" />
              </template>
              {{ detectionError }}
            </q-banner>
          </div>

          <template v-else>
            <div class="row q-col-gutter-lg">
              <div class="col-12 col-lg-7">
                <q-card flat bordered class="result-image-card">
                  <q-card-section class="q-pa-none">
                    <div class="text-subtitle2 q-pa-sm bg-grey-2 text-grey-8">结果图像</div>
                    <q-img
                      :src="resultImage"
                      v-if="resultImage"
                      spinner-color="primary"
                      style="max-height: 500px; object-fit: contain;"
                    />
                    <div v-else class="text-center q-pa-xl text-grey-6">
                      <q-icon name="image" size="3rem" />
                      <p>无结果图像</p>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col-12 col-lg-5">
                <q-card flat bordered class="result-info-card">
                  <q-card-section class="q-pa-none">
                    <div class="text-subtitle2 q-pa-sm bg-grey-2 text-grey-8">检测信息</div>
                    <q-list separator dense padding>
                      <q-item>
                        <q-item-section avatar><q-icon name="info" color="primary"/></q-item-section>
                        <q-item-section>
                          <q-item-label caption>检测状态</q-item-label>
                          <q-item-label class="text-weight-medium">{{ detectionResult.status }}</q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item>
                        <q-item-section avatar><q-icon name="timer" color="primary"/></q-item-section>
                        <q-item-section>
                          <q-item-label caption>处理耗时</q-item-label>
                          <q-item-label class="text-weight-medium">{{ detectionResult.processing_time_ms ? (detectionResult.processing_time_ms / 1000).toFixed(2) + ' 秒' : 'N/A' }}</q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item>
                        <q-item-section avatar><q-icon name="my_location" color="primary"/></q-item-section>
                        <q-item-section>
                          <q-item-label caption>目标数量</q-item-label>
                          <q-item-label class="text-weight-medium">{{ detectionBoxes.length }}</q-item-label>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </q-card-section>
                </q-card>
              </div>
            </div>

            <q-card flat bordered class="q-mt-lg result-table-card" v-if="detectionBoxes.length > 0">
              <q-card-section class="q-pa-none">
                <div class="text-subtitle2 q-pa-sm bg-grey-2 text-grey-8">识别结果详情</div>
                <q-table
                  :rows="detectionBoxes"
                  :columns="boxesColumns"
                  row-key="id"
                  flat
                  dense
                  :pagination="{ rowsPerPage: 5 }"
                  class="result-q-table"
                />
              </q-card-section>
            </q-card>
          </template>
        </template>

        <template v-else-if="isLoading">
          <div class="empty-state">
            <div class="empty-state-content">
              <q-spinner-dots color="primary" size="3rem" />
              <h2 class="empty-title q-mt-md">正在检测中...</h2>
              <p class="empty-description">
                请稍候，系统正在处理您的图像。
              </p>
            </div>
          </div>
        </template>

        <template v-else>
          <div class="empty-state">
            <div class="empty-state-content">
              <q-icon name="image_search" size="5rem" class="empty-icon" />
              <h2 class="empty-title">单图检测模块</h2>
              <p class="empty-description">
                在左侧上传您的天文图像，设置参数后开始检测。
              </p>
              <div class="feature-list">
                <div class="feature-item">
                  <q-icon name="upload_file" size="1.5rem" />
                  <span>支持多种图像格式</span>
                </div>
                <div class="feature-item">
                  <q-icon name="tune" size="1.5rem" />
                  <span>可调检测参数</span>
                </div>
                <div class="feature-item">
                  <q-icon name="visibility" size="1.5rem" />
                  <span>可视化结果</span>
                </div>
                <div class="feature-item">
                  <q-icon name="save_alt" size="1.5rem" />
                  <span>结果可保存</span>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watchEffect } from 'vue';
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
const currentSampleImage = ref(null); // 声明 currentSampleImage ref

// 监听selectedFile的变化，如果用户选择了本地文件，则清空示例图片状态
watchEffect(() => {
  if (selectedFile.value) {
    currentSampleImage.value = null;
  }
});

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

// 重置检测状态的函数
const resetDetectionState = () => {
  detectionResult.value = null;
  selectedFile.value = null;
  currentSampleImage.value = null;
  resultImage.value = ''; // 可能也需要清空结果图片
  detectionBoxes.value = []; // 清空检测框
  detectionError.value = ''; // 清空错误信息
};

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
      currentSampleImage.value = sample; // 设置 currentSampleImage
      
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

<style scoped>
/* 基本页面和面板布局，参考 PredictPage.vue */
.page-container {
  min-height: 100vh;
  display: flex;
  background: linear-gradient(135deg, var(--md-sys-color-background) 0%, #eef2f7 100%);
  position: relative;
  overflow: hidden;
}

.background-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 0;
  overflow: hidden;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(45deg, var(--md-sys-color-primary-container), var(--md-sys-color-secondary-container));
  opacity: 0.1;
  animation: float 20s infinite ease-in-out alternate;
}

.circle-1 {
  width: 30vw;
  height: 30vw;
  top: -10vw;
  left: -10vw;
}

.circle-2 {
  width: 40vw;
  height: 40vw;
  bottom: -15vw;
  right: -15vw;
  animation-delay: 5s;
}

.circle-3 {
  width: 25vw;
  height: 25vw;
  top: 20vh;
  right: 5vw;
  animation-delay: 10s;
}

@keyframes float {
  0% {
    transform: translateY(0px) translateX(0px) rotate(0deg);
  }
  100% {
    transform: translateY(30px) translateX(-20px) rotate(15deg);
  }
}

.left-panel, .right-panel {
  position: relative;
  z-index: 1;
  height: 100vh;
  overflow-y: auto;
  padding: 1rem; /* Reduced padding for smaller screens */
}

.left-panel {
  width: 35%;
  min-width: 380px;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 5px 0 15px rgba(0,0,0,0.05);
}

.right-panel {
  width: 65%;
  background: transparent; /* Right panel is part of the main gradient */
}

.panel-content {
  padding: 1.5rem; /* Consistent padding */
  height: 100%;
}

.title-wrapper {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.title-icon {
  color: var(--md-sys-color-primary);
  background: rgba(var(--md-sys-color-primary-rgb), 0.1);
  padding: 0.8rem;
  border-radius: 16px;
  box-shadow: 0 6px 20px rgba(var(--md-sys-color-primary-rgb), 0.1);
}

.title-text {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--md-sys-color-on-surface);
}

.section-wrapper {
  background: rgba(255, 255, 255, 0.6);
  padding: 1.5rem;
  border-radius: 16px;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface-variant);
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

/* Glassmorphism inspired inputs */
.glass-select :deep(.q-field__control),
.glass-uploader :deep(.q-field__control),
.glass-uploader :deep(.q-uploader__header) {
  background: rgba(255, 255, 255, 0.3) !important;
  backdrop-filter: blur(5px);
  border-radius: 12px !important;
  border: 1px solid rgba(255, 255, 255, 0.5) !important;
  box-shadow: 0 2px 5px rgba(0,0,0,0.03);
}

.glass-uploader :deep(.q-uploader__list) {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  margin-top: 8px;
  padding: 8px;
}

.sample-card {
  border-radius: 12px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  background: rgba(255,255,255,0.5);
}

.sample-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.1);
}

.sample-card.selected-sample {
  border: 2px solid var(--md-sys-color-primary);
  box-shadow: 0 0 10px rgba(var(--md-sys-color-primary-rgb), 0.3);
}

.sample-card-title {
  background-color: rgba(0,0,0,0.4);
  font-size: 0.8rem;
  padding: 4px 0;
}

.predict-button {
  border-radius: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
  background: linear-gradient(45deg, var(--md-sys-color-primary), var(--md-sys-color-secondary));
  color: white;
  box-shadow: 0 4px 15px rgba(var(--md-sys-color-primary-rgb), 0.2);
}

.predict-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(var(--md-sys-color-primary-rgb), 0.3);
}

/* Right Panel Styles */
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.result-title {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
}

.result-icon {
  background: rgba(var(--md-sys-color-primary-rgb), 0.1);
  padding: 0.6rem;
  border-radius: 12px;
}

.result-actions .action-btn {
  border-radius: 8px;
  font-weight: 500;
}

.result-image-card, .result-info-card, .result-table-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.3);
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.result-q-table :deep(th) {
  background-color: rgba(0,0,0,0.03);
  font-weight: 600;
  color: var(--md-sys-color-on-surface-variant);
}

.result-q-table :deep(td) {
  color: var(--md-sys-color-on-surface);
}

/* Empty State Styles */
.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.empty-state-content {
  text-align: center;
  max-width: 550px;
  padding: 2.5rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.empty-icon {
  color: var(--md-sys-color-primary);
  background: rgba(var(--md-sys-color-primary-rgb), 0.1);
  padding: 1.2rem;
  border-radius: 50%;
  margin-bottom: 1.2rem;
  box-shadow: 0 6px 20px rgba(var(--md-sys-color-primary-rgb), 0.1);
}

.empty-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--md-sys-color-on-surface);
  margin-bottom: 0.8rem;
}

.empty-description {
  font-size: 1rem;
  color: var(--md-sys-color-on-surface-variant);
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.feature-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.8rem 1rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
}

.feature-item .q-icon {
  color: var(--md-sys-color-primary);
  background: rgba(var(--md-sys-color-primary-rgb), 0.1);
  padding: 0.4rem;
  border-radius: 6px;
}

.feature-item span {
  font-size: 0.9rem;
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 500;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .page-container {
    flex-direction: column;
  }
  .left-panel, .right-panel {
    width: 100%;
    min-height: auto; /* Allow panels to shrink */
    height: auto; /* Allow panels to shrink */
    max-height: none; /* Remove max-height for stacked view */
    padding: 0.5rem; /* Further reduce padding on very small screens */
  }
  .left-panel {
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  }
  .panel-content {
    padding: 1rem; /* Reduce padding inside panels */
  }
  .title-text {
    font-size: 1.5rem;
  }
  .result-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  .result-actions {
    width: 100%;
    justify-content: flex-start; /* Align actions to start on mobile */
    gap: 0.5rem;
  }
  .result-actions .q-btn {
    flex-grow: 1; /* Allow buttons to grow */
  }
  .feature-list {
    grid-template-columns: 1fr; /* Single column for features on mobile */
  }
  .empty-state-content {
    padding: 1.5rem;
  }
  .empty-title {
    font-size: 1.4rem;
  }
  .empty-description {
    font-size: 0.9rem;
  }
}

/* Custom scrollbar for panels if needed */
.left-panel::-webkit-scrollbar,
.right-panel::-webkit-scrollbar {
  width: 6px;
}

.left-panel::-webkit-scrollbar-thumb,
.right-panel::-webkit-scrollbar-thumb {
  background: rgba(0,0,0,0.2);
  border-radius: 3px;
}

.left-panel::-webkit-scrollbar-track,
.right-panel::-webkit-scrollbar-track {
  background: transparent;
}
</style>
