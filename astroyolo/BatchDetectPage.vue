<template>
  <q-page padding>
    <div class="q-pa-md">
      <h1 class="text-h4 q-mb-md">批量检测</h1>
      
      <!-- 参数设置卡片 -->
      <q-card class="q-mb-md">
        <q-card-section>
          <div class="text-h6">检测参数</div>
        </q-card-section>
        
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-4">
              <q-select
                v-model="detectionModel"
                :options="modelOptions"
                label="检测模型类型"
                outlined
                dense
              />
            </div>
            <div class="col-12 col-md-4">
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
                  阈值: {{ confidenceThreshold.toFixed(2) }}
                </template>
              </q-slider>
            </div>
            <div class="col-12 col-md-4">
              <q-checkbox
                v-model="enhancedDetection"
                label="增强检测"
                class="q-mt-md"
              />
            </div>
          </div>
        </q-card-section>
      </q-card>
      
      <!-- 文件上传卡片 -->
      <div class="q-mb-lg">
        <q-tabs
          v-model="tab"
          class="text-primary"
          active-color="primary"
          indicator-color="primary"
          align="justify"
          narrow-indicator
        >
          <q-tab name="upload" icon="cloud_upload" label="文件上传" />
          <q-tab name="dataset" icon="view_module" label="数据集" />
        </q-tabs>
        
        <q-tab-panels v-model="tab" animated>
          <q-tab-panel name="upload">
            <q-card ref="batchDropAreaRef" class="drop-area" id="batch-drop-area">
              <q-card-section>
                <div class="text-h6">批量上传图片</div>
                <div class="text-caption">支持jpg、png、npy文件，最大50个文件</div>
              </q-card-section>
              
              <q-card-section class="text-center">
                <q-file
                  v-model="files"
                  outlined
                  multiple
                  accept=".jpg,.jpeg,.png,.npy"
                  label="选择文件"
                  @update:model-value="handleFileChange"
                  counter
                  max-files="50"
                  style="max-width: 500px; margin: 0 auto;"
                >
                  <template v-slot:prepend>
                    <q-icon name="attach_file" />
                  </template>
                  <template v-slot:append v-if="files && files.length > 0">
                    <q-icon name="close" @click.stop="files = []" class="cursor-pointer" />
                  </template>
                </q-file>
                
                <div class="q-mt-md">
                  <q-btn
                    label="开始检测"
                    color="primary"
                    :disable="!files || files.length === 0"
                    :loading="isDetecting"
                    @click="startBatchDetection"
                  />
                </div>
              </q-card-section>
              
              <q-inner-loading :showing="isUploading">
                <q-spinner-dots size="50px" color="primary" />
              </q-inner-loading>
            </q-card>
          </q-tab-panel>
          
          <q-tab-panel name="dataset">
            <q-card>
              <q-card-section>
                <div class="text-h6">选择数据集</div>
              </q-card-section>
              
              <q-card-section>
                <div class="row q-col-gutter-md">
                  <div class="col-12 col-md-4" v-for="(dataset, index) in datasets" :key="index">
                    <q-card class="dataset-card cursor-pointer" @click="useDataset(dataset)">
                      <q-img :src="dataset.previewImage" height="160px">
                        <div class="absolute-bottom text-subtitle1 text-center bg-transparent">
                          {{ dataset.name }}
                        </div>
                      </q-img>
                      <q-card-section>
                        <div class="text-caption">包含 {{ dataset.imageCount }} 张图片</div>
                      </q-card-section>
                    </q-card>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </q-tab-panel>
        </q-tab-panels>
      </div>
      
      <!-- 进度条 -->
      <q-card v-if="isDetecting || uploadProgress > 0 || detectionProgress > 0" class="q-mb-md">
        <q-card-section>
          <div class="text-h6">处理进度</div>
        </q-card-section>
        
        <q-card-section>
          <div v-if="uploadProgress > 0 && uploadProgress < 100">
            <div class="text-subtitle2">上传进度</div>
            <q-linear-progress :value="uploadProgress / 100" color="blue" class="q-mb-md" />
          </div>
          
          <div v-if="detectionProgress > 0">
            <div class="text-subtitle2">检测进度</div>
            <q-linear-progress :value="detectionProgress / 100" color="primary" />
            <div class="text-caption text-right">
              {{ detectionProgress.toFixed(0) }}% 完成
            </div>
          </div>
        </q-card-section>
      </q-card>
      
      <!-- 检测结果 -->
      <div v-if="detectionResults.length > 0" class="q-my-lg">
        <q-card class="results-card">
          <q-card-section class="row items-center">
            <div class="text-h6">检测结果</div>
            <q-space />
            <q-btn flat round icon="download" @click="exportResults">
              <q-tooltip>导出结果</q-tooltip>
            </q-btn>
          </q-card-section>
          
          <q-separator />
          
          <q-card-section>
            <q-table
              :rows="detectionResults"
              :columns="resultsColumns"
              row-key="id"
              flat
              bordered
              :pagination="{ rowsPerPage: 10 }"
            >
              <template v-slot:body="props">
                <q-tr :props="props">
                  <q-td key="filename" :props="props">
                    {{ props.row.filename }}
                  </q-td>
                  <q-td key="detectedObjects" :props="props">
                    {{ props.row.detectedObjects }}
                  </q-td>
                  <q-td key="processingTime" :props="props">
                    {{ props.row.processingTime }}s
                  </q-td>
                  <q-td key="confidence" :props="props">
                    {{ props.row.confidence }}
                  </q-td>
                  <q-td key="status" :props="props">
                    <q-badge :color="props.row.status === 'completed' ? 'positive' : 'warning'">
                      {{ props.row.status === 'completed' ? '完成' : '处理中' }}
                    </q-badge>
                  </q-td>
                  <q-td key="actions" :props="props">
                    <q-btn
                      flat
                      round
                      dense
                      icon="visibility"
                      @click="viewResult(props.row)"
                    >
                      <q-tooltip>查看结果</q-tooltip>
                    </q-btn>
                  </q-td>
                </q-tr>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>
    </div>
    
    <!-- 结果对话框 -->
    <q-dialog v-model="showResultDialog">
      <q-card style="width: 80vw; max-width: 1000px">
        <q-card-section class="row items-center">
          <div class="text-h6">检测结果对话框</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        
        <q-separator />
        
        <q-card-section>
          <div v-if="selectedResult">
            <div class="text-subtitle1 q-mb-md">文件名: {{ selectedResult.filename }}</div>
            <div class="row q-col-gutter-md">
              <div class="col-md-8 col-sm-12">
                <q-img
                  src="/img/placeholder-result.jpg"
                  spinner-color="primary"
                  style="height: 400px"
                >
                  <div class="absolute-bottom text-subtitle2 bg-transparent">
                    检测结果预览
                  </div>
                </q-img>
              </div>
              <div class="col-md-4 col-sm-12">
                <div class="text-subtitle2 q-mb-sm">检测到的物体 {{ selectedResult.detectedObjects }} 个</div>
                <div class="text-subtitle2 q-mb-sm">处理时间: {{ selectedResult.processingTime }}s</div>
                <div class="text-subtitle2 q-mb-sm">置信度: {{ selectedResult.confidence }}</div>
                
                <q-list bordered separator>
                  <q-item v-for="i in selectedResult.detectedObjects" :key="i">
                    <q-item-section>
                      <q-item-label>物体 {{ i }}</q-item-label>
                      <q-item-label caption>置信度: {{ (Math.random() * 0.3 + 0.7).toFixed(2) }}</q-item-label>
                    </q-item-section>
                    <q-item-section avatar>
                      <q-badge color="primary">{{ ['star', 'nebula', 'galaxy'][i % 3] }}</q-badge>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount } from 'vue';
