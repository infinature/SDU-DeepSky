<template>
  <q-page class="page-container">
    <div class="circles">
      <div></div>
      <div></div>
      <div></div>
      <div></div>
      <div></div>
      <div></div>
      <div></div>
      <div></div>
      <div></div>
      <div></div>
    </div>

    <div class="panel-container">
      <!-- Left Panel: Inputs and Controls -->
      <div class="left-panel">
        <q-scroll-area class="fit">
          <div class="panel-content">
            <div class="text-h5 q-mb-lg text-astroyolo-text-primary">天文图像批量检测</div>

            <!-- 批量上传区域 -->
            <div v-if="!detectionResult" class="section q-mb-md section-wrapper">
              <div class="section-title">文件选择</div>
              <q-file
                v-model="files"
                multiple
                use-chips
                clearable
                accept="image/*,.npy,.fit,.fits"
                label="选择图像文件或拖拽到此处"
                filled
                dense
                @update:model-value="selectFiles"
                class="q-mb-md"
                label-color="astroyolo-text-secondary"
                input-class="text-astroyolo-text-primary"
              >
                <template v-slot:prepend>
                  <q-icon name="attach_file" color="astroyolo-text-secondary" />
                </template>
              </q-file>

              <!-- 批量预览 -->
              <div v-if="actualFiles.length > 0" class="q-my-md">
                <div class="text-subtitle2 q-mb-sm text-astroyolo-text-secondary">已选中 {{ actualFiles.length }} 个文件:</div>
                <div class="row q-col-gutter-sm image-preview-container">
                  <div v-for="(file, index) in actualFiles" :key="index" class="col-6 col-sm-4 col-md-3">
                    <q-card class="image-preview-card section-wrapper" flat bordered>
                      <q-img
                        ratio="1"
                        class="cursor-pointer rounded-borders"
                        :src="file.preview || '/images/file_placeholder.png'"
                        @click="previewImage(index)"
                        no-transition
                      >
                        <div class="absolute-bottom text-subtitle2 text-center bg-black-transparent-light py-xs text-white">
                          {{ file.name }}
                        </div>
                      </q-img>
                      <q-card-section class="q-py-xs q-px-sm">
                        <div class="text-caption text-astroyolo-text-tertiary">{{ formatFileSize(file.size) }}</div>
                      </q-card-section>
                    </q-card>
                  </div>
                </div>
              </div>

              <!-- 样本批次选择 -->
              <div class="q-mt-md section-wrapper">
                <div class="section-title">或选择示例批次:</div>
                <div class="row q-col-gutter-md">
                  <div 
                    v-for="batch in sampleBatches" 
                    :key="batch.id"
                    class="col-6 col-sm-4"
                  >
                    <q-card 
                      class="cursor-pointer sample-batch-card section-wrapper"
                      flat bordered
                      :class="{'selected-batch': files.length > 0 && files[0].batch_id === batch.id}"
                      @click="loadSampleBatch(batch.id)"
                    >
                      <q-card-section class="text-center">
                        <div class="text-subtitle1 text-astroyolo-text-primary">{{ batch.name }}</div>
                        <div class="text-caption text-astroyolo-text-secondary">{{ batch.files.length }} 个文件</div>
                      </q-card-section>
                    </q-card>
                  </div>
                </div>
              </div>

              <!-- 数据集模式 (保留，但可以考虑是否常用) -->
              <div v-if="activeTab === 'dataset' && !detectionResult && !showHistory" class="section q-mb-md section-wrapper">
                <div class="section-title">数据集模式</div>
                <q-select
                  v-model="selectedDataset"
                  :options="datasets"
                  label="选择数据集"
                  filled
                  dense
                  emit-value
                  map-options
                  class="q-mb-sm"
                  label-color="astroyolo-text-secondary"
                  popup-content-class="bg-astroyolo-surface-container-high text-astroyolo-text-primary"
                />
                <q-select
                  v-model="datasetType"
                  :options="datasetTypes"
                  label="数据集类型（可选）"
                  filled
                  dense
                  emit-value
                  map-options
                  label-color="astroyolo-text-secondary"
                  popup-content-class="bg-astroyolo-surface-container-high text-astroyolo-text-primary"
                />
              </div>

              <!-- 参数设置 -->
              <div v-if="!detectionResult" class="section q-mb-md section-wrapper">
                <div class="section-title">检测参数</div>
                <div class="text-caption text-astroyolo-text-secondary q-mb-xs">置信度阈值: {{ confidenceThreshold }}</div>
                <q-slider
                  v-model="confidenceThreshold"
                  :min="0"
                  :max="1"
                  :step="0.01"
                  label
                  color="primary"
                  class="q-mb-md"
                />

                <div class="text-caption text-astroyolo-text-secondary q-mb-xs">检测硬件选择</div>
                <q-option-group
                  v-model="gpuOption"
                  :options="[
                    { label: '自动选择 (推荐)', value: 'auto', color: 'astroyolo-text-primary' },
                    { label: '强制CPU', value: 'cpu', color: 'astroyolo-text-primary' },
                    { label: '自定义GPU', value: 'custom', color: 'astroyolo-text-primary' }
                  ]"
                  color="primary"
                  inline
                  dense
                  class="q-mb-md custom-option-group text-astroyolo-text-primary"
                />
                <q-select
                  v-if="gpuOption === 'custom'"
                  v-model="selectedGPU"
                  :options="availableGPUs"
                  label="选择GPU"
                  filled
                  dense
                  emit-value
                  map-options
                  class="q-mb-md"
                  label-color="astroyolo-text-secondary"
                  popup-content-class="bg-astroyolo-surface-container-high text-astroyolo-text-primary"
                />

                <div class="text-caption text-astroyolo-text-secondary q-mb-xs">自定义权重文件 (可选)</div>
                <q-file
                  v-model="weightFile"
                  label="选择 .pt 权重文件"
                  filled
                  dense
                  clearable
                  accept=".pt"
                  class="q-mb-md"
                  label-color="astroyolo-text-secondary"
                  input-class="text-astroyolo-text-primary"
                >
                  <template v-slot:prepend>
                    <q-icon name="upload_file" color="astroyolo-text-secondary" />
                  </template>
                </q-file>
                <div class="text-caption text-astroyolo-text-tertiary q-ml-sm">✔️ 服务器不保存检测结果</div>
              </div>

              <!-- 开始检测按钮 -->
              <div v-if="!detectionResult" class="q-mt-lg">
                <q-btn
                  color="primary"
                  text-color="white"
                  :disable="(!files || files.length === 0) && !selectedDataset"
                  label="开始批量检测"
                  @click="startBatchDetection"
                  :loading="isLoading"
                  icon="science"
                  size="lg"
                  class="full-width"
                >
                  <template v-slot:loading>
                    <q-spinner-puff color="white" />
                    检测中...
                  </template>
                </q-btn>
              </div>
            </div>
          </div>
        </q-scroll-area>
      </div>

      <!-- Right Panel: Status and Information -->
      <div class="right-panel">
        <q-scroll-area class="fit">
          <div class="panel-content">
            <!-- Detection Status/Results -->
            <div class="section-wrapper status-card">
              <div class="section-title">检测状态</div>
              <div v-if="isLoading" class="text-center">
                <q-circular-progress
                  indeterminate
                  size="70px"
                  :thickness="0.2"
                  color="primary"
                  track-color="grey-3"
                  class="q-ma-md"
                />
                <div class="text-h6 q-mt-md text-astroyolo-text-secondary">正在处理批次...</div>
                <div class="text-caption text-astroyolo-text-tertiary q-mt-sm">已处理 {{ processedCount }} / {{ totalToProcess }} 张图像</div>
                <q-linear-progress :value="processingProgress / 100" color="primary" class="q-mt-md" />
                <div v-if="currentFile" class="text-caption text-astroyolo-text-tertiary q-mt-sm">当前文件: {{ currentFile }}</div>
              </div>
              <div v-else-if="detectionError" class="text-center text-negative">
                <q-icon name="error_outline" size="3em" class="q-mb-sm" />
                <div class="text-subtitle1">检测出错</div>
                <p class="text-astroyolo-text-secondary">{{ detectionError }}</p>
                <q-btn
                  label="重试或返回"
                  color="primary"
                  @click="resetDetectionState"
                  class="q-mt-md"
                />
              </div>
              <div v-else-if="!detectionResult && !showHistory" class="placeholder-info text-center text-astroyolo-text-secondary">
                <q-icon name="info_outline" size="3em" class="q-mb-md text-grey-5" />
                <p>请在左侧上传文件或选择示例批次，配置检测参数后开始批量检测。</p>
                <p>检测结果将在处理完成后跳转到新的页面显示。</p>
              </div>
            </div>
          </div>
        </q-scroll-area>
      </div>
    </div>

    <!-- Image Preview Dialog -->
    <q-dialog v-model="showPreview">
      <q-card style="width: 700px; max-width: 80vw;" class="glass-effect">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-white">图像预览</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="white" />
        </q-card-section>
        <q-card-section>
          <q-img :src="previewImageUrl" style="max-height: 70vh;" />
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Removed original global loading dialog as progress is shown in right panel -->

  </q-page>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router'; // 恢复导入
