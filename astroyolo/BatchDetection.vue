<template>
  <q-page padding>
    <div class="row justify-center">
      <div class="col-12 col-md-10">
        <q-card class="q-mb-md">
          <q-card-section>
            <div class="text-h5 q-mb-md">天文图像批量检测</div>
            
            <!-- 批量上传区域 -->
            <div v-if="!detectionResult">
              <q-card-section>
                <div class="q-mb-md">
                  <q-file
                    v-model="files"
                    multiple
                    use-chips
                    clearable
                    accept="image/*,.npy,.fit,.fits"
                    label="选择图像文件"
                    @update:model-value="selectFiles"
                  >
                    <template v-slot:prepend>
                      <q-icon name="attach_file" />
                    </template>
                  </q-file>
                </div>

                <!-- 批量预览 -->
                <div v-if="actualFiles.length > 0" class="q-my-md">
                  <div class="text-subtitle1 q-mb-sm">选中 {{ actualFiles.length }} 个文件</div>
                  <div class="row q-col-gutter-md">
                    <div v-for="(file, index) in actualFiles" :key="index" class="col-6 col-sm-4 col-md-3">
                      <q-card>
                        <q-img
                          ratio="1"
                          class="cursor-pointer"
                          :src="file.preview || '/images/file_placeholder.png'"
                          @click="previewImage(index)"
                          no-transition
                        >
                          <div class="absolute-bottom text-subtitle2 text-center bg-black bg-opacity-60">
                            {{ file.name }}
                          </div>
                        </q-img>
                        <q-card-section class="q-py-xs">
                          <div class="text-caption">{{ formatFileSize(file.size) }}</div>
                        </q-card-section>
                      </q-card>
                    </div>
                  </div>
                </div>

                <!-- 样本批次选择 -->
                <div class="q-mt-md">
                  <div class="text-subtitle1 q-mb-sm">或选择示例批次:</div>
                  <div class="row q-col-gutter-md">
                    <div 
                      v-for="batch in sampleBatches" 
                      :key="batch.id"
                      class="col-6 col-sm-4 col-md-3"
                    >
                      <q-card 
                        class="cursor-pointer" 
                        :class="{'bg-blue-1': files.length > 0 && files[0].batch_id === batch.id}"
                        @click="loadSampleBatch(batch.id)"
                      >
                        <q-card-section>
                          <div class="text-h6">{{ batch.name }}</div>
                          <div class="text-caption">{{ batch.files.length }} 个文件</div>
                        </q-card-section>
                      </q-card>
                    </div>
                  </div>
                </div>
              </q-card-section>
            </div>

            <!-- 数据集模式 -->
            <div v-if="activeTab === 'dataset' && !detectionResult && !showHistory">
              <q-card-section>
                <div class="q-mb-md">
                  <q-select
                    v-model="selectedDataset"
                    :options="datasets"
                    label="选择数据集"
                    outlined
                    dense
                    emit-value
                    map-options
                  />
                </div>
                
                <div class="q-mb-md">
                  <q-select
                    v-model="datasetType"
                    :options="datasetTypes"
                    label="数据集类型（可选）"
                    outlined
                    dense
                    emit-value
                    map-options
                  />
                </div>
              </q-card-section>
            </div>

            <!-- 参数设置 -->
            <q-card-section v-if="!detectionResult">
              <div class="text-subtitle1 q-mb-sm">检测参数</div>
              <div class="row q-col-gutter-md">
                <div class="col-12 col-sm-6">
                  <q-slider
                    v-model="confidenceThreshold"
                    :min="0"
                    :max="1"
                    :step="0.01"
                    label
                    label-always
                    color="primary"
                    class="q-my-lg"
                  >
                    <template v-slot:thumb-label>
                      置信度: {{ confidenceThreshold.toFixed(2) }}
                    </template>
                  </q-slider>
                </div>
                <div class="col-12 col-sm-6">
                  <q-toggle
                    v-model="useLocalCache"
                    label="结果暂存在本地缓存中"
                    color="primary"
                    class="q-my-md"
                  />
                  <div class="text-caption text-grey-8 q-ml-md">✔️ 服务器不保存检测结果</div>
                </div>
                
                <div class="col-12">
                  <div class="text-subtitle2 q-mb-xs">检测硬件选择</div>
                  <q-option-group
                    v-model="gpuOption"
                    :options="[
                      { label: '使用服务器GPU（默认）', value: 'server' },
                      { label: '自选显卡', value: 'custom' }
                    ]"
                    color="primary"
                    inline
                  />
                  <q-select
                    v-if="gpuOption === 'custom'"
                    v-model="selectedGPU"
                    :options="availableGPUs"
                    label="选择显卡"
                    outlined
                    dense
                    class="q-mt-sm"
                    style="max-width: 300px"
                  />
                </div>
                
                <div class="col-12">
                  <q-file
                    v-model="weightFile"
                    label="自定义权重文件 (.pt) - 可选"
                    outlined
                    dense
                    accept=".pt"
                  >
                    <template v-slot:prepend>
                      <q-icon name="insert_drive_file" />
                    </template>
                  </q-file>
                </div>
              </div>
              
              <!-- 开始检测按钮 -->
              <div class="q-mt-lg">
                <q-btn
                  color="primary"
                  :disable="!files || files.length === 0"
                  :loading="isLoading"
                  @click="startFolderDetection"
                >
                  开始检测
                </q-btn>
                
                <q-btn
                  v-if="isLoading"
                  flat
                  color="negative"
                  class="q-ml-sm"
                  @click="isLoading = false"
                >
                  取消
                </q-btn>
              </div>
              
              <!-- 进度条 -->
              <div v-if="isLoading" class="q-mt-md">
                <q-linear-progress
                  :value="processingProgress / 100"
                  color="primary"
                  class="q-mb-xs"
                />
                <div class="text-caption text-right">{{ processingProgress }}%</div>
              </div>
            </q-card-section>
            
            <!-- 已移除检测结果显示区域，结果将在新页面中显示 -->
            
            <!-- 错误提示 -->
            <q-card-section v-if="detectionError">
              <q-banner class="bg-negative text-white">
                {{ detectionError }}
                <template v-slot:action>
                  <q-btn
                    flat
                    color="white"
                    label="关闭"
                    @click="detectionError = null"
                  />
                </template>
              </q-banner>
            </q-card-section>
          </q-card-section>
        </q-card>
      </div>
    </div>
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
async function startFolderDetection() {
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
  /* ... */
</style>