import { Notify } from 'quasar';

// 为拖放区域元素创建模板引用
const batchDropAreaRef = ref(null);
// 跟踪事件监听器是否已附加
const batchListenersAttached = ref(false);

// 状态变量
const tab = ref('upload');
const detectionModel = ref('standard');
const confidenceThreshold = ref(0.3);
const enhancedDetection = ref(false);
const files = ref([]);
const isUploading = ref(false);
const isDetecting = ref(false);
const uploadProgress = ref(0);
const detectionProgress = ref(0);
const detectionResults = ref([]);
const showResultDialog = ref(false);
const selectedResult = ref(null);

// 选项
const modelOptions = [
  { label: '标准检测模型', value: 'standard' },
  { label: '高精度检测模型', value: 'high_precision' },
  { label: '快速检测模型', value: 'fast' }
];

// 数据集
const datasets = ref([
  {
    id: 1,
    name: '星系数据集',
    previewImage: '/img/datasets/galaxy-dataset.jpg',
    imageCount: 15,
    path: '/datasets/galaxy'
  },
  {
    id: 2,
    name: '星云数据集',
    previewImage: '/img/datasets/nebula-dataset.jpg',
    imageCount: 8,
    path: '/datasets/nebula'
  },
  {
    id: 3,
    name: '混合数据集',
    previewImage: '/img/datasets/mixed-dataset.jpg',
    imageCount: 25,
    path: '/datasets/mixed'
  }
]);

// 表格列
const resultsColumns = [
  { name: 'filename', align: 'left', label: '文件名', field: 'filename' },
  { name: 'detectedObjects', align: 'center', label: '检测到的物体', field: 'detectedObjects', sortable: true },
  { name: 'processingTime', align: 'center', label: '处理时间(s)', field: 'processingTime', sortable: true },
  { name: 'confidence', align: 'center', label: '置信度', field: 'confidence', sortable: true },
  { name: 'status', align: 'center', label: '状态', field: 'status' },
  { name: 'actions', align: 'center', label: '操作', field: 'actions' }
];