import { Notify as QNotify } from 'quasar';

defineOptions({
  name: 'BatchDetection'
});

const router = useRouter(); // 恢复使用
const apiBaseUrl = process.env.API_URL || 'http://localhost:5000';

// 参数设置
const weightFile = ref(null);
const confidenceThreshold = ref(0.5);
const useLocalCache = ref(true); // 默认使用本地缓存存储结果

// GPU选择
const gpuOption = ref('server'); // 默认使用服务器GPU
const selectedGPU = ref(null);
const availableGPUs = [
  { label: 'NVIDIA RTX 3090', value: 'rtx3090' },
  { label: 'NVIDIA RTX 2080 Ti', value: 'rtx2080ti' },
  { label: 'NVIDIA Tesla V100', value: 'teslav100' },
  { label: 'NVIDIA A100', value: 'a100' }
];

// 状态管理
const files = ref([]);
const actualFiles = ref([]); // 实际文件对象
const isLoading = ref(false);
const processingProgress = ref(0);
const detectionError = ref('');

// 控制状态 - 已简化
const detectionResult = ref(null);

// 检测模式选项
const selectedImages = ref([]);

// API基础URL已在上方定义

// 使用真实的样本图片数据
const sampleBatches = ref([
  {
    id: 1,
    name: '批次示例1',
    files: [
      { id: 1, name: '星系示例1', path: '/sample_images/SDSS_1.2376611256069e+18_rgb.jpg', thumbnail: '/sample_images/SDSS_1.2376611256069e+18_rgb_thumb.jpg', type: 'jpg', batch_id: 1 },
      { id: 2, name: '星云示例1', path: '/sample_images/SDSS_1.2376618718633e+18_rgb.jpg', thumbnail: '/sample_images/SDSS_1.2376618718633e+18_rgb_thumb.jpg', type: 'jpg', batch_id: 1 }
    ]
  },
  {
    id: 2,
    name: '星云与NPY数据',
    files: [
      { id: 3, name: '星云示例2', path: '/sample_images/SDSS_1.2376618718633e+18_rgb.jpg', thumbnail: '/sample_images/SDSS_1.2376618718633e+18_rgb_thumb.jpg', type: 'jpg', batch_id: 2 },
      { id: 4, name: 'NPY数据示例', path: '/sample_images/SDSS_1237668572011365559.npy', thumbnail: '/sample_images/SDSS_1237668572011365559_thumb.jpg', type: 'npy', batch_id: 2 }
    ]
  },
  {
    id: 3,
    name: '混合数据集',
    files: [
      { id: 5, name: '星系示例2', path: '/sample_images/SDSS_1.2376546407598e+18_rgb.jpg', thumbnail: '/sample_images/SDSS_1.2376546407598e+18_rgb_thumb.jpg', type: 'jpg', batch_id: 3 },
      { id: 6, name: '星系大图', path: '/sample_images/SDSS_1237648673968291868_rgb.jpg', thumbnail: '/sample_images/SDSS_1237648673968291868_rgb_thumb.jpg', type: 'jpg', batch_id: 3 },
      { id: 7, name: 'NPY数据示例2', path: '/sample_images/SDSS_1237668572011429966.npy', thumbnail: '/sample_images/SDSS_1237668572011429966_thumb.jpg', type: 'npy', batch_id: 3 }
    ]
  }
]);

