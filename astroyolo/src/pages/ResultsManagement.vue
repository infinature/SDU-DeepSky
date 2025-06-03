<template>
  <q-page class="results-management-page bg-astroyolo-bg q-pa-md">
    <!-- 顶部标题区域 -->
    <div class="page-header q-pb-md">
      <h1 class="page-title q-my-none flex items-center text-astroyolo-text-primary">
        <q-icon name="insights" size="md" class="q-mr-sm text-astroyolo-secondary-text" />
        检测结果管理
      </h1>
      <div class="page-subtitle text-astroyolo-text-secondary q-mt-xs">查看、分析和导出天体检测结果</div>
    </div>

    <!-- 搜索和过滤工具栏 -->
    <q-card class="search-card q-mb-lg animation-slide-up bg-astroyolo-surface-container">
      <q-card-section>
        <div class="row q-col-gutter-md items-center">
          <div class="col-12 col-md-5">
            <q-input 
              outlined 
              v-model="searchText" 
              placeholder="搜索结果..." 
              dense
              class="search-input"
              label-color="astroyolo-text-secondary"
              input-class="text-astroyolo-text-primary"
            >
              <template v-slot:prepend>
                <q-icon name="search" color="secondary" />
              </template>
              <template v-slot:append v-if="searchText">
                <q-icon name="close" color="astroyolo-text-secondary" class="cursor-pointer" @click="searchText = ''" />
              </template>
            </q-input>
          </div>
          <div class="col-6 col-md-3">
            <q-select 
              outlined 
              v-model="fileType" 
              :options="fileTypes"
              label="检测类型"
              dense
              color="primary"
              label-color="astroyolo-text-secondary"
              popup-content-class="bg-astroyolo-surface-container-high text-astroyolo-text-primary"
              class="filter-select"
            >
              <template v-slot:prepend>
                <q-icon name="filter_list" color="secondary" size="xs" />
              </template>
            </q-select>
          </div>
          <div class="col-6 col-md-3">
            <q-select 
              outlined 
              v-model="sortBy" 
              :options="sortOptions"
              label="排序方式"
              dense
              color="primary"
              label-color="astroyolo-text-secondary"
              popup-content-class="bg-astroyolo-surface-container-high text-astroyolo-text-primary"
              class="filter-select"
            >
              <template v-slot:prepend>
                <q-icon name="sort" color="secondary" size="xs" />
              </template>
            </q-select>
          </div>
          <div class="col-12 col-md-1 text-right">
            <q-btn 
              color="secondary" 
              icon="refresh" 
              round
              flat 
              class="refresh-btn"
              @click="refreshData"
              :loading="isLoading"
            >
              <q-tooltip class="bg-astroyolo-tooltip text-astroyolo-tooltip-text">刷新数据</q-tooltip>
            </q-btn>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- 统计卡片组 -->
    <div class="row q-col-gutter-md q-mb-lg animation-fade-in" style="animation-delay: 200ms">
      <div class="col-12 col-sm-6 col-md-3">
        <q-card class="stat-card bg-astroyolo-surface-container text-astroyolo-text-primary card-hover">
          <q-card-section>
            <div class="stat-header flex items-center text-astroyolo-text-secondary">
              <q-icon name="analytics" class="q-mr-sm" size="sm" />
              <div class="text-subtitle2">总任务数量</div>
            </div>
            <div class="text-h3 text-weight-bold q-mt-sm">{{ stats.totalTasks || 0 }}</div>
            <div class="stat-trend text-caption q-mt-xs text-positive">
              <q-icon name="check_circle" size="xs" /> 实时数据
            </div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-sm-6 col-md-3">
        <q-card class="stat-card bg-astroyolo-surface-container text-astroyolo-text-primary card-hover">
          <q-card-section>
            <div class="stat-header flex items-center text-astroyolo-text-secondary">
              <q-icon name="check_circle" class="q-mr-sm" size="sm" />
              <div class="text-subtitle2">文件总数</div>
            </div>
            <div class="text-h3 text-weight-bold q-mt-sm">{{ stats.totalFiles || 0 }}</div>
            <div class="stat-trend text-caption q-mt-xs text-positive">
              <q-icon name="check_circle" size="xs" /> 所有批次
            </div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-sm-6 col-md-3">
        <q-card class="stat-card bg-astroyolo-surface-container text-astroyolo-text-primary card-hover">
          <q-card-section>
            <div class="stat-header flex items-center text-astroyolo-text-secondary">
              <q-icon name="star" class="q-mr-sm" size="sm" />
              <div class="text-subtitle2">平均每文件检测数</div>
            </div>
            <div class="text-h3 text-weight-bold q-mt-sm">{{ stats.totalFiles > 0 ? Math.round((stats.totalDetections / stats.totalFiles) * 10) / 10 : 0 }}</div>
            <div class="stat-trend text-caption q-mt-xs text-positive">
              <q-icon name="check_circle" size="xs" /> 实时统计
            </div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-sm-6 col-md-3">
        <q-card class="stat-card bg-astroyolo-surface-container text-astroyolo-text-primary card-hover">
          <q-card-section>
            <div class="stat-header flex items-center text-astroyolo-text-secondary">
              <q-icon name="speed" class="q-mr-sm" size="sm" />
              <div class="text-subtitle2">平均处理时间</div>
            </div>
            <div class="text-h3 text-weight-bold q-mt-sm">1.46s</div>
            <div class="stat-trend text-caption q-mt-xs text-negative">
              <q-icon name="trending_down" size="xs" /> 提升 0.3s
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- 检测历史表格 -->
    <q-card class="history-card animation-slide-up bg-astroyolo-surface-container" style="animation-delay: 300ms">
      <q-card-section>
        <div class="table-header flex justify-between items-center q-pb-md">
          <div class="text-h6 flex items-center text-astroyolo-text-primary">
            <q-icon name="history" class="q-mr-sm text-astroyolo-secondary-text" />
            <span>检测历史</span>
          </div>
          <div>
            <q-btn flat round icon="file_download" color="secondary" :disable="detectionHistory.length === 0">
              <q-tooltip class="bg-astroyolo-tooltip text-astroyolo-tooltip-text">导出数据</q-tooltip>
            </q-btn>
          </div>
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="text-negative q-pa-md text-center">
          <q-icon name="error" size="2em" class="q-mr-sm" />
          {{ error }}
        </div>

        <!-- 数据表格 -->
        <q-table
          :rows="detectionHistory"
          :columns="columns"
          row-key="task_id"
          color="primary"
          :pagination="{ rowsPerPage: 10 }"
          :loading="isLoading"
          selection="multiple"
          v-model:selected="selected"
          table-header-class="bg-astroyolo-surface text-astroyolo-text-primary"
          class="history-table text-astroyolo-text-primary"
          card-class="bg-astroyolo-surface-container text-astroyolo-text-primary"
          :rows-per-page-options="[5, 10, 20, 50]"
        >
          <!-- 操作列的自定义渲染 -->
          <template v-slot:body-cell-actions="props">
            <q-td :props="props" class="text-center">
              <div class="row justify-center no-wrap">
                <q-btn round flat size="sm" color="secondary" icon="visibility" @click="viewTaskDetails(props.row.task_id)">
                  <q-tooltip class="bg-astroyolo-tooltip text-astroyolo-tooltip-text">查看详情</q-tooltip>
                </q-btn>
                <q-btn round flat size="sm" color="secondary" icon="file_download">
                  <q-tooltip class="bg-astroyolo-tooltip text-astroyolo-tooltip-text">下载结果</q-tooltip>
                </q-btn>
              </div>
            </q-td>
          </template>

          <!-- 时间列自定义格式 -->
          <template v-slot:body-cell-timestamp="props">
            <q-td :props="props">
              {{ new Date(props.value * 1000).toLocaleString() }}
            </q-td>
          </template>

          <!-- 文件数量列格式化 -->
          <template v-slot:body-cell-files_count="props">
            <q-td :props="props">
              <q-chip size="sm" outline color="blue-grey" text-color="white" icon="folder">
                {{ props.value }}
              </q-chip>
            </q-td>
          </template>

          <!-- 检测目标数格式化 -->
          <template v-slot:body-cell-detection_count="props">
            <q-td :props="props">
              <q-chip size="sm" outline color="green" text-color="white" icon="looks">
                {{ props.value }}
              </q-chip>
            </q-td>
          </template>

          <!-- 成功处理数格式化 -->
          <template v-slot:body-cell-success_count="props">
            <q-td :props="props">
              <q-chip size="sm" outline color="teal" text-color="white" icon="check_circle">
                {{ props.value }}
              </q-chip>
            </q-td>
          </template>
          
          <!-- 分页控件 -->
          <template v-slot:pagination="props">
            <q-pagination
              v-model="props.pagination.page"
              :max="props.pagesNumber"
              :max-pages="6"
              color="secondary"
              active-color="secondary"
              direction-links
              boundary-links
              input
              rounded
              dense
              class="q-my-sm"
            />
          </template>
        </q-table>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { Notify as QNotify } from 'quasar';

