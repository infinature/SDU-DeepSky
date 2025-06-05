<template>
  <div class="timeline-bg">
    <div class="timeline-container single">
      <div class="timeline-content">
        <div class="timeline-card timeline-detail-card">
          <q-btn flat color="deep-purple-6" icon="arrow_back" label="返回导航页" class="q-mb-lg nav-btn" @click="returnToNavigationPortal" />
          <div class="timeline-title text-h4 q-mb-md">J-PLUS 数据集</div>
          <div class="timeline-desc q-mb-xl">J-PLUS 项目提供多波段成像数据，适合恒星、星系等天体的多色测光分析。</div>
          <div class="row q-col-gutter-xl responsive-row">
            <!-- 左侧表单区 -->
            <div class="col-12 col-md-4">
              <q-card class="option-card q-pa-xl">
                <q-card-section class="q-pa-none">
                  <div class="form-section-title">目标上传</div>
                  <q-separator spaced color="deep-purple-2" />
                  <div class="form-center-wrap">
                    <q-card class="upload-card q-mb-xl q-mt-md">
                      <q-card-section>
                        <div class="text-body2 q-mb-md">
                          上传包含 <b>TILE_ID, FILTER_ID, RA, DEC</b> 列的 CSV 文件。
                        </div>
                        <q-file
                          v-model="csvFile"
                          label="选择目标列表 CSV 文件"
                          accept=".csv"
                          class="q-mb-md"
                          @update:model-value="onFileSelected"
                          clearable
                          outlined
                          color="deep-purple-5"
                        >
                          <template v-slot:prepend>
                            <q-icon name="attach_file" />
                          </template>
                          <template v-slot:append>
                            <q-icon name="close" @click.stop="clearCsvFile" class="cursor-pointer" />
                          </template>
                        </q-file>
                        <div v-if="uploadStatus" class="text-caption q-mb-md" :class="uploadStatus.color">
                          {{ uploadStatus.message }}
                        </div>
                      </q-card-section>
                    </q-card>
                  </div>
                  <div class="form-section-title q-mt-xl">参数设置</div>
                  <q-separator spaced color="deep-purple-2" />
                  <div class="form-center-wrap">
                    <q-form @submit="onSubmit" class="q-gutter-lg q-mt-lg">
                      <div class="row q-col-gutter-xl q-mb-lg">
                        <div class="col-12 col-md-6">
                          <q-select
                            v-model="form.dataType"
                            :options="dataTypeOptions"
                            label="数据类型"
                            :rules="[val => !!val || '请选择数据类型']"
                            outlined
                            color="deep-purple-5"
                          >
                            <template v-slot:option="scope">
                              <q-item v-bind="scope.itemProps">
                                <q-item-section>
                                  <q-item-label>{{ scope.opt.label }}</q-item-label>
                                  <q-item-label caption>
                                    {{ getDataTypeDescription(scope.opt.value) }}
                                  </q-item-label>
                                </q-item-section>
                              </q-item>
                            </template>
                          </q-select>
                        </div>
                        <div class="col-12 col-md-6">
                          <q-input
                            v-model="form.saveDir"
                            label="保存目录"
                            :rules="[val => !!val || '请输入保存目录']"
                            outlined
                            color="deep-purple-5"
                          >
                            <template v-slot:append>
                              <q-icon name="folder" class="cursor-pointer" @click="openFilesPage">
                                <q-tooltip>选择目录</q-tooltip>
                              </q-icon>
                            </template>
                          </q-input>
                        </div>
                      </div>
                      <div v-if="form.dataType === 'cutout' || form.dataType === 'graphic_cutout'" class="row q-col-gutter-xl q-mb-lg">
                        <div class="col-12 col-md-6">
                          <q-input
                            v-model.number="form.width"
                            label="宽度 (度)"
                            type="number"
                            :rules="[
                              val => !!val || '请输入宽度',
                              val => val > 0 || '宽度必须大于0'
                            ]"
                            outlined
                            color="deep-purple-5"
                          />
                        </div>
                        <div class="col-12 col-md-6">
                          <q-input
                            v-model.number="form.height"
                            label="高度 (度)"
                            type="number"
                            :rules="[
                              val => !!val || '请输入高度',
                              val => val > 0 || '高度必须大于0'
                            ]"
                            outlined
                            color="deep-purple-5"
                          />
                        </div>
                      </div>
                      <q-separator spaced color="deep-purple-2" />
                      <div class="row justify-center q-mt-xl">
                        <q-btn
                          type="submit"
                          color="deep-purple-6"
                          label="开始下载"
                          :loading="loading"
                          :disable="!hasTargets"
                          class="download-btn"
                          unelevated
                          rounded
                          size="lg"
                          icon="cloud_download"
                        />
                      </div>
                    </q-form>
                  </div>
                </q-card-section>
              </q-card>
            </div>
            <!-- 右侧历史区 -->
            <div class="col-12 col-md-8">
              <q-card class="history-card q-pa-xl">
                <q-card-section>
                  <div class="text-h6 q-mb-md">下载历史</div>
                  <q-table
                    :rows="downloadHistory"
                    :columns="historyColumns"
                    row-key="id"
                    :pagination="{ rowsPerPage: 5 }"
                    flat
                    bordered
                    class="history-table"
                  >
                    <template v-slot:body-cell-status="props">
                      <q-td :props="props">
                        <q-chip
                          :color="getStatusColor(props.row.status)"
                          text-color="white"
                          dense
                        >
                          {{ props.row.status }}
                        </q-chip>
                      </q-td>
                    </template>
                    <template v-slot:body-cell-progress="props">
                      <q-td :props="props">
                        <q-linear-progress
                          :value="props.row.progress / 100"
                          :color="getStatusColor(props.row.status)"
                          size="20px"
                          rounded
                        >
                          <div class="absolute-full flex flex-center">
                            <q-badge color="white" text-color="black">
                              {{ props.row.progress }}%
                            </q-badge>
                          </div>
                        </q-linear-progress>
                      </q-td>
                    </template>
                  </q-table>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'JPlusPage',

  setup () {
    const $q = useQuasar()
    const router = useRouter()
    const loading = ref(false)
    const csvFile = ref(null)
    const targets = ref([])
    const downloadHistory = ref([])
    const uploadStatus = ref(null)
    const currentTaskId = ref(null)
    const statusCheckInterval = ref(null)

    const form = ref({
      dataType: 'fits',
      saveDir: 'jplus_downloads',
      width: 0.1,
      height: 0.1
    })

    const dataTypeOptions = [
      { label: 'FITS 图像', value: 'fits' },
      { label: '权重图', value: 'weight' },
      { label: 'FITS 切图', value: 'cutout' },
      { label: 'PSF 文件', value: 'psf' },
      { label: '位置 PSF', value: 'psf_position' },
      { label: '预览图', value: 'graphic' },
      { label: '预览图切图', value: 'graphic_cutout' }
    ]

    const historyColumns = [
      { name: 'id', label: 'ID', field: 'id', align: 'left' },
      { name: 'timestamp', label: '时间', field: 'timestamp', align: 'left' },
      { name: 'dataType', label: '数据类型', field: 'dataType', align: 'left' },
      { name: 'status', label: '状态', field: 'status', align: 'left' },
      { name: 'progress', label: '进度', field: 'progress', align: 'left' }
    ]

    const hasTargets = computed(() => targets.value.length > 0)

    const getStatusColor = (status) => {
      switch (status) {
        case 'completed': return 'positive'
        case 'failed': return 'negative'
        case 'running': return 'warning'
        default: return 'grey'
      }
    }

    const getDataTypeDescription = (type) => {
      const descriptions = {
        'fits': '下载完整的 FITS 科学图像',
        'weight': '下载 FITS 图像对应的权重图',
        'cutout': '下载指定位置的 FITS 图像切图',
        'psf': '下载点延展函数 (PSF) 文件',
        'psf_position': '下载指定位置的 PSF 模型文件',
        'graphic': '下载 RGB 预览图',
        'graphic_cutout': '下载指定位置的 RGB 预览图切图'
      }
      return descriptions[type] || ''
    }

    const clearCsvFile = () => {
      csvFile.value = null
      uploadStatus.value = null
      targets.value = []
    }

    const onFileSelected = async (file) => {
      if (file) {
        try {
          uploadStatus.value = { color: 'text-grey', message: '正在解析 CSV 文件...' }
          const text = await file.text()
          const rows = text.split('\n')
          const headers = rows[0].toLowerCase().split(',').map(h => h.trim().replace(/"/g, ''))

          // 验证必需的列
          const requiredColumns = ['tile_id', 'filter_id']
          const missingColumns = requiredColumns.filter(col => !headers.includes(col))
          if (missingColumns.length > 0) {
            throw new Error(`CSV 文件缺少必需的列: ${missingColumns.join(', ')}`)
          }

          // 获取列索引
          const tileIdIndex = headers.indexOf('tile_id')
          const filterIdIndex = headers.indexOf('filter_id')
          const raIndex = headers.indexOf('ra')
          const decIndex = headers.indexOf('dec')

          // 解析数据行
          const newTargets = []
          for (let i = 1; i < rows.length; i++) {
            if (!rows[i].trim()) continue // 跳过空行

            const values = rows[i].split(',').map(v => v.trim().replace(/"/g, ''))
            if (values.length < headers.length) continue // 跳过格式不正确的行

            const tileId = values[tileIdIndex]
            const filterId = values[filterIdIndex]
            const ra = raIndex >= 0 ? parseFloat(values[raIndex]) : null
            const dec = decIndex >= 0 ? parseFloat(values[decIndex]) : null

            if (!tileId || !filterId) {
              console.warn(`跳过第 ${i + 1} 行: 缺少必需的字段`)
              continue
            }

            newTargets.push({ tileId, filterId, ra, dec })
          }

          if (newTargets.length === 0) {
            throw new Error('CSV 文件中没有有效的目标数据')
          }

          // 添加新目标
          targets.value = newTargets

          uploadStatus.value = {
            color: 'text-positive',
            message: `成功导入 ${newTargets.length} 个目标`
          }
        } catch (error) {
          uploadStatus.value = {
            color: 'text-negative',
            message: `CSV 文件解析错误: ${error.message}`
          }
        }
      } else {
        uploadStatus.value = null
      }
    }

    const checkTaskStatus = async (taskId) => {
      try {
        const response = await fetch(`http://localhost:5003/api/status/${taskId}`)
        const data = await response.json()

        // 更新下载历史中的状态
        const historyItem = downloadHistory.value.find(h => h.id === taskId)
        if (historyItem) {
          historyItem.status = data.status
          if (data.progress) {
            historyItem.progress = data.progress
          }
          if (data.error) {
            historyItem.error = data.error
          }
        }

        // 如果任务完成或失败，停止检查
        if (data.status === 'completed' || data.status === 'failed') {
          if (statusCheckInterval.value) {
            clearInterval(statusCheckInterval.value)
            statusCheckInterval.value = null
          }

          // 显示完成或错误消息
          if (data.status === 'completed') {
            $q.notify({
              color: 'positive',
              message: '下载完成'
            })
          } else {
            $q.notify({
              color: 'negative',
              message: `下载失败: ${data.error || '未知错误'}`
            })
          }
        }
      } catch (error) {
        console.error('检查任务状态失败:', error)
      }
    }

    const startStatusCheck = () => {
      if (statusCheckInterval.value) {
        clearInterval(statusCheckInterval.value)
      }
      statusCheckInterval.value = setInterval(() => {
        if (currentTaskId.value) {
          checkTaskStatus(currentTaskId.value)
        }
      }, 2000) // 每2秒检查一次
    }

    const onSubmit = async () => {
      if (!hasTargets.value) {
        $q.notify({
          color: 'negative',
          message: '请上传包含目标的 CSV 文件'
        })
        return
      }

      try {
        loading.value = true
        const response = await fetch('http://localhost:5003/api/jplus/download', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            targets: targets.value,
            dataType: form.value.dataType.value || form.value.dataType,
            saveDir: form.value.saveDir,
            width: form.value.width,
            height: form.value.height
          })
        })

        const data = await response.json()
        if (data.status === 'success') {
          currentTaskId.value = data.task_id
          downloadHistory.value.unshift({
            id: data.task_id,
            timestamp: new Date().toLocaleString(),
            dataType: form.value.dataType.label || form.value.dataType,
            status: 'running',
            progress: 0
          })
          startStatusCheck()
        } else {
          throw new Error(data.message)
        }
      } catch (error) {
        $q.notify({
          color: 'negative',
          message: `下载失败: ${error.message}`,
          icon: 'error'
        })
      } finally {
        loading.value = false
      }
    }

    const openFilesPage = () => {
      router.push('/files')
    }

    const returnToNavigationPortal = () => {
      window.location.href = 'http://localhost:8000/';
    }

    // 组件卸载时清理定时器
    onUnmounted(() => {
      if (statusCheckInterval.value) {
        clearInterval(statusCheckInterval.value)
      }
    })

    return {
      form,
      loading,
      csvFile,
      targets,
      dataTypeOptions,
      historyColumns,
      downloadHistory,
      hasTargets,
      getStatusColor,
      onFileSelected,
      onSubmit,
      clearCsvFile,
      uploadStatus,
      getDataTypeDescription,
      openFilesPage,
      returnToNavigationPortal
    }
  }
})
</script>

