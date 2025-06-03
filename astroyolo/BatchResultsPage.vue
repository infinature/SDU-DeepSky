<template>
  <q-page padding class="batch-results-page" style="background-color: #ffffff;">
    <div class="row justify-center q-mb-md">
      <div class="col-12 col-md-10 text-center">
        <h4 class="text-h5 q-mb-md text-weight-bold" style="color: var(--md-sys-color-primary)">天文图像检测结果管理</h4>
      </div>
    </div>

    <div v-if="loading" class="q-pa-md text-center">
      <q-spinner
        color="primary"
        size="3em"
        class="q-mb-md"
      />
      <div>正在加载结果数据...</div>
    </div>

    <div v-else-if="!taskData" class="q-pa-md text-center">
      <q-icon name="error_outline" size="3em" color="negative" />
      <div class="q-mt-sm text-negative text-body2">找不到检测结果数据</div>
      <q-btn
        color="primary"
        class="q-mt-md"
        to="/batch-detection"
        icon="arrow_back"
        label="返回批量检测"
      />
    </div>

    <div v-else class="row justify-center">
      <div class="col-12 col-md-10">
        <!-- 结果标题 -->
        <div class="text-h5 q-mb-md flex items-center q-pa-sm rounded-borders" style="background-color: #1976d2; color: #ffffff;">
          <q-icon name="insert_chart" size="md" class="q-mr-sm" />
          <span>检测结果详情</span>
          <q-space />
          <q-btn
            flat
            round
            icon="arrow_back"
            color="primary"
            @click="goBack"
            class="q-mr-sm"
          />
          <q-btn
            outline
            color="primary"
            icon-right="download"
            label="下载结果"
            @click="downloadResults"
          />
        </div>

        <!-- 结果摘要卡片 -->
        <q-card flat class="q-mb-md shadow-1">
          <q-card-section style="background-color: var(--md-sys-color-secondary-container); color: var(--md-sys-color-on-secondary-container);">
            <div class="text-subtitle1 q-mb-sm">检测摘要</div>
            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-4">
                <q-item>
                  <q-item-section avatar>
                    <q-icon name="photo_library" color="primary" size="md" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>检测文件</q-item-label>
                    <q-item-label caption>{{ taskData?.files_count || 0 }} 个文件</q-item-label>
                  </q-item-section>
                </q-item>
              </div>
              <div class="col-12 col-sm-4">
                <q-item>
                  <q-item-section avatar>
                    <q-icon name="find_in_page" color="primary" size="md" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>识别对象</q-item-label>
                    <q-item-label caption>{{ taskData?.detection_count || 0 }} 个目标</q-item-label>
                  </q-item-section>
                </q-item>
              </div>
              <div class="col-12 col-sm-4">
                <q-item>
                  <q-item-section avatar>
                    <q-icon name="check_circle_outline" color="primary" size="md" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>成功率</q-item-label>
                    <q-item-label caption>{{ calcSuccessRate() }}%</q-item-label>
                  </q-item-section>
                </q-item>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- 下载和设置路径按钮 -->
        <q-card flat class="q-mb-md shadow-1" style="background-color: var(--md-sys-color-surface-container-low);">
          <q-card-section>
            <div class="row items-center">
              <div class="col-12 col-sm-4 q-mb-sm-0 q-mb-md">
                <div class="text-subtitle1" style="color: var(--md-sys-color-primary);">结果管理</div>
                <div class="text-caption" style="color: var(--md-sys-color-on-surface-variant);">您可以下载所有结果或设置保存路径</div>
              </div>
              <div class="col-12 col-sm-8 text-right">
                <q-btn 
                  style="background-color: var(--md-sys-color-primary); color: var(--md-sys-color-on-primary);" 
                  icon="download" 
                  label="下载所有结果" 
                  @click="downloadResults" 
                  :disable="!taskData || !taskData.results || taskData.results.length === 0"
                  padding="sm md"
                  class="q-mr-sm"
                />
                <q-btn 
                  flat
                  style="color: var(--md-sys-color-primary);" 
                  icon="folder" 
                  label="设置路径" 
                  @click="showPathDialog = true"
                  padding="sm md"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- 结果列表卡片 -->
        <q-card flat class="q-mb-md shadow-1">
          <q-card-section style="background-color: #80aaa0; color: #ffffff;">
            <div class="text-subtitle1 q-mb-sm">检测结果详情</div>
            
            <div class="q-mb-md">
              <q-input
                v-model="searchTerm"
                outlined
                dense
                bg-color="white"
                color="primary"
                placeholder="搜索文件名"
                class="q-mb-md search-input"
                style="background-color: #ffffff;"
              >
                <template v-slot:append>
                  <q-icon name="search" color="#1976d2" />
                </template>
              </q-input>
              
              <q-table
                :rows="filteredResults"
                :columns="columns"
                row-key="id"
                :pagination="{ rowsPerPage: 10 }"
                class="results-table"
                style="background-color: #ffffff;"
                color="#1976d2"
                flat
              >
                <template v-slot:body="props">
                  <q-tr :props="props">
                    <q-td key="filename" :props="props">
                      {{ props.row.filename }}
                    </q-td>
                    <q-td key="status" :props="props">
                      <q-chip 
                        :style="props.row.status === 'error' ? 'background-color: #c72c27; color: #ffffff;' : 'background-color: #1976d2; color: #ffffff;'" 
                        size="sm"
                        class="status-chip"
                      >
                        {{ props.row.status === 'error' ? '失败' : '成功' }}
                      </q-chip>
                    </q-td>
                    <q-td key="detection_count" :props="props">
                      {{ props.row.detection_count || 0 }}
                    </q-td>
                    <q-td key="actions" :props="props">
                      <q-btn
                        v-if="props.row.status !== 'error'"
                        flat
                        round
                        size="sm"
                        style="color: #1976d2;"
                        icon="visibility"
                        @click="previewImage(props.row)"
                      />
                      <q-btn
                        v-if="props.row.status !== 'error'"
                        flat
                        round
                        size="sm"
                        style="color: #1976d2;"
                        icon="download"
                        @click="downloadSingleResult(props.row)"
                      />
                      <q-tooltip v-if="props.row.status === 'error'">
                        {{ props.row.message || '处理失败' }}
                      </q-tooltip>
                    </q-td>
                  </q-tr>
                </template>
              </q-table>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- 预览对话框 -->
    <q-dialog v-model="showPreview" maximized>
      <q-card class="preview-dialog">
        <q-card-section class="row items-center q-pb-none" style="background-color: #1976d2; color: #ffffff;">
          <div class="text-h6">{{ previewItem?.filename || '检测结果预览' }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup text-color="white" />
        </q-card-section>

        <q-card-section>
          <div class="row">
            <!-- 图片预览区域 -->
            <div class="col-12 col-md-8">
              <div class="text-center">
                <q-img
                  :src="previewUrl"
                  style="max-height: 70vh; max-width: 100%"
                  fit="contain"
                />
              </div>
              <div class="text-center q-my-md">
                <q-btn style="background-color: #1976d2; color: #ffffff;" icon="download" label="下载当前结果" @click="downloadSingleResult(previewItem)" class="q-px-md" />
              </div>
              <div class="text-center q-mt-md">
                <q-chip style="background-color: #1976d2; color: #ffffff;" class="glossy">
                  检测到 {{ previewItem?.detection_count || 0 }} 个目标
                </q-chip>
              </div>
            </div>

            <!-- 检测数据详情区域 -->
            <div class="col-12 col-md-4">
              <q-card flat bordered class="q-ml-md">
                <q-card-section style="background-color: #1976d2; color: #ffffff;">
                  <div class="text-h6">检测数据详情</div>
                </q-card-section>
                
                <q-separator color="#1976d2" />
                
                <q-card-section>
                  <div v-if="previewItem?.boxes && previewItem.boxes.length > 0">
                    <q-list separator>
                      <q-item v-for="box in previewItem.boxes" :key="box.id">
                        <q-item-section>
                          <q-item-label header class="text-primary">目标 #{{ box.id }}</q-item-label>
                          <q-item-label caption>
                            <div class="row">
                              <div class="col-6">置信度：</div>
                              <div class="col-6">{{ (box.confidence * 100).toFixed(2) }}%</div>
                            </div>
                            <div class="row">
                              <div class="col-6">坐标：</div>
                              <div class="col-6">
                                ({{ Math.round(box.x1) }}, {{ Math.round(box.y1) }}) -<br>
                                ({{ Math.round(box.x2) }}, {{ Math.round(box.y2) }})
                              </div>
                            </div>
                            <div class="row">
                              <div class="col-6">特征值：</div>
                              <div class="col-6">
                                宽: {{ Math.round(box.x2 - box.x1) }}像素<br>
                                高: {{ Math.round(box.y2 - box.y1) }}像素
                              </div>
                            </div>
                          </q-item-label>
                        </q-item-section>
                        
                        <q-item-section side>
                          <q-badge style="color: #1976d2; border-color: #1976d2;" outline>
                            星系 {{ box.class_id === 0 ? '星系' : '未知' }}
                          </q-badge>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </div>
                  <div v-else class="text-center q-pa-md">
                    <q-icon name="search_off" size="3rem" color="grey-7" />
                    <div class="text-grey-7 q-mt-sm">没有检测到目标</div>
                  </div>
                </q-card-section>
                
                <q-separator />
                
                <q-card-section>
                  <div class="text-caption" style="color: #666666;">
                    文件名：{{ previewItem?.filename || '未知' }}<br>
                    目标类型：天体天文学<br>
                    检测时间：{{ new Date().toLocaleString() }}
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="关闭" style="color: #1976d2;" v-close-popup />
          <q-btn 
            flat 
            label="下载" 
            style="color: #1976d2;" 
            icon="download"
            @click="downloadSingleResult(previewItem)"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- 设置下载路径对话框 -->
    <q-dialog v-model="showPathDialog">
      <q-card style="min-width: 350px" class="path-dialog">
        <q-card-section class="row items-center q-pb-none" style="background-color: #1976d2; color: #ffffff;">
          <div class="text-h6">设置下载路径</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup text-color="white" />
        </q-card-section>
        
        <q-card-section>
          <p class="text-body2 q-my-md">
            请选择一个文件夹来保存检测结果。系统会尝试记住你的选择，但出于浏览器安全限制，你可能需要在每次使用时重新授权。
          </p>
          
          <div class="q-mt-md text-center">
            <q-btn style="background-color: #1976d2; color: #ffffff;" label="选择文件夹" icon="folder" @click="selectDownloadPath" class="full-width" />
          </div>
          
          <div v-if="userDownloadPath" class="q-mt-md">
            <q-banner style="background-color: #f7f7f7; color: #1976d2;">
              <template v-slot:avatar>
                <q-icon name="folder" style="color: #1976d2;" size="sm" />
              </template>
              <span class="text-body2">
                当前路径: {{ userDownloadPath }}
              </span>
            </q-banner>
          </div>
        </q-card-section>
        
        <q-card-actions align="right">
          <q-btn flat label="关闭" style="color: #1976d2;" v-close-popup class="q-px-md" />
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

// 返回按钮
function goBack() {
  router.push('/batch-detection');
}
</script>

<style lang="scss" scoped>
.batch-results-page {
  min-height: 100vh;
}

.preview-dialog,
.path-dialog {
  border-radius: 8px;
  overflow: hidden;
}

.preview-dialog .q-card__section,
.path-dialog .q-card__section {
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.text-weight-bold {
  font-weight: 600;
}

.rounded-borders {
  border-radius: 4px;
}

.results-table {
  border-radius: 4px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
}

:deep(.q-table__container) {
  background-color: #ffffff;
}

:deep(.q-table th) {
  background-color: #f0f4f8 !important;
  color: #133665 !important;
  font-weight: 600 !important;
}

:deep(.q-table tr) {
  background-color: #ffffff !important;
}

:deep(.q-table td) {
  color: #333333 !important;
}

.batch-results-page .q-table thead tr {
  background-color: #f0f4f8;
}

.batch-results-page .q-table thead th {
  font-weight: 600;
  color: #133665;
}

.batch-results-page .q-table tbody tr:hover {
  background-color: rgba(25, 118, 210, 0.05);
}

.search-input {
  max-width: 300px;
}

.status-chip {
  font-weight: 500;
}

.shadow-1 {
  box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.12);
}

.detection-logo {
  width: 40px;
  height: 40px;
  margin-right: 10px;
}

/* 使用light-mc.css的颜色变量 */
:deep(.q-table__grid-content) {
  row-gap: 5px;
  background-color: #ffffff;
}

:deep(.q-card) {
  background-color: #ffffff !important;
  color: #333333 !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.12);
}

:deep(.q-table) {
  background-color: #ffffff !important;
  color: #333333 !important;
}

:deep(.q-table th) {
  background-color: #f0f4f8 !important;
  color: #133665 !important;
  font-weight: 600 !important;
}
</style>