defineOptions({
  name: 'ResultsManagement'
});

const router = useRouter();
const apiBaseUrl = process.env.API_URL || 'http://localhost:5000';

// 状态变量
const isLoading = ref(false);
const error = ref('');
const searchText = ref('');
const fileType = ref(null);
const fileTypes = [
  { label: '全部检测', value: 'all' },
  { label: '单图检测', value: 'single' },
  { label: '批量检测', value: 'batch' }
];
const sortBy = ref({ label: '最新优先', value: 'newest' });
const sortOptions = [
  { label: '最新优先', value: 'newest' },
  { label: '最早优先', value: 'oldest' },
  { label: '置信度降序', value: 'confidence' }
];
const selected = ref([]);

// 统计信息
const stats = ref({
  totalTasks: 0,
  totalFiles: 0,
  totalDetections: 0,
  averageConfidence: 0
});

// 表格列定义
const columns = [
  { name: 'task_id', align: 'left', label: '任务ID', field: 'task_id' },
  { name: 'timestamp', align: 'left', label: '检测时间', field: 'timestamp', sortable: true, format: val => new Date(val * 1000).toLocaleString() },
  { name: 'files_count', align: 'center', label: '文件数量', field: 'files_count', sortable: true },
  { name: 'detection_count', align: 'center', label: '检测目标数', field: 'detection_count', sortable: true },
  { name: 'success_count', align: 'center', label: '成功处理数', field: 'success_count', sortable: true },
  { name: 'actions', align: 'center', label: '操作', field: 'actions' }
];