<style scoped>
.timeline-bg {
  min-height: 100vh;
  background: linear-gradient(120deg, #e0e7ff 0%, #ede9fe 100%);
  padding-top: 32px;
}
.timeline-container.single {
  display: flex;
  flex-direction: row;
  max-width: 96vw;
  margin: 32px auto;
  position: relative;
  padding: 16px 0;
}
.timeline-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 48px;
  margin-left: 0;
}
.timeline-card.timeline-detail-card {
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 4px 32px rgba(120, 87, 255, 0.12);
  padding: 48px 56px 40px 56px;
  margin-bottom: 20px;
  position: relative;
  transition: box-shadow 0.2s, transform 0.2s;
}
.timeline-card.timeline-detail-card:hover {
  box-shadow: 0 8px 48px rgba(120, 87, 255, 0.18);
  transform: translateY(-4px) scale(1.01);
}
.timeline-title {
  font-size: 2.2rem;
  font-weight: bold;
  margin-bottom: 18px;
  color: #5b21b6;
  letter-spacing: 1px;
}
.timeline-desc {
  color: #444;
  font-size: 1.15rem;
  margin-bottom: 28px;
  line-height: 1.7;
}
.upload-card, .option-card, .history-card {
  border-radius: 16px;
  box-shadow: 0 2px 16px rgba(120, 87, 255, 0.08);
  border: none;
}
.download-btn {
  font-size: 1.15rem;
  font-weight: bold;
  border-radius: 12px;
  padding: 0 32px;
  min-width: 160px;
  letter-spacing: 1px;
}
.nav-btn {
  font-size: 1.1rem;
  font-weight: bold;
  border-radius: 10px;
  padding: 0 20px;
  min-width: 120px;
  letter-spacing: 1px;
}
.history-table {
  border-radius: 12px;
  overflow: hidden;
  font-size: 1.05rem;
}
.q-table th {
  background: #ede9fe;
  color: #5b21b6;
  font-weight: bold;
  font-size: 1.08rem;
}
.q-table td {
  font-size: 1.05rem;
}
.form-section-title {
  font-size: 1.18rem;
  font-weight: bold;
  color: #7c3aed;
  margin-bottom: 8px;
  margin-top: 8px;
  letter-spacing: 1px;
}
.form-center-wrap {
  max-width: 520px;
  margin: 0 auto;
}
@media (max-width: 1024px) {
  .timeline-card.timeline-detail-card {
    padding: 24px 8px 24px 8px;
  }
  .timeline-container.single {
    max-width: 98vw;
    padding: 0;
  }
}
@media (max-width: 768px) {
  .responsive-row {
    flex-direction: column !important;
  }
  .timeline-card.timeline-detail-card {
    padding: 12px 2vw 12px 2vw;
  }
  .option-card, .history-card {
    padding: 16px 4px !important;
  }
}
</style>