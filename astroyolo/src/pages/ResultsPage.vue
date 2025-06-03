<template>
  <q-page padding class="bg-astroyolo-bg">
    <div class="row justify-center">
      <div class="col-12 col-md-10">
        <div class="text-h5 q-mb-md text-astroyolo-text-primary">检测结果管理</div>
      
        <!-- 筛选和排序工具栏 -->
        <q-card class="q-mb-md bg-astroyolo-card" flat bordered>
          <q-card-section>
            <div class="row q-col-gutter-md items-center">
              <div class="col-md-4 col-sm-6 col-xs-12">
                <q-input
                  v-model="search"
                  outlined
                  dense
                  placeholder="搜索结果..."
                  clearable
                  bg-color="astroyolo-card"
                  color="primary"
                  class="search-input"
                >
                  <template v-slot:append>
                    <q-icon name="search" color="astroyolo-primary" />
                  </template>
                </q-input>
              </div>
              
              <div class="col-md-3 col-sm-6 col-xs-12">
                <q-select
                  v-model="timeFilter"
                  :options="timeFilterOptions"
                  outlined
                  dense
                  label="时间筛选"
                  bg-color="astroyolo-card"
                  color="primary"
                />
              </div>
              
              <div class="col-md-3 col-sm-6 col-xs-12">
                <q-select
                  v-model="sortBy"
                  :options="sortOptions"
                  outlined
                  dense
                  label="排序方式"
                  bg-color="astroyolo-card"
                  color="primary"
                />
              </div>
              
              <div class="col-md-2 col-sm-6 col-xs-12">
                <q-btn icon="refresh" label="刷新" color="primary" flat @click="refreshResults" />
              </div>
            </div>
          </q-card-section>
        </q-card>
      
      <!-- 结果统计信息 -->
      <div class="row q-col-gutter-md q-mb-md">
        <div class="col-md-3 col-sm-6 col-xs-12">
          <q-card class="bg-astroyolo-surface-container-low" flat>
            <q-card-section>
              <div class="text-body2 text-astroyolo-text-secondary">总检测数量</div>
              <div class="text-subtitle1 text-astroyolo-text-primary">{{ stats.total }}</div>
            </q-card-section>
          </q-card>
        </div>
        
        <div class="col-md-3 col-sm-6 col-xs-12">
          <q-card class="bg-astroyolo-surface-container" flat>
            <q-card-section>
              <div class="text-body2 text-astroyolo-text-secondary">今日检测</div>
              <div class="text-subtitle1 text-astroyolo-text-primary">{{ stats.today }}</div>
            </q-card-section>
          </q-card>
        </div>
        
        <div class="col-md-3 col-sm-6 col-xs-12">
          <q-card class="bg-astroyolo-surface-container-low" flat>
            <q-card-section>
              <div class="text-body2 text-astroyolo-text-secondary">检测目标数</div>
              <div class="text-subtitle1 text-astroyolo-text-primary">{{ stats.objects }}</div>
            </q-card-section>
          </q-card>
        </div>
        
        <div class="col-md-3 col-sm-6 col-xs-12">
          <q-card class="bg-astroyolo-surface-container-high" flat>
            <q-card-section>
              <div class="text-body2 text-astroyolo-text-secondary">平均处理时间</div>
              <div class="text-subtitle1 text-astroyolo-text-primary">{{ stats.avgTime }}s</div>
            </q-card-section>
          </q-card>
        </div>
      </div>
      
      <!-- 结果表格 -->
      <q-card class="q-mb-lg bg-astroyolo-card" flat bordered>
        <q-card-section class="row items-center">
          <div class="text-subtitle1 text-astroyolo-text-primary">检测历史</div>
          <q-space />
          <q-btn flat round icon="archive" size="sm" color="primary" @click="exportAllResults">
            <q-tooltip>导出所有结果</q-tooltip>
          </q-btn>
          <q-btn flat round icon="delete" size="sm" color="negative" @click="confirmDeleteSelected" :disable="!hasSelectedItems">
            <q-tooltip>删除所选</q-tooltip>
          </q-btn>
        </q-card-section>
        
        <q-separator color="astroyolo-outline-variant" />
        
        <q-card-section class="row items-center">
          <q-table
            :rows="filteredResults"
            :columns="columns"
            row-key="id"
            :loading="loading"
            :pagination="pagination"
            selection="multiple"
            v-model:selected="selected"
            flat
            color="primary"
            class="my-custom-table full-width"
          >
            <template v-slot:header="props">
              <q-tr :props="props" class="custom-header-row bg-astroyolo-surface-container-low">
                <q-th auto-width class="text-astroyolo-primary">
                  <q-checkbox v-model="allSelected" @update:model-value="selectAllRows" />
                </q-th>
                <q-th v-for="col in props.cols" :key="col.name" :props="props" :class="col.classes" class="text-astroyolo-primary">
                  {{ col.label }}
                </q-th>
              </q-tr>
            </template>
            
            <template v-slot:body="props">
              <q-tr :props="props" class="custom-body-row bg-astroyolo-card">
                <q-td auto-width class="text-astroyolo-text-primary">
                  <q-checkbox v-model="props.selected" />
                </q-td>
                <q-td key="id" :props="props" class="text-astroyolo-text-primary">
                  {{ props.row.id }}
                </q-td>
                <q-td key="filename" :props="props" class="text-astroyolo-text-primary">
                  {{ props.row.filename }}
                </q-td>
                <q-td key="timestamp" :props="props" class="text-astroyolo-text-primary">
                  {{ formatDate(props.row.timestamp) }}
                </q-td>
                <q-td key="detections" :props="props" class="text-astroyolo-text-primary">
                  {{ props.row.detections }}
                </q-td>
                <q-td key="confidence" :props="props" class="text-astroyolo-text-primary">
                  {{ props.row.confidence }}
                </q-td>
                <q-td key="actions" :props="props" class="text-astroyolo-text-primary">
                  <div class="row q-gutter-xs justify-center">
                    <q-btn flat round dense icon="visibility" color="primary" @click="viewResult(props.row)">
                      <q-tooltip>查看</q-tooltip>
                    </q-btn>
                    <q-btn flat round dense icon="download" color="primary" @click="downloadResult(props.row)">
                      <q-tooltip>下载</q-tooltip>
                    </q-btn>
                    <q-btn flat round dense icon="delete" color="negative" @click="confirmDelete(props.row)">
                      <q-tooltip>删除</q-tooltip>
                    </q-btn>
                  </div>
                </q-td>
              </q-tr>
            </template>
            
            <template v-slot:loading>
              <q-inner-loading showing color="primary" />
            </template>
            
            <template v-slot:no-data>
              <div class="full-width row flex-center q-pa-md text-negative">
                <q-icon name="sentiment_dissatisfied" size="2em" />
                <span class="q-ml-sm text-astroyolo-text-primary">没有检测结果数据</span>
              </div>
            </template>
          </q-table>
        </q-card-section>
      </q-card>
    </div>
    
    <!-- 结果详情对话框 -->
    <q-dialog v-model="showResultDialog" maximized transition-show="slide-up" transition-hide="slide-down">
      <q-card>
        <q-card-section class="row items-center">
          <div class="text-h6">检测结果详情</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        
        <q-separator />
        
        <q-card-section v-if="selectedResult" style="max-height: 80vh" class="scroll">
          <div class="row q-col-gutter-lg">
            <!-- 左侧：结果图像 -->
            <div class="col-md-8 col-sm-12">
              <q-card flat bordered>
                <q-card-section>
                  <div class="text-subtitle1">检测结果图像</div>
                </q-card-section>
                
                <q-card-section class="q-pa-none">
                  <q-img
                    src="/img/placeholder-result.jpg"
                    spinner-color="primary"
                    style="height: 500px; max-width: 100%"
                  />
                </q-card-section>
              </q-card>
            </div>
            
            <!-- 右侧：检测信息 -->
            <div class="col-md-4 col-sm-12">
              <q-card flat bordered>
                <q-card-section>
                  <div class="text-subtitle1">基本信息</div>
                </q-card-section>
                
                <q-list bordered padding>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>文件名</q-item-label>
                      <q-item-label>{{ selectedResult.filename }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>检测时间</q-item-label>
                      <q-item-label>{{ formatDate(selectedResult.timestamp) }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>检测模型</q-item-label>
                      <q-item-label>{{ selectedResult.model || '标准模型' }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>置信度阈值</q-item-label>
                      <q-item-label>{{ selectedResult.confidence }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>处理时间</q-item-label>
                      <q-item-label>{{ selectedResult.processingTime || '1.25' }}s</q-item-label>
                    </q-item-section>
                  </q-item>
                  
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>检测对象数量</q-item-label>
                      <q-item-label>{{ selectedResult.detections }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card>
              
              <q-card flat bordered class="q-mt-md">
                <q-card-section>
                  <div class="text-subtitle1">检测对象</div>
                </q-card-section>
                
                <q-list bordered separator>
                  <q-item v-for="i in selectedResult.detections" :key="i">
                    <q-item-section>
                      <q-item-label>天体对象 {{ i }}</q-item-label>
                      <q-item-label caption>置信度: {{ (Math.random() * 0.3 + 0.7).toFixed(2) }}</q-item-label>
                      <q-item-label caption>坐标: ({{ Math.floor(Math.random() * 1000) }}, {{ Math.floor(Math.random() * 1000) }})</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-badge color="primary">{{ ['star', 'nebula', 'galaxy'][i % 3] }}</q-badge>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar, date } from 'quasar'

const $q = useQuasar()

// 状态变量
const loading = ref(false)
const results = ref([])
const selected = ref([])
const allSelected = ref(false)
const search = ref('')
const timeFilter = ref('all')
const sortBy = ref('newest')
const showResultDialog = ref(false)
const selectedResult = ref(null)

// 分页设置
const pagination = ref({
  rowsPerPage: 10,
  sortBy: 'timestamp',
  descending: true
})

// 筛选选项
const timeFilterOptions = [
  { label: '所有时间', value: 'all' },
  { label: '今天', value: 'today' },
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' }
]

// 排序选项
const sortOptions = [
  { label: '最新优先', value: 'newest' },
  { label: '最早优先', value: 'oldest' },
  { label: '检测数量 ↑', value: 'detections-asc' },
  { label: '检测数量 ↓', value: 'detections-desc' },
  { label: '置信度 ↑', value: 'confidence-asc' },
  { label: '置信度 ↓', value: 'confidence-desc' }
]

// 表格列定义
const columns = [
  { name: 'id', align: 'left', label: 'ID', field: 'id', sortable: true },
  { name: 'filename', align: 'left', label: '文件名', field: 'filename', sortable: true },
  { name: 'timestamp', align: 'left', label: '检测时间', field: 'timestamp', sortable: true, format: val => formatDate(val) },
  { name: 'detections', align: 'center', label: '检测数量', field: 'detections', sortable: true },
  { name: 'confidence', align: 'center', label: '置信度', field: 'confidence', sortable: true },
  { name: 'actions', align: 'center', label: '操作', field: 'actions' }
]

// 统计信息
const stats = ref({
  total: 0,
  today: 0,
  objects: 0,
  avgTime: 0
})

// 计算属性：是否有选中的项目
const hasSelectedItems = computed(() => selected.value.length > 0)

// 计算属性：筛选后的结果
const filteredResults = computed(() => {
  let filtered = results.value
  
  // 搜索筛选
  if (search.value) {
    const searchLower = search.value.toLowerCase()
    filtered = filtered.filter(item => {
      return item.filename.toLowerCase().includes(searchLower) ||
             item.id.toString().includes(searchLower)
    })
  }
  
  // 时间筛选
  if (timeFilter.value !== 'all') {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const weekStart = new Date(today)
    weekStart.setDate(today.getDate() - today.getDay())
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1)
    
    filtered = filtered.filter(item => {
      const itemDate = new Date(item.timestamp)
      if (timeFilter.value === 'today') {
        return itemDate >= today
      } else if (timeFilter.value === 'week') {
        return itemDate >= weekStart
      } else if (timeFilter.value === 'month') {
        return itemDate >= monthStart
      }
      return true
    })
  }
  
  // 排序
  if (sortBy.value === 'newest') {
    filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
  } else if (sortBy.value === 'oldest') {
    filtered.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
  } else if (sortBy.value === 'detections-asc') {
    filtered.sort((a, b) => a.detections - b.detections)
  } else if (sortBy.value === 'detections-desc') {
    filtered.sort((a, b) => b.detections - a.detections)
  } else if (sortBy.value === 'confidence-asc') {
    filtered.sort((a, b) => parseFloat(a.confidence) - parseFloat(b.confidence))
  } else if (sortBy.value === 'confidence-desc') {
    filtered.sort((a, b) => parseFloat(b.confidence) - parseFloat(a.confidence))
  }
  
  return filtered
})

// 格式化日期
const formatDate = (timestamp) => {
  return date.formatDate(timestamp, 'YYYY-MM-DD HH:mm:ss')
}

// 查看结果详情
const viewResult = (row) => {
  selectedResult.value = row
  showResultDialog.value = true
}

// 下载结果
const downloadResult = (row) => {
  $q.notify({
    type: 'info',
    message: `正在下载 ${row.filename} 的检测结果...`,
    position: 'top'
  })
  
  // 在实际应用中，这里应该调用下载API
  setTimeout(() => {
    $q.notify({
      type: 'positive',
      message: '下载完成',
      position: 'top'
    })
  }, 2000)
}

// 确认删除单个结果
const confirmDelete = (row) => {
  $q.dialog({
    title: '确认删除',
    message: `是否确定删除 ${row.filename} 的检测结果？`,
    cancel: true,
    persistent: true
  }).onOk(() => {
    deleteResult(row)
  })
}

// 删除单个结果
const deleteResult = (row) => {
  // 在实际应用中，这里应该调用删除API
  results.value = results.value.filter(item => item.id !== row.id)
  selected.value = selected.value.filter(item => item.id !== row.id)
  updateStats()
  
  $q.notify({
    type: 'positive',
    message: '删除成功',
    position: 'top'
  })
}

// 确认删除选中项
const confirmDeleteSelected = () => {
  if (selected.value.length === 0) return
  
  $q.dialog({
    title: '确认批量删除',
    message: `是否确定删除选中的 ${selected.value.length} 项检测结果？`,
    cancel: true,
    persistent: true
  }).onOk(() => {
    deleteSelected()
  })
}

// 删除选中项
const deleteSelected = () => {
  // 在实际应用中，这里应该调用批量删除API
  const selectedIds = selected.value.map(item => item.id)
  results.value = results.value.filter(item => !selectedIds.includes(item.id))
  selected.value = []
  allSelected.value = false
  updateStats()
  
  $q.notify({
    type: 'positive',
    message: '批量删除成功',
    position: 'top'
  })
}

// 选择/取消选择所有行
const selectAllRows = () => {
  if (allSelected.value) {
    selected.value = [...filteredResults.value]
  } else {
    selected.value = []
  }
}

// 刷新结果列表
const refreshResults = () => {
  loading.value = true
  
  // 在实际应用中，这里应该调用API获取最新结果
  setTimeout(() => {
    fetchResults()
    loading.value = false
    
    $q.notify({
      type: 'positive',
      message: '数据已刷新',
      position: 'top'
    })
  }, 1000)
}

// 导出所有结果
const exportAllResults = () => {
  $q.notify({
    type: 'info',
    message: '正在准备导出所有结果...',
    position: 'top'
  })
  
  // 在实际应用中，这里应该调用导出API
  setTimeout(() => {
    $q.notify({
      type: 'positive',
      message: '导出完成',
      position: 'top'
    })
  }, 2000)
}

// 获取检测结果数据
const fetchResults = () => {
  // 在实际应用中，这里应该调用API获取数据
  // 模拟数据
  results.value = Array.from({ length: 50 }, (_, i) => ({
    id: i + 1,
    filename: `astro_image_${i + 1}.jpg`,
    timestamp: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
    detections: Math.floor(Math.random() * 15) + 1,
    confidence: (Math.random() * 0.3 + 0.7).toFixed(2),
    model: ['标准模型', '高精度模型', '快速模型'][Math.floor(Math.random() * 3)],
    processingTime: (Math.random() * 2 + 0.5).toFixed(2)
  }))
  
  updateStats()
}

// 更新统计信息
const updateStats = () => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  
  const todayResults = results.value.filter(item => new Date(item.timestamp) >= today)
  const totalObjects = results.value.reduce((sum, item) => sum + item.detections, 0)
  const totalTime = results.value.reduce((sum, item) => sum + parseFloat(item.processingTime || '1'), 0)
  
  stats.value = {
    total: results.value.length,
    today: todayResults.length,
    objects: totalObjects,
    avgTime: results.value.length ? (totalTime / results.value.length).toFixed(2) : '0.00'
  }
}

// 初始化
onMounted(() => {
  // 获取检测结果数据
  loading.value = true
  setTimeout(() => {
    fetchResults()
    loading.value = false
  }, 1000)
})
</script>

<style lang="scss">
/* 表格样式 */
:deep(.q-table), 
:deep(.q-table__container), 
:deep(.q-table__middle), 
:deep(.q-table__bottom),
:deep(.q-table__control),
:deep(.q-table--horizontal-separator tbody tr:not(:last-child) > td),
:deep(.q-table--vertical-separator td),
:deep(.q-table--vertical-separator th),
:deep(.q-table--horizontal-separator thead tr:last-child > th) {
  background-color: #ffffff !important;
  color: #333333 !important;
  border-color: #e0e0e0 !important;
}

:deep(.q-table thead tr),
:deep(.q-table thead th) {
  background-color: #f0f4f8 !important;
  color: #133665 !important;
  border-top: none !important;
}

:deep(.q-table tbody tr) {
  background-color: #ffffff !important;
}

:deep(.q-table tbody td) {
  background-color: #ffffff !important;
  color: #333333 !important;
}

:deep(.q-checkbox__inner) {
  color: #1976d2 !important;
}

:deep(.q-btn) {
  color: #1976d2;
}

:deep(.q-dialog__inner) {
  background-color: rgba(0, 0, 0, 0.2) !important;
}

:deep(.q-dialog__inner .q-card) {
  background-color: #ffffff !important;
}

/* 确保所有卡片和表格背景为白色 */
:deep(.q-card),
:deep(.q-table) {
  background-color: #ffffff !important;
  color: #333333 !important;
  border-radius: 8px;
  box-shadow: 0 1px 5px rgba(0,0,0,0.08) !important;
}

/* 搜索框和输入组件 */
:deep(.q-field__control) {
  background-color: #ffffff !important;
  color: #333333 !important;
}

:deep(.q-field__marginal) {
  background-color: #ffffff !important;
  color: #1976d2 !important;
}

/* 重置默认的黑色背景 */
:deep(.q-dark),
:deep([class*="bg-"]:not(.bg-white):not(.bg-blue-1):not(.bg-green-1):not(.bg-purple-1)) {
  background-color: #ffffff !important;
  color: #333333 !important;
}

.my-custom-table {
  background-color: #ffffff !important;
  border-radius: 8px;
  overflow: hidden;
}

.my-custom-table :deep(th) {
  background-color: #f0f4f8 !important;
  color: #133665 !important;
  font-weight: 600 !important;
}

.my-custom-table :deep(td) {
  background-color: #ffffff !important;
  color: #333333 !important;
}

.my-custom-table :deep(tr) {
  background-color: #ffffff !important;
}

.q-card {
  transition: all 0.3s ease;
  background-color: #ffffff !important;
}
</style>