// 检测历史记录
const detectionHistory = ref([]);

// 加载检测历史记录
const loadHistoryResults = async () => {
  try {
    isLoading.value = true;
    error.value = '';
    
    // 从后端API获取历史检测记录列表
    const response = await axios.get(`${apiBaseUrl}/api/tasks`);
    
    if (response.data.status === 'success' && response.data.tasks) {
      detectionHistory.value = response.data.tasks;
      
      // 计算统计信息
      stats.value.totalTasks = detectionHistory.value.length;
      stats.value.totalFiles = detectionHistory.value.reduce((sum, task) => sum + (task.files_count || 0), 0);
      stats.value.totalDetections = detectionHistory.value.reduce((sum, task) => sum + (task.detection_count || 0), 0);
      
      // 排序处理
      sortHistoryResults();
    } else {
      error.value = response.data.message || '未能获取任务列表';
      QNotify.create({
        color: 'negative',
        message: '加载历史记录失败: ' + error.value,
        position: 'top',
        timeout: 3000
      });
    }
  } catch (err) {
    console.error('加载历史记录出错', err);
    error.value = err.response?.data?.message || err.message || '服务器连接错误';
    QNotify.create({
      color: 'negative',
      message: '加载历史记录失败: ' + error.value,
      position: 'top',
      timeout: 3000
    });
  } finally {
    isLoading.value = false;
  }
};

// 根据排序选项对结果进行排序
const sortHistoryResults = () => {
  const sortValue = sortBy.value.value;
  let sortedResults = [...detectionHistory.value];
  
  if (sortValue === 'newest') {
    sortedResults.sort((a, b) => b.timestamp - a.timestamp);
  } else if (sortValue === 'oldest') {
    sortedResults.sort((a, b) => a.timestamp - b.timestamp);
  } else if (sortValue === 'confidence') {
    // 如果有置信度信息，可以根据置信度排序
    sortedResults.sort((a, b) => b.detection_count - a.detection_count);
  }
  
  detectionHistory.value = sortedResults;
};