// 简化获取样本数据的函数为同步函数
const fetchSampleBatches = () => {
  console.log('使用本地间样本数据');
  // sampleBatches已经预先设置
};

// 页面加载时获取样本批次
fetchSampleBatches();

// 加载示例图片批次
async function loadSampleBatch(batchId) {
  const batch = sampleBatches.value.find(b => b.id === batchId);
  if (!batch) return;
  
  // 更新UI显示的文件列表
  files.value = batch.files.map(file => ({ ...file }));
  
  // 创建示例文件对象和预览图片列表
  const sampleFileList = [];
  const previewImages = [];
  
  try {
    // 尝试获取实际样本图片信息
    for (const file of batch.files) {
      let filePath = file.path;
      if (!filePath.startsWith('/')) {
        filePath = `/static/sample_images/${file.name}`;
      }
      
      // 通过网络请求获取样本图片数据
      // 对于真实环境，这里应该是先检查文件是否存在
      try {
        // 根据文件类型构建样本信息
        
        // 仅记录路径信息，不预加载文件内容
        // 当用户点击开始检测时，后端会根据路径加载文件
        const sampleFile = { 
          name: file.name || filePath.split('/').pop(), // 确保始终有名称，如果没有则使用路径的最后部分
          path: filePath,
          type: file.type || (filePath.toLowerCase().endsWith('.npy') ? 'npy' : 'jpg') // 确保有类型，如果没有类型则根据文件后缀判断
        };
        sampleFileList.push(sampleFile);
        
        // 为图片类型文件添加预览信息
        if (!file.name.endsWith('.npy')) {
          previewImages.push({
            name: file.name,
            url: `${apiBaseUrl}${filePath}`
          });
        } else {
          // 对于NPY文件使用占位图
          previewImages.push({
            name: file.name,
            url: `${apiBaseUrl}/static/images/npy_placeholder.jpg`
          });
        }
      } catch (err) {
        console.error(`加载样本文件 ${file.name} 失败`, err);
      }
    }
    
    // 设置文件列表
    actualFiles.value = sampleFileList;
    files.value = sampleFileList; // 同时更新files引用，确保处理正确的文件列表
    selectedImages.value = previewImages;
    
    QNotify.create({
      message: `已加载${batch.name}示例，共${sampleFileList.length}个文件`,
      color: 'secondary',
      icon: 'check_circle',
      position: 'bottom-right',
      timeout: 2000
    });
  } catch (error) {
    console.error('加载样本批次失败', error);
    
    QNotify.create({
      message: `加载样本失败: ${error.message}`,
      color: 'negative',
      icon: 'error',
      position: 'bottom-right',
      timeout: 3000
    });
  }
}

