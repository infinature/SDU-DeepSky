<template>
  <q-page padding class="bg-white">
    <div class="row justify-center">
      <div class="col-12 col-md-10">
        <div class="text-h5 q-mb-md">单图检测</div>
      
        <!-- 参数设置卡片 -->
        <q-card flat bordered class="q-mb-md">
          <q-card-section>
            <div class="text-subtitle1">检测参数</div>
          </q-card-section>
          
          <q-card-section>
            <div class="row q-col-gutter-md">
              <div class="col-12 col-md-6">
                <q-select
                  v-model="imageType"
                  :options="imageTypeOptions"
                  label="图像类型"
                  outlined
                  dense
                />
              </div>
              <div class="col-12 col-md-6">
                <q-slider
                  v-model="confidenceThreshold"
                  :min="0"
                  :max="1"
                  :step="0.01"
                  label
                  label-always
                  color="astroyolo-primary"
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
        <q-card ref="dropAreaRef" class="q-mb-md drop-area" flat bordered id="drop-area">
          <q-card-section>
            <div class="text-subtitle1">上传图片</div>
            <div class="text-caption">支持jpg、png和npy格式文件</div>
          </q-card-section>
          
          <q-card-section class="text-center">
            <div class="text-center q-pa-md">
              <q-file
                v-model="file"
                outlined
                accept=".jpg,.jpeg,.png,.npy"
                label="选择文件"
                @update:model-value="handleFileChange"
              >
                <template v-slot:prepend>
                  <q-icon name="attach_file" />
                </template>
                <template v-slot:append v-if="file">
                  <q-icon name="close" @click.stop="file = null" class="cursor-pointer" />
                </template>
              </q-file>
              
              <q-separator spaced />
              
              <div class="text-body2 q-mb-sm text-grey-8">或拖放文件至此区域</div>
              
              <q-separator spaced />
              
              <div class="text-body2 q-mb-sm text-astroyolo-primary">选择示例图片</div>
              <div class="row justify-center q-gutter-sm">
                <q-btn 
                  v-for="sample in sampleImages" 
                  :key="sample.id"
                  :label="sample.name"
                  color="astroyolo-primary"
                  flat
                  @click="loadSampleImage(sample.path, sample.type)"
                />
              </div>
            </div>
          </q-card-section>
          
          <q-inner-loading :showing="isUploading">
            <q-spinner-dots size="50px" color="astroyolo-primary" />
          </q-inner-loading>
        </q-card>
      
      <!-- 图片预览和结果区域 -->
        <q-slide-transition>
          <div v-if="showPreview" class="q-mb-lg">
            <div class="row q-col-gutter-md">
              <div class="col-md-6 col-sm-12">
                <q-card flat bordered>
                  <q-card-section>
                    <div class="text-subtitle1">原始图像</div>
                  </q-card-section>
                  <q-card-section class="preview-container">
                    <img :src="previewUrl" class="preview-image" />
                  </q-card-section>
                </q-card>
              </div>
              
              <div class="col-md-6 col-sm-12">
                <q-card v-if="resultUrl" flat bordered>
                  <q-card-section>
                    <div class="text-subtitle1">检测结果</div>
                  </q-card-section>
                  <q-card-section class="preview-container">
                    <img :src="resultUrl" class="preview-image" />
                  </q-card-section>
                </q-card>
                <q-card v-else-if="!isLoading" flat bordered>
                  <q-card-section>
                    <div class="text-subtitle1">准备检测</div>
                  </q-card-section>
                  <q-card-section>
                    <div class="text-body2 text-grey-8">请点击下方按钮开始检测。</div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
            
            <!-- 检测结果信息 -->
            <q-card v-if="detectionResult" class="q-mt-md" flat bordered>
              <q-card-section>
                <div class="text-subtitle1">检测信息</div>
              </q-card-section>
              <q-card-section>
                <div class="row q-col-gutter-md">
                  <div class="col-md-4 col-sm-6 col-xs-12">
                    <q-card flat class="bg-astroyolo-primary-container">
                      <q-card-section>
                        <div class="text-body2 text-grey-8">检测时间</div>
                        <div class="text-subtitle1">{{ detectionResult.processingTime || '-- ' }} ms</div>
                      </q-card-section>
                    </q-card>
                  </div>
                  <div class="col-md-4 col-sm-6 col-xs-12">
                    <q-card flat class="bg-astroyolo-secondary-container">
                      <q-card-section>
                        <div class="text-body2 text-grey-8">检测目标数</div>
                        <div class="text-subtitle1">{{ detectionCount }}</div>
                      </q-card-section>
                    </q-card>
                  </div>
                  <div class="col-md-4 col-sm-6 col-xs-12">
                    <q-card flat class="bg-astroyolo-tertiary-container">
                      <q-card-section>
                        <div class="text-body2 text-grey-8">平均置信度</div>
                        <div class="text-subtitle1">{{ averageConfidence }}</div>
                      </q-card-section>
                    </q-card>
                  </div>
                </div>
              </q-card-section>
            </q-card>
            
            <!-- 操作按钮 -->
            <div class="q-mt-md text-center">
              <q-btn 
                v-if="file && !isLoading && !detectionError" 
                label="开始检测" 
                color="astroyolo-primary" 
                icon="search" 
                @click="performDetection" 
                :loading="isLoading"
                :disable="!file"
              />
              
              <q-btn 
                v-if="resultUrl" 
                label="保存结果" 
                color="astroyolo-secondary" 
                flat
                icon="save" 
                class="q-ml-sm"
                @click="downloadResult"
              />
              
              <q-btn 
                v-if="showPreview" 
                label="重新选择" 
                color="grey-6" 
                flat
                icon="refresh" 
                class="q-ml-sm"
                @click="resetDetection"
              />
            </div>
            
            <!-- 错误信息 -->
            <q-banner v-if="detectionError" class="bg-negative text-white q-mt-md">
              检测过程中出现错误: {{ detectionError }}
              <template v-slot:action>
                <q-btn flat label="重试" @click="resetDetection" />
              </template>
            </q-banner>
          </div>
        </q-slide-transition>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount } from 'vue'