// 处理文件选择变更
const handleFileChange = (uploadedFiles) => {
  // uploadedFiles 可以是一个文件对象或一个文件对象数组
  if (!uploadedFiles) {
    files.value = [];
    return;
  }
  // 确保 files.value 总是一个数组
  files.value = Array.isArray(uploadedFiles) ? uploadedFiles : [uploadedFiles];
  
  // 可选：如果需要，可以在这里添加对文件数量或类型的即时验证
  if (files.value.length > 50) {
    Notify.create({
      type: 'warning',
      message: '一次最多只能处理50个文件。已选择前50个。',
      position: 'top'
    });
    files.value = files.value.slice(0, 50);
  }
  console.log('Files selected:', files.value.length);
};

// 阻止默认拖放行为
const preventDefaults = (e) => {
  e.preventDefault();
  e.stopPropagation();
};

// 拖放区域高亮
const highlight = () => {
  if (batchDropAreaRef.value && batchDropAreaRef.value.$el) {
    batchDropAreaRef.value.$el.classList.add('is-dragover');
  }
};

// 移除拖放区域高亮
const unhighlight = () => {
  if (batchDropAreaRef.value && batchDropAreaRef.value.$el) {
    batchDropAreaRef.value.$el.classList.remove('is-dragover');
  }
};

// 处理文件拖放
const handleDrop = (e) => {
  if (!batchDropAreaRef.value || !batchDropAreaRef.value.$el) return;

  const dt = e.dataTransfer;
  const droppedFiles = dt.files;

  if (droppedFiles.length > 0) {
    // 将FileList转换为数组，以便可以与现有的files ref合并或替换
    const newFiles = Array.from(droppedFiles).slice(0, 50 - (files.value ? files.value.length : 0));
    if (files.value && files.value.length > 0) {
      files.value = [...files.value, ...newFiles];
    } else {
      files.value = newFiles;
    }
    handleFileChange(files.value); // 触发文件变更处理
  }
  // unhighlight(); // unhighlight 会在 dragleave 和 drop 事件中通过监听器调用
};

// 初始化拖放区域
onMounted(async () => {
  // 确保DOM更新完毕后再初始化拖放区域
  await nextTick();
  initDropZone();
});

// 初始化拖放区域DOM
// 把这个功能独立出来便于管理
const initDropZone = () => {
  if (!batchDropAreaRef.value || !batchDropAreaRef.value.$el) {
    console.error('批量拖放区域元素 (batchDropAreaRef.$el) 未找到!');
    Notify.create({
      type: 'negative',
      message: '无法初始化批量拖放功能: 目标区域未找到。',
      position: 'top'
    });
    return;
  }

  if (batchListenersAttached.value) {
    // console.log('批量拖放事件监听器已附加，跳过。');
    return;
  }

  const element = batchDropAreaRef.value.$el;

  try {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      element.addEventListener(eventName, preventDefaults, false);
      document.body.addEventListener(eventName, preventDefaults, false); // 适用于全局拖放行为
    });
    ['dragenter', 'dragover'].forEach(eventName => {
      element.addEventListener(eventName, highlight, false);
    });
    ['dragleave', 'drop'].forEach(eventName => {
      element.addEventListener(eventName, unhighlight, false);
    });
    element.addEventListener('drop', handleDrop, false);
    
    batchListenersAttached.value = true;
    console.log('批量拖放区域已初始化');

  } catch (error) {
    console.error('初始化批量拖放区域失败:', error);
    Notify.create({
      type: 'negative',
      message: `初始化批量拖放区域失败: ${error.message}`,
      position: 'top'
    });
  }
};

// 在组件卸载前移除事件监听器
onBeforeUnmount(() => {
  if (batchListenersAttached.value && batchDropAreaRef.value && batchDropAreaRef.value.$el) {
    const element = batchDropAreaRef.value.$el;
    console.log('正在移除批量拖放区域事件监听器...');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      element.removeEventListener(eventName, preventDefaults, false);
      document.body.removeEventListener(eventName, preventDefaults, false);
    });
    ['dragenter', 'dragover'].forEach(eventName => {
      element.removeEventListener(eventName, highlight, false);
    });
    ['dragleave', 'drop'].forEach(eventName => {
      element.removeEventListener(eventName, unhighlight, false);
    });
    element.removeEventListener('drop', handleDrop, false);
    
    batchListenersAttached.value = false;
    console.log('批量拖放区域事件监听器已移除');
  } else {
    // console.log('无需移除批量拖放监听器，因为它们未附加或元素不存在。');
  }
});

</script>

<style lang="scss" scoped>
.drop-area {
  border: 2px dashed $grey-5;
  padding: 20px;
  text-align: center;
  transition: all 0.3s ease;
  border-radius: 8px;

  &.is-dragover {
    border-color: $primary;
    background-color: rgba($primary, 0.05);
  }
}

.dataset-card {
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }
}

.results-card {
  overflow: hidden;
}
</style>