// 预览批量图片
function previewImage(index) {
  if (!actualFiles.value[index]) return;
  
  const file = actualFiles.value[index];
  const reader = new FileReader();
  
  reader.onload = (e) => {
    // 检查该图片是否已经在预览列表中
    const existingIndex = selectedImages.value.findIndex(img => img.name === file.name);
    
    if (existingIndex === -1) {
      // 如果是npy文件，我们使用一个默认的图标
      if (file.name.endsWith('.npy')) {
        selectedImages.value.push({
          name: file.name,
          url: '/sample_images/npy_placeholder.jpg'  // 使用npy文件的默认图标
        });
      } else {
        selectedImages.value.push({
          name: file.name,
          url: e.target.result
        });
      }
    } else {
      // 如果已存在，更新图片URL
      if (!file.name.endsWith('.npy')) {
        selectedImages.value[existingIndex].url = e.target.result;
      }
    }
  };
  
  // 如果不是npy文件，则读取数据为URL
  if (!file.name.endsWith('.npy')) {
    reader.readAsDataURL(file);
  } else {
    // 如果是npy文件，直接添加占位图片
    selectedImages.value.push({
      name: file.name,
      url: '/sample_images/npy_placeholder.jpg'  // 使用npy文件的默认图标
    });
  }
}