import { Notify } from 'quasar'

// 使用Quasar提供的通知系统

// 为拖放区域元素创建模板引用
const dropAreaRef = ref(null);
// 跟踪事件监听器是否已附加
const listenersAttached = ref(false);

// 状态变量
const imageType = ref('jpg')
const confidenceThreshold = ref(0.3)
const file = ref(null)
const isUploading = ref(false)
const isLoading = ref(false)
const showPreview = ref(false)
const showResults = ref(false)
const originalPreviewUrl = ref('')
const resultPreviewUrl = ref('')
const sampleImages = ref([])
const detectionDetails = ref([])

// 选项
const imageTypeOptions = [
  { label: '图像文件 (JPG, PNG)', value: 'jpg' },
  { label: 'NPY数据文件', value: 'npy' }
]

// 处理文件选择变更
const handleFileChange = (uploadedFiles) => {
  if (!uploadedFiles) return
  
  const selectedFile = Array.isArray(uploadedFiles) ? uploadedFiles[0] : uploadedFiles;
  if (selectedFile) {
    handleFile(selectedFile);
  } else {
    file.value = null;
    originalPreviewUrl.value = '';
    showPreview.value = false;
    showResults.value = false;
    detectionDetails.value = [];
  }
}

// 处理文件
const handleFile = (selectedFile) => {
  if (!selectedFile) return
  
  const reader = new FileReader()
  reader.onload = (e) => {
    originalPreviewUrl.value = e.target.result
    showPreview.value = true
  }
  reader.readAsDataURL(selectedFile)
}

// 执行检测
const performDetection = async () => {
  if (!file.value) {
    Notify.create({
      type: 'negative',
      message: '请先选择一个文件',
      position: 'top'
    })
    return
  }
  
  isLoading.value = true
  
  try {
    // 创建参数对象
    // 在实际项目中，这里会使用params对象作为API调用参数
    // const params = {
    //   confidence: confidenceThreshold.value,
    //   imageType: imageType.value
    // }
    
    // 这里将调用API服务
    // const response = await apiService.detectSingleImage(file.value, params)
    
    // 模拟检测响应
    await new Promise(resolve => setTimeout(resolve, 1500))
    const response = {
      resultImageUrl: originalPreviewUrl.value,
      detections: [
        { id: 1, type: '星系', confidence: 0.95, coordinates: 'x: 150, y: 200, w: 100, h: 100' },
        { id: 2, type: '恒星', confidence: 0.88, coordinates: 'x: 300, y: 350, w: 50, h: 50' }
      ]
    }
    
    // 处理成功响应
    resultPreviewUrl.value = response.resultImageUrl
    detectionDetails.value = response.detections || []
    showResults.value = true
    
    // 显示成功通知
    Notify.create({
      type: 'positive',
      message: '检测完成',
      position: 'top'
    })
  } catch (error) {
    console.error('检测失败:', error)
    Notify.create({
      type: 'negative',
      message: `检测失败: ${error.message || '未知错误'}`,
      position: 'top'
    })
  } finally {
    isLoading.value = false
  }
}

// 加载示例图片
const loadSampleImage = async (samplePath) => {
  try {
    if (!samplePath) {
      Notify.create({
        type: 'negative',
        message: '无效的示例图片路径',
        position: 'top'
      })
      return
    }
    
    isLoading.value = true
    file.value = null // 清除已选文件
    
    // 模拟从服务器获取图片
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 在实际情况下，这里应该是获取真实图片的代码
    // const response = await fetch(samplePath)
    // const blob = await response.blob()
    // file.value = new File([blob], 'sample.jpg')
    
    // 模拟文件加载
    originalPreviewUrl.value = samplePath
    showPreview.value = true
    
    Notify.create({
      type: 'positive',
      message: '示例图片加载完成',
      position: 'top'
    })
  } catch (error) {
    console.error('加载示例图片失败:', error)
    Notify.create({
      type: 'negative',
      message: `加载示例图片失败: ${error.message || '未知错误'}`,
      position: 'top'
    })
  } finally {
    isLoading.value = false
  }
}