// 刷新数据
const refreshData = () => {
  loadHistoryResults();
};

// 查看任务详情
const viewTaskDetails = (taskId) => {
  if (!taskId) {
    QNotify.create({
      color: 'negative',
      message: '无效的任务ID',
      position: 'top'
    });
    return;
  }
  
  // 导航到结果显示页面
  router.push({ name: 'ResultDisplay', params: { taskId } });
};

// 在组件挂载时加载数据
onMounted(() => {
  loadHistoryResults();
});
</script>

<style lang="scss" scoped>
// SASS color module now imported via quasar.config.js additionalData

.results-management-page {
  padding: 32px;
}

// 页面标题样式
.page-header {
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: $astroyolo-text-primary;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.page-subtitle {
  font-size: 1rem;
  letter-spacing: 0.3px;
  opacity: 0.8;
}

// 卡片样式
.search-card, .history-card {
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
}

// 表格头部样式
.table-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
}

// 表格样式
:deep(.history-table) {
  color: $astroyolo-text-primary;
  
  .q-table__top,
  .q-table__bottom {
    padding: 8px 16px;
  }
  
  thead tr {
    background-color: rgba($astroyolo-text-secondary, 0.05);
    th {
      color: $astroyolo-text-primary;
      font-weight: 500;
      padding: 10px 16px;
      border-bottom: 2px solid rgba($astroyolo-text-secondary, 0.2);
    }
  }
  
  tbody tr {
    transition: all 0.2s ease;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    
    &:hover {
      background-color: rgba(255, 255, 255, 0.05) !important;
    }
    
    &.bg-secondary-1 {
      background-color: rgba($astroyolo-text-secondary, 0.1);
    }
    
    td {
      padding: 10px 16px;
    }
  }
  
  .q-checkbox {
    .q-checkbox__inner {
      color: $astroyolo-text-primary;
    }
  }
}

// 统计卡片样式
.stat-card {
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  
  &.card-hover {
    cursor: pointer;
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
    }
  }
  
  .stat-header {
    opacity: 0.8;
    margin-bottom: 0.5rem;
  }
  
  .text-h3 {
    font-weight: 700;
    margin: 10px 0 5px 0;
  }
  
  .stat-trend {
    opacity: 0.8;
    font-size: 0.8rem;
  }
  
  // 设置渐变背景
  &.blue-card {
    background: linear-gradient(135deg, rgba(81, 118, 236, 0.85), rgba(81, 118, 236, 0.65));
  }
  &.green-card {
    background: linear-gradient(135deg, rgba(66, 184, 131, 0.85), rgba(66, 184, 131, 0.65));
  }
  &.purple-card {
    background: linear-gradient(135deg, rgba(142, 68, 173, 0.85), rgba(142, 68, 173, 0.65));
  }
  &.cyan-card {
    background: linear-gradient(135deg, rgba(52, 152, 219, 0.85), rgba(52, 152, 219, 0.65));
  }
}

// 搜索输入和下拉选择器样式
.search-input, .filter-select {
  .q-field__control {
    background-color: rgba(255, 255, 255, 0.05) !important;
    transition: all 0.3s ease;
    
    &:hover {
      background-color: rgba(255, 255, 255, 0.08) !important;
    }
  }
}

.light-popup {
  background-color: $astroyolo-surface-container-high !important;
  color: $astroyolo-text-primary !important;
}

// ID标记和数量标签样式
.id-badge {
  background-color: rgba($astroyolo-text-secondary, 0.15);
  color: $astroyolo-text-secondary;
  border-radius: 4px;
  padding: 2px 6px;
  display: inline-block;
  font-size: 0.9rem;
}

.count-chip {
  font-weight: 500;
  font-size: 0.9rem;
  padding: 2px 8px;
}

// 刷新按钮动画
.refresh-btn {
  transition: all 0.3s ease;
  
  &:hover {
    transform: rotate(180deg);
  }
}

// 动画效果
.animation-slide-up {
  animation: slideUp 0.6s ease forwards;
}

.animation-fade-in {
  animation: fadeIn 0.8s ease forwards;
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

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