// 选择文件
function selectFiles(selectedFiles) {
  if (!selectedFiles || selectedFiles.length === 0) return;
  
  // 更新UI显示的文件列表
  files.value = Array.from(selectedFiles).map(file => ({
    name: file.name,
    size: file.size
  }));
  
  // 将原始文件对象添加到 actualFiles 中，这是实际会上传到服务器的文件
  actualFiles.value = Array.from(selectedFiles);
  
  // 清空已选图片预览
  selectedImages.value = [];
  
  // 为每个文件生成预览
  actualFiles.value.forEach((file, index) => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        // 创建一个新的数组，避免直接修改原对象
        const filesCopy = [...actualFiles.value];
        filesCopy[index] = {
          ...filesCopy[index],
          preview: e.target.result
        };
        actualFiles.value = filesCopy;
      };
      reader.readAsDataURL(file);
    }
  });
  
  QNotify.create({
    message: `已选择${files.value.length}个文件`,
    color: 'secondary',
    icon: 'check_circle',
    position: 'bottom-right',
    timeout: 2000
  });
}

// 格式化文件大小
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  else return (bytes / 1048576).toFixed(1) + ' MB';
}

// 开始批量检测 - 参照单图检测的实现方式
async function startBatchDetection() {
  // 直接使用 files.value 进行检查，该值由 q-file 组件直接设置
  if (!files.value || files.value.length === 0) {
    QNotify.create({
      color: 'negative',
      message: '请先选择文件',
      position: 'top'
    });
    return;
  }
  
  isLoading.value = true;
  detectionError.value = '';
  processingProgress.value = 0;
  
  try {
    // 打印日志查看文件对象
    console.log('准备上传文件:', files.value);
    
    // 重置文件处理逻辑，为每个文件对象添加必要的属性
    let filesToProcess = [];
    if (actualFiles.value.length > 0) {
      filesToProcess = actualFiles.value;
    } else {
      // 如果actualFiles为空，根据files生成有效的文件对象
      filesToProcess = files.value.map(file => {
        // 确保每个文件对象都有name和path属性
        if (!file) return null;
        
        // 构造一个有效的文件对象
        const path = file.path || (file.name ? `/static/sample_images/${file.name}` : null);
        return {
          name: file.name || (path ? path.split('/').pop() : `file_${Math.random().toString(36).substring(7)}`),
          path: path,
          type: file.type || (file.name && file.name.toLowerCase().endsWith('.npy') ? 'npy' : 'jpg')
        };
      }).filter(file => file !== null); // 过滤无效文件
    }
    
    // 再次检查每个文件对象，确保它们都有name和path属性
    filesToProcess = filesToProcess.map((file, index) => {
      if (!file) return null;
      if (!file.name) file.name = `file_${index+1}`;
      if (!file.path && file.name) file.path = `/static/sample_images/${file.name}`;
      return file;
    }).filter(file => file !== null && file.name && file.path);
    
    console.log('处理后的文件列表:', filesToProcess);
    
    // 检查文件对象是否完整，如果不完整则跳过处理
    if (!filesToProcess || filesToProcess.length === 0) {
      QNotify.create({
        color: 'negative',
        message: '没有可用的文件进行检测',
        position: 'top'
      });
      isLoading.value = false;
      return;
    }
    
    // 全部采用单图检测的处理方式
    let successCount = 0;
    let totalDetections = 0;
    const allResults = [];
    
    // 逐个处理文件，而不是一次性发送全部
    for (let i = 0; i < filesToProcess.length; i++) {
      try {
        const currentFile = filesToProcess[i];
        
        // 文件对象已在前面处理过，现在只需要简单验证
        console.log(`处理文件 ${i+1}/${filesToProcess.length}:`, currentFile.name);
        
        // 创建新的 FormData 对象
        const formData = new FormData();
        
        // 这里是关键 - 根据文件类型处理：File对象直接添加，示例批次文件则使用路径
        if (currentFile instanceof File) {
          // 正常上传的文件是File对象
          formData.append('file', currentFile);
          console.log('添加文件到FormData，类型:', currentFile.type, '大小:', currentFile.size);
        } else if (currentFile.path) {
          // 对于示例批次文件，我们有路径信息，将路径发送到后端
          // 修正路径，移除开头的斜杠
          const correctedPath = currentFile.path.startsWith('/') ? currentFile.path.substring(1) : currentFile.path;
          formData.append('file_path', correctedPath);
          formData.append('file_name', currentFile.name);
          console.log('添加示例文件路径到FormData:', currentFile.path);
        } else {
          throw new Error(`${currentFile.name} 不是有效的File对象或没有路径信息`);
        }
        
        // 添加其他参数
        formData.append('confidence', confidenceThreshold.value.toString());
        formData.append('image_type', currentFile.name.toLowerCase().endsWith('.npy') ? 'npy' : 'jpg');
        formData.append('use_local_cache', useLocalCache.value.toString());
        formData.append('gpu_option', gpuOption.value);
        
        // 如果选择自定义GPU，添加GPU信息
        if (gpuOption.value === 'custom' && selectedGPU.value) {
          formData.append('gpu_id', selectedGPU.value);
        }
        
        console.log('请求参数:', {
          confidence: confidenceThreshold.value,
          image_type: currentFile.name.toLowerCase().endsWith('.npy') ? 'npy' : 'jpg',
          use_local_cache: useLocalCache.value,
          gpu_option: gpuOption.value,
          gpu_id: selectedGPU.value
        });
        
        // 添加权重文件（如果有）
        if (weightFile.value) {
          formData.append('weight_file', weightFile.value);
        }
        
        // 调用单图检测 API
        console.log('发送请求到:', `${apiBaseUrl}/api/detect`);
        const response = await axios.post(`${apiBaseUrl}/api/detect`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        console.log(`文件 ${currentFile.name} 的响应:`, response.data);
        
        if (response.data.status === 'success') {
          successCount++;
          totalDetections += response.data.detection_count || 0;
          
          // 添加到结果列表
          allResults.push({
            filename: currentFile.name,
            result_filename: `${currentFile.name.split('.')[0]}_result.png`,
            detection_count: response.data.detection_count || 0,
            boxes: response.data.boxes || [],
            // 重要：添加base64图像数据用于预览和下载
            result_image: response.data.result_image ? `data:image/png;base64,${response.data.result_image}` : null,
            status: 'success'
          });
        } else {
          throw new Error(response.data.message || '检测失败');
        }
      } catch (err) {
        // 文件对象已经预处理过，不需要重复提取文件名
        const fileName = filesToProcess[i].name;
        console.error(`处理文件 ${fileName} 时出错:`, err);
        allResults.push({
          filename: fileName,
          status: 'error',
          message: err.message || '处理失败'
        });
      }
      
      // 更新进度
      processingProgress.value = Math.round(((i + 1) / filesToProcess.length) * 100);
    }
    
    // 模拟批量检测响应
    const mockResponse = {
      status: 'success',
      task_id: `task_${Date.now()}`,
      files_count: filesToProcess.length,
      success_count: successCount, // 使用 successCount 变量
      detection_count: totalDetections,
      results: allResults
    };
    
    // 处理最终结果
    if (mockResponse.status === 'success') {
      QNotify.create({
        color: 'positive',
        message: `成功检测${mockResponse.files_count}个文件，共发现${mockResponse.detection_count}个目标。`,
        position: 'top',
        timeout: 3000
      });
      
      // 跳转到结果显示页面
      const taskId = mockResponse.task_id;
      localStorage.setItem(`batch_task_${taskId}`, JSON.stringify(mockResponse));
      router.push({ name: 'BatchResults', params: { taskId } });
    } else {
      detectionError.value = mockResponse.message || '检测过程中出现错误';
      QNotify.create({
        color: 'negative',
        message: detectionError.value,
        position: 'top'
      });
    }
  } catch (error) {
    console.error('批量检测请求错误', error);
    detectionError.value = error.response?.data?.message || '服务器连接错误';
    QNotify.create({
      color: 'negative',
      message: detectionError.value,
      position: 'top'
    });
  } finally {
    isLoading.value = false;
    processingProgress.value = 100;
  }
}

// 数据集检测功能已移除

// 加载历史检测记录
// 历史记录相关功能已移除

// 标签相关功能已移除

</script>

<style lang="scss" scoped>
@import '../css/_variables.scss'; 

.page-container {
  min-height: 100vh;
  background: linear-gradient(135deg, $background 0%, #eef2f7 100%);
  display: flex;
  position: relative;
  overflow: hidden;
}

.circles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.circles div {
  position: absolute;
  display: block;
  list-style: none;
  width: 20px;
  height: 20px;
  background: rgba(200, 220, 255, 0.1);
  animation: animate 25s linear infinite;
  bottom: -150px;
  border-radius: 50%;
}

// ... (rest of the circle animations as in SingleDetection.vue)
.circles div:nth-child(1) { left: 25%; width: 80px; height: 80px; animation-delay: 0s; }
.circles div:nth-child(2) { left: 10%; width: 20px; height: 20px; animation-delay: 2s; animation-duration: 12s; }
.circles div:nth-child(3) { left: 70%; width: 20px; height: 20px; animation-delay: 4s; }
.circles div:nth-child(4) { left: 40%; width: 60px; height: 60px; animation-delay: 0s; animation-duration: 18s; }
.circles div:nth-child(5) { left: 65%; width: 20px; height: 20px; animation-delay: 0s; }
.circles div:nth-child(6) { left: 75%; width: 110px; height: 110px; animation-delay: 3s; }
.circles div:nth-child(7) { left: 35%; width: 150px; height: 150px; animation-delay: 7s; }
.circles div:nth-child(8) { left: 50%; width: 25px; height: 25px; animation-delay: 15s; animation-duration: 45s; }
.circles div:nth-child(9) { left: 20%; width: 15px; height: 15px; animation-delay: 2s; animation-duration: 35s; }
.circles div:nth-child(10) { left: 85%; width: 150px; height: 150px; animation-delay: 0s; animation-duration: 11s; }

@keyframes animate {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 0.6;
  }
  100% {
    transform: translateY(-1000px) rotate(720deg);
    opacity: 0;
  }
}

.panel-container {
  display: flex;
  width: 90%;
  max-width: 1400px;
  height: 85vh;
  max-height: 800px;
  z-index: 1;
  gap: 20px;
}

.left-panel, 
.right-panel {
  height: 100vh; 
  overflow-y: auto; 
  position: relative; 
  z-index: 1; 
}

.left-panel {
  width: 35%; 
  min-width: 380px; 
  padding: 1rem; 
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 5px 0 15px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.right-panel {
  width: 65%; 
  padding: 1rem; 
  background: transparent;
  display: flex;
  flex-direction: column;
  justify-content: flex-start; 
  gap: 1.5rem; 
}

.section-wrapper {
  background: rgba(255, 255, 255, 0.6); 
  padding: 1.5rem;
  border-radius: 16px;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  color: $on-surface; 
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface-variant); 
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.status-card {
  width: 100%;
}

.image-preview-card {
  .bg-black-transparent-light {
    background-color: rgba(0, 0, 0, 0.3);
  }
}

.sample-batch-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.1);
  }
}

.selected-batch {
  border: 2px solid $primary;
  box-shadow: 0 0 8px rgba($primary, 0.4);
}

.custom-option-group ::v-deep .q-radio__label {
  color: $on-surface-variant !important; 
}

.placeholder-info {
  margin-top: 2rem;
  q-icon {
    font-size: 3rem; 
    color: $grey-5; 
    margin-bottom: 1rem; 
  }
  p {
    color: $text-secondary; 
    font-size: 0.95rem;
    line-height: 1.6;
  }
}

</style>
