<template>
  <q-page class="page-container batch-results-page">
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
      <!-- Left Panel: Summary, Actions -->
      <div class="left-panel">
        <q-scroll-area class="fit">
          <div class="panel-content">
            <div class="section-title text-h5 q-mb-lg">天文图像检测结果管理</div>

            <div v-if="loading" class="text-center q-pa-md section-wrapper">
              <q-spinner
                color="primary"
                size="3em"
                class="q-mb-sm"
              />
              <div class="text-grey-7">正在加载结果数据...</div>
            </div>

            <div v-else-if="!taskData" class="text-center q-pa-md section-wrapper">
              <q-icon name="error_outline" size="3em" color="negative" />
              <div class="q-mt-sm text-negative text-body1">找不到检测结果数据</div>
              <q-btn
                color="primary"
                class="q-mt-lg"
                to="/batch-detection"
                icon="arrow_back"
                label="返回批量检测"
                unelevated
              />
            </div>

            <div v-else class="section-wrapper">
              <!-- 结果摘要卡片 -->
              <div>
                <div class="section-title-secondary text-subtitle1 q-mb-sm">检测摘要</div>
                <q-list dense padding class="text-grey-8">
                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="photo_library" color="primary" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>检测文件</q-item-label>
                      <q-item-label caption class="text-grey-7">{{ taskData?.files_count || 0 }} 个文件</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="find_in_page" color="primary" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>识别对象</q-item-label>
                      <q-item-label caption class="text-grey-7">{{ taskData?.detection_count || 0 }} 个目标</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section avatar>
                      <q-icon name="check_circle_outline" color="primary" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>成功率</q-item-label>
                      <q-item-label caption class="text-grey-7">{{ calcSuccessRate() }}%</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>

              <!-- 下载和设置路径按钮 -->
              <div class="q-mt-md">
                <div class="section-title-secondary text-subtitle1 q-mb-sm">结果管理</div>
                <q-btn
                  color="primary"
                  icon-right="download"
                  label="下载全部结果"
                  @click="downloadResults"
                  class="full-width q-mb-sm"
                  unelevated
                />
                <q-btn
                  outline
                  color="primary"
                  icon="folder_open"
                  :label="userDownloadPath ? `下载路径: ${userDownloadPath}` : '设置下载路径'"
                  @click="showPathDialog = true"
                  class="full-width"
                />
              </div>

              <q-btn
                color="amber-8"
                text-color="black"
                class="full-width q-mt-xl"
                to="/batch-detection"
                icon="arrow_back"
                label="返回批量检测页面"
                unelevated
              />
            </div>
          </div>
        </q-scroll-area>
      </div>

      <!-- Right Panel: Results Table -->
      <div class="right-panel">
        <q-scroll-area class="fit">
          <div class="panel-content">
            <div class="section-title text-h6 q-mb-md">检测结果详情</div>
            <div class="section-wrapper">
              <div v-if="taskData && taskData.results && taskData.results.length > 0">
                <q-input
                  v-model="searchTerm"
                  filled
                  dense
                  clearable
                  label="搜索文件名..."
                  class="q-mb-md"
                >
                  <template v-slot:prepend>
                    <q-icon name="search" />
                  </template>
                </q-input>

                <q-table
                  :rows="filteredResults"
                  :columns="columns"
                  row-key="filename"
                  dense
                  flat
                  class="results-table"
                  :rows-per-page-options="[10, 20, 50, 0]"
                  table-header-class="text-primary"
                  virtual-scroll
                  style="height: calc(100vh - 250px);" 
                >
                  <template v-slot:body-cell-status="props">
                    <q-td :props="props">
                      <q-chip
                        :color="props.row.status === 'success' ? 'positive' : 'negative'"
                        text-color="white"
                        dense
                        class="status-chip"
                      >
                        {{ props.row.status === 'success' ? '成功' : '失败' }}
                      </q-chip>
                      <q-tooltip v-if="props.row.status === 'error'" class="bg-grey-9 text-white shadow-2" :offset="[10, 10]">
                        {{ props.row.message || '处理失败' }}
                      </q-tooltip>
                    </q-td>
                  </template>

                  <template v-slot:body-cell-actions="props">
                    <q-td :props="props">
                      <q-btn
                        v-if="props.row.status !== 'error' && props.row.result_image"
                        flat
                        round
                        dense
                        size="sm"
                        color="primary"
                        icon="visibility"
                        @click="previewImage(props.row)"
                      >
                        <q-tooltip class="bg-grey-9 text-white shadow-2" :offset="[10, 10]">预览</q-tooltip>
                      </q-btn>
                      <q-btn
                        v-if="props.row.status !== 'error' && props.row.result_image"
                        flat
                        round
                        dense
                        size="sm"
                        color="green-3"
                        icon="download"
                        @click="downloadSingleResult(props.row)"
                      >
                        <q-tooltip class="bg-grey-9 text-white shadow-2" :offset="[10, 10]">下载此结果</q-tooltip>
                      </q-btn>
                    </q-td>
                  </template>

                  <template v-slot:no-data>
                    <div class="full-width row flex-center text-grey-7 q-gutter-sm">
                      <q-icon size="2em" name="sentiment_dissatisfied" />
                      <span>没有找到匹配的结果。</span>
                    </div>
                  </template>
                </q-table>
              </div>
              <div v-else class="text-center text-grey-7 q-pa-xl">
                <q-icon name="hourglass_empty" size="xl" class="q-mb-sm" />
                <p>没有可供显示的检测结果。</p>
              </div>
            </div>
          </div>
        </q-scroll-area>
      </div>
    </div>

    <!-- Image Preview Dialog -->
    <q-dialog v-model="showPreview" maximized>
      <q-card class="preview-dialog bg-astroyolo-surface-container text-astroyolo-text-primary">
        <q-card-section class="row items-center q-pb-none bg-astroyolo-primary text-astroyolo-on-primary">
          <div class="text-h6">{{ previewItem?.filename || '检测结果预览' }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <div class="row">
            <!-- 图片预览区域 -->
            <div class="col-12 col-md-8">
              <q-img
                v-if="previewItem?.annotated_image_url"
                :src="previewItem?.annotated_image_url"
                style="max-width: 100%; max-height: 80vh; object-fit: contain;"
                spinner-color="primary"
              />
              <div v-else class="text-center q-pa-xl">
                <q-icon name="image_not_supported" size="4em" class="text-astroyolo-text-secondary"/>
                <p class="text-astroyolo-text-secondary q-mt-md">无法加载预览图像。</p>
              </div>
            </div>
            <!-- 目标列表区域 -->
            <div class="col-12 col-md-4 q-pa-md">
              <div class="text-subtitle1 q-mb-sm">识别到的目标</div>
              <q-list bordered separator v-if="previewItem?.detections && previewItem.detections.length > 0">
                <q-item v-for="(det, index) in previewItem.detections" :key="index">
                  <q-item-section>
                    <q-item-label>{{ det.name }} ({{ (det.confidence * 100).toFixed(2) }}%)</q-item-label>
                    <q-item-label caption class="text-astroyolo-text-secondary">位置: [{{ det.box.join(', ') }}]</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
              <div v-else class="text-astroyolo-text-secondary">未识别到目标。</div>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="关闭" color="secondary" v-close-popup />
          <q-btn 
            flat 
            label="下载"
            color="primary" 
            icon="download"
            @click="downloadSingleResult(previewItem)"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- 设置下载路径对话框 -->
    <q-dialog v-model="showPathDialog">
      <q-card style="min-width: 350px" class="path-dialog bg-astroyolo-surface-container text-astroyolo-text-primary">
        <q-card-section class="row items-center q-pb-none bg-astroyolo-primary text-astroyolo-on-primary">
          <div class="text-h6">设置下载路径</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        
        <q-card-section>
          <p class="text-astroyolo-text-secondary">当前下载路径: {{ currentDownloadPath || '未设置' }}</p>
          <q-input
            v-model="selectedPathDisplay"
            label="选择或输入新路径"
            readonly
            outlined
            dense
            label-color="astroyolo-text-secondary"
            input-class="text-astroyolo-text-primary"
            class="q-mb-sm"
          />
          <q-btn label="选择路径" color="secondary" @click="selectDownloadPath" class="q-mb-sm full-width" />
          <div class="text-caption text-astroyolo-text-tertiary q-mt-xs">
            如果留空，将使用浏览器默认下载位置。
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="取消" color="secondary" v-close-popup />
          <q-btn flat label="保存" color="primary" @click="savePath" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { Notify } from 'quasar';

const router = useRouter();
const route = useRoute();

// 任务数据
const taskId = ref(route.params.taskId);
const taskData = ref(null);

// 用户自定义路径管理
const userDownloadPath = ref(localStorage.getItem('user_download_path') || '');
const showPathDialog = ref(false);

// 搜索和过滤
const searchTerm = ref('');
const filteredResults = computed(() => {
  if (!taskData.value || !taskData.value.results) return [];
  
  if (!searchTerm.value) return taskData.value.results;
  
  return taskData.value.results.filter(result => 
    result.filename.toLowerCase().includes(searchTerm.value.toLowerCase())
  );
});

// 表格列定义
const columns = [
  { name: 'filename', label: '文件名', field: 'filename', align: 'left', sortable: true },
  { name: 'status', label: '状态', field: row => row.status === 'error' ? '失败' : '成功', align: 'center' },
  { name: 'detection_count', label: '检测目标数', field: 'detection_count', align: 'center', sortable: true },
  { name: 'actions', label: '操作', field: 'actions', align: 'center' }
];

// 预览相关
const showPreview = ref(false);
const previewItem = ref(null);
const previewUrl = ref('');

// 获取任务数据
onMounted(() => {
  loadTaskData();
});

// 从本地存储加载任务数据
function loadTaskData() {
  try {
    const cachedData = localStorage.getItem(`batch_task_${taskId.value}`);
    if (cachedData) {
      taskData.value = JSON.parse(cachedData);
      console.log('从本地缓存加载任务数据:', taskData.value);
    } else {
      // 如果本地没有缓存，显示错误消息
      Notify.create({
        color: 'negative',
        message: '无法找到任务数据，请返回批量检测页面重新检测',
        position: 'top',
        timeout: 5000
      });
      // 延时后返回批量检测页面
      setTimeout(() => {
        router.push('/batch-detection');
      }, 2000);
    }
  } catch (error) {
    console.error('加载任务数据失败:', error);
    Notify.create({
      color: 'negative',
      message: '加载任务数据失败',
      position: 'top'
    });
  }
}

// 计算成功率
function calcSuccessRate() {
  if (!taskData.value || !taskData.value.results || taskData.value.results.length === 0) {
    return 0;
  }
  
  const successCount = taskData.value.results.filter(r => r.status !== 'error').length;
  return Math.round((successCount / taskData.value.results.length) * 100);
}

// 预览图片
function previewImage(item) {
  previewItem.value = item;
  
  // 只使用本地缓存的数据
  if (item.result_image && item.result_image.startsWith('data:image')) {
    // 使用base64格式的图片数据
    previewUrl.value = item.result_image;
  } else if (item.boxes && item.boxes.length > 0) {
    // 如果有盒子数据但没有图片，生成一个缓存数据占位图
    previewUrl.value = './static/placeholder-image.png'; // 修正路径
  } else {
    // 如果没有缓存的图像，显示一个错误占位图
    previewUrl.value = './static/no-result.png'; // 修正路径
  }
  
  showPreview.value = true;
}

// 下载单个结果
function downloadSingleResult(item) {
  if (!item) return;
  
  try {
    // 只使用本地缓存的数据
    if (!item.result_image || !item.result_image.startsWith('data:image')) {
      Notify.create({
        color: 'warning',
        message: '没有可下载的图片数据',
        position: 'top'
      });
      return;
    }
    
    // 创建链接并触发下载
    const link = document.createElement('a');
    link.href = item.result_image; // 使用base64数据
    
    link.download = item.result_filename || `result_${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    Notify.create({
      color: 'positive',
      message: '开始下载结果图片',
      position: 'top',
      timeout: 2000
    });
  } catch (error) {
    console.error('下载结果失败:', error);
    Notify.create({
      color: 'negative',
      message: '下载结果失败',
      position: 'top'
    });
  }
}

// 选择下载路径
async function selectDownloadPath() {
  if (!('showDirectoryPicker' in window)) {
    Notify.create({
      color: 'negative',
      message: '您的浏览器不支持文件系统访问功能',
      position: 'top'
    });
    return;
  }
  
  try {
    const dirHandle = await window.showDirectoryPicker().catch(() => null);
    if (!dirHandle) return;
    
    // 尝试获取目录信息
    const relativePaths = [];
    for await (const entry of dirHandle.values()) {
      if (relativePaths.length < 3) {
        relativePaths.push(entry.name);
      } else {
        break;
      }
    }
    
    // 生成用户友好的路径展示
    let displayPath = '已选择的文件夹';
    if (relativePaths.length > 0) {
      displayPath = `文件夹(${relativePaths.join(', ')})`;
    }
    
    // 保存路径信息
    localStorage.setItem('astroyolo_download_dirhandle_id', 'astroyolo-detection-results');
    localStorage.setItem('astroyolo_download_dir_samples', JSON.stringify(relativePaths));
    userDownloadPath.value = displayPath;
    localStorage.setItem('user_download_path', displayPath);
    
    Notify.create({
      color: 'positive',
      message: `已设置下载路径: ${displayPath}`,
      position: 'top'
    });
  } catch (error) {
    console.error('选择目录失败:', error);
    Notify.create({
      color: 'negative',
      message: '选择目录失败',
      position: 'top'
    });
  }
}

// 打包下载所有结果
async function downloadResults() {
  if (!taskData.value || !taskData.value.results || taskData.value.results.length === 0) {
    Notify.create({
      color: 'warning',
      message: '没有可下载的结果',
      position: 'top'
    });
    return;
  }
  
  const successResults = taskData.value.results.filter(r => r.status !== 'error' && r.result_image && r.result_image.startsWith('data:image'));
  
  if (successResults.length === 0) {
    Notify.create({
      color: 'warning',
      message: '没有成功的检测结果可供下载',
      position: 'top'
    });
    return;
  }
  
  try {
    // 检查是否支持 File System Access API
    if ('showDirectoryPicker' in window) {
      Notify.create({
        color: 'info',
        message: '请选择保存结果的文件夹',
        position: 'top',
        timeout: 3000
      });

      // 尝试使用最后一次选择的路径，如果失败则让用户重新选择
      let dirHandle;
      
      try {
        dirHandle = await window.showDirectoryPicker({
          // 使用id而不是路径，避免浏览器安全限制
          id: 'astroyolo-detection-results'
        }).catch(() => null);
      } catch {
        // 如果出错，回退到标准选择器
        dirHandle = await window.showDirectoryPicker().catch(() => null);
      }
      
      if (!dirHandle) {
        Notify.create({
          color: 'warning',
          message: '没有选择目录，下载已取消',
          position: 'top'
        });
        return;
      }
      
      // 保存目录句柄，下次使用
      try {
        // 尝试获取目录路径信息（注意：几乎所有浏览器都不支持获取实际路径）
        const relativePaths = [];
        for await (const entry of dirHandle.values()) {
          if (relativePaths.length < 3) {
            relativePaths.push(entry.name);
          } else {
            break;
          }
        }
        
        // 生成用户友好的路径展示
        let displayPath = '所选文件夹';
        if (relativePaths.length > 0) {
          displayPath = `文件夹(${relativePaths.join(', ')})`;
        }
        
        // 保存路径信息到本地存储
        localStorage.setItem('astroyolo_download_dirhandle_id', 'astroyolo-detection-results');
        localStorage.setItem('astroyolo_download_dir_samples', JSON.stringify(relativePaths));
        userDownloadPath.value = displayPath;
        localStorage.setItem('user_download_path', displayPath);
        
        // 显示路径已设置成功通知
        Notify.create({
          color: 'positive',
          message: `已设置下载路径: ${displayPath}`,
          position: 'top',
          timeout: 2000
        });
      } catch (error) {
        console.warn('无法获取目录信息:', error);
      }
      
      // 正在保存通知
      Notify.create({
        color: 'info',
        message: `正在保存 ${successResults.length} 个结果到${userDownloadPath.value || '所选文件夹'}...`,
        position: 'top',
        timeout: 3000
      });
      
      // 逐个写入文件
      for (let i = 0; i < successResults.length; i++) {
        const result = successResults[i];
        const fileName = result.result_filename || `result_${i+1}.png`;
        
        try {
          // 转换base64为二进制数据
          const base64Data = result.result_image.split(',')[1];
          const byteCharacters = atob(base64Data);
          const byteArrays = [];
          
          for (let j = 0; j < byteCharacters.length; j += 512) {
            const slice = byteCharacters.slice(j, j + 512);
            const byteNumbers = new Array(slice.length);
            
            for (let k = 0; k < slice.length; k++) {
              byteNumbers[k] = slice.charCodeAt(k);
            }
            
            byteArrays.push(new Uint8Array(byteNumbers));
          }
          
          const blob = new Blob(byteArrays, {type: 'image/png'});
          
          // 创建文件
          const fileHandle = await dirHandle.getFileHandle(fileName, {create: true});
          const writable = await fileHandle.createWritable();
          await writable.write(blob);
          await writable.close();
          
        } catch (error) {
          console.error(`保存文件 ${fileName} 失败:`, error);
        }
      }
      
      Notify.create({
        color: 'positive',
        message: `成功保存 ${successResults.length} 个结果到选定文件夹`,
        position: 'top',
        timeout: 3000
      });
    } else {
      // 如果不支持文件系统 API，则逐个下载
      Notify.create({
        color: 'info',
        message: '浏览器不支持文件夹选择，将逐个下载文件',
        position: 'top',
        timeout: 3000
      });
      
      successResults.forEach((result, index) => {
        setTimeout(() => {
          downloadSingleResult(result);
        }, index * 500);
      });
    }
  } catch (error) {
    console.error('下载操作失败:', error);
    Notify.create({
      color: 'negative',
      message: '下载操作失败: ' + (error.message || '未知错误'),
      position: 'top'
    });
  }
}

</script>

<style lang="scss" scoped>
@import '../css/_variables.scss';

.batch-results-page {
  // Match .page-container from BatchDetection
  min-height: 100vh;
  padding: 0; 
  background: linear-gradient(135deg, $deep-space-start 0%, $deep-space-end 100%);
  position: relative;
  overflow: hidden; 
}

.panel-container {
  display: flex;
  height: 100vh;
  width: 100%;
}

.left-panel,
.right-panel {
  height: 100vh;
  overflow-y: auto;
  position: relative;
  z-index: 1;
  padding: 1rem;
}

.left-panel {
  width: 35%;
  min-width: 380px;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
}

.right-panel {
  width: 65%;
  background: transparent;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 1.5rem;
}

.panel-content {
  padding: 1rem;
}

.section-wrapper {
  background: rgba(255, 255, 255, 0.6);
  padding: 1.5rem;
  border-radius: 16px;
  margin-bottom: 1.5rem;
  color: $on-surface;
  &:last-child {
    margin-bottom: 0;
  }
}

.section-title {
  font-size: 1.5rem; // text-h5
  font-weight: 600;
  color: var(--md-sys-color-on-surface-variant);
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.section-title-secondary {
  font-size: 1.125rem; // text-subtitle1
  font-weight: 500;
  color: var(--md-sys-color-on-surface-variant);
  margin-bottom: 0.75rem;
}

.results-table {
  background-color: transparent; // Ensure table itself is transparent if section-wrapper provides bg
  color: $on-surface; // Ensure text in table is readable
  thead th {
    color: $primary !important; // Ensure header text color
  }
  tbody td {
    color: $on-surface; // Ensure body text color
  }
}

.status-chip {
  min-width: 60px;
  text-align: center;
}

.circles{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    z-index: 0;
}

.circles div{
    position: absolute;
    display: block;
    list-style: none;
    width: 20px;
    height: 20px;
    background: rgba(255, 255, 255, 0.1);
    animation: animate 25s linear infinite;
    bottom: -150px;
}

/* ... (rest of the .circles div:nth-child styles and @keyframes animate) ... */
</style>