// 从后端获取示例图片列表
const fetchSampleImages = async () => {
  try {
    // 在实际项目中，这里应该是API调用
    // const response = await apiService.getSampleImages()
    // sampleImages.value = response
    
    // 模拟数据
    sampleImages.value = [
      { id: 1, name: '星系示例', path: '/img/samples/galaxy.jpg', type: 'jpg' },
      { id: 2, name: '星云示例', path: '/img/samples/nebula.jpg', type: 'jpg' },
      { id: 3, name: 'NPY数据示例', path: '/img/samples/data.npy', type: 'npy' }
    ]
  } catch (error) {
    console.error('获取示例图片列表失败:', error)
    Notify.create({
      type: 'negative',
      message: `无法加载示例图片: ${error.message || '未知错误'}`,
      position: 'top'
    })
  }
}

// 阻止默认拖放行为
const preventDefaults = (e) => {
  e.preventDefault();
  e.stopPropagation();
};

// 处理拖放区域高亮
const highlight = () => {
  if (dropAreaRef.value && dropAreaRef.value.$el) {
    dropAreaRef.value.$el.classList.add('is-dragover');
  }
};

// 处理拖放区域取消高亮
const unhighlight = () => {
  if (dropAreaRef.value && dropAreaRef.value.$el) {
    dropAreaRef.value.$el.classList.remove('is-dragover');
  }
};

// 处理文件拖放
const handleDrop = (e) => {
  if (!dropAreaRef.value || !dropAreaRef.value.$el) return;

  const dt = e.dataTransfer;
  const files = dt.files;

  if (files.length) {
    handleFile(files[0]);
  }
  // unhighlight(); // unhighlight 会在 dragleave 和 drop 事件中通过监听器调用
};

// 初始化拖放区域
onMounted(async () => {
  // 获取示例图片列表
  await fetchSampleImages();

  // 确保DOM更新完毕后再初始化拖放区域
  await nextTick();
  initDropZone(); 
});

// 初始化拖放区域DOM
// 把这个功能独立出来便于管理
const initDropZone = () => {
  if (!dropAreaRef.value || !dropAreaRef.value.$el) {
    console.error('拖放区域元素 (dropAreaRef.$el) 未找到!');
    Notify.create({
      type: 'negative',
      message: '无法初始化拖放功能: 目标区域未找到。',
      position: 'top'
    });
    return;
  }

  if (listenersAttached.value) {
    // console.log('拖放事件监听器已附加，跳过。');
    return;
  }

  const element = dropAreaRef.value.$el; // 获取实际的DOM元素

  try {
    // 防止事件重复添加，尽管 listenersAttached.value 应该处理此问题
    // 但更健壮的方式是先移除（如果可能存在旧的），再添加

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      element.addEventListener(eventName, preventDefaults, false);
      // 注意：对 document.body 添加全局监听器需要谨慎处理，确保在组件卸载时清理
      document.body.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
      element.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      element.addEventListener(eventName, unhighlight, false);
    });

    element.addEventListener('drop', handleDrop, false);
    
    listenersAttached.value = true;
    console.log('拖放区域已初始化');

  } catch (error) {
    console.error('初始化拖放区域失败:', error);
    Notify.create({
      type: 'negative',
      message: `初始化拖放区域失败: ${error.message}`,
      position: 'top'
    });
  }
};

// 在组件卸载前移除事件监听器
onBeforeUnmount(() => {
  if (listenersAttached.value && dropAreaRef.value && dropAreaRef.value.$el) {
    const element = dropAreaRef.value.$el;
    console.log('正在移除拖放区域事件监听器...');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      element.removeEventListener(eventName, preventDefaults, false);
      document.body.removeEventListener(eventName, preventDefaults, false); // 清理 document.body 上的监听器
    });
    ['dragenter', 'dragover'].forEach(eventName => {
      element.removeEventListener(eventName, highlight, false);
    });
    ['dragleave', 'drop'].forEach(eventName => {
      element.removeEventListener(eventName, unhighlight, false);
    });
    element.removeEventListener('drop', handleDrop, false);
    
    listenersAttached.value = false; // 重置标志
    console.log('拖放区域事件监听器已移除');
  } else {
    // console.log('无需移除拖放监听器，因为它们未附加或元素不存在。');
  }
});

// 注意: fetchSampleImages() 已在上方的 onMounted 钩子中调用

</script>

<style lang="scss" scoped>
.drop-area {
  border: 2px dashed $grey-5;
  border-radius: 8px;
  transition: all 0.3s;
  
  &.is-dragover {
    border-color: $primary;
    background-color: rgba($primary, 0.05);
  }
}

.preview-container {
  max-height: 350px;
  overflow: hidden;
  display: flex;
  justify-content: center;
}

.preview-image {
  max-width: 100%;
  max-height: 350px;
  object-fit: contain;
}
</style>
