<template>
  <div class="timeline-bg">
    <div class="timeline-container single">
      <div class="timeline-content">
        <div class="timeline-card timeline-detail-card">
          <q-btn flat color="deep-purple-6" icon="arrow_back" label="返回导航页" class="q-mb-lg nav-btn" @click="returnToNavigationPortal" />
          <div class="timeline-title text-h4 q-mb-md">DESI 数据集</div>
          <div class="timeline-desc q-mb-xl">DESI（暗能量光谱仪）项目的数据集，包含丰富的光谱观测数据，适用于宇宙学和星系研究。</div>
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
                          上传包含 <b>RA, DEC, TARGET_ID(可选)</b> 列的 CSV 文件。
                        </div>
                        <q-file
                          v-model="csvFile"
                          label="选择目标列表 CSV 文件"
                          accept=".csv"
                          class="q-mb-md"
                          @update:model-value="handleFileUpload"
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
                    <div v-if="!csvFile" class="row q-col-gutter-xl q-mb-lg">
                      <div class="col-12 col-md-6">
                        <q-input
                          v-model="form.ra"
                          label="赤经 (度)"
                          type="number"
                          :rules="[val => !!val || '请输入赤经']"
                          outlined
                          color="deep-purple-5"
                        />
                      </div>
                      <div class="col-12 col-md-6">
                        <q-input
                          v-model="form.dec"
                          label="赤纬 (度)"
                          type="number"
                          :rules="[val => !!val || '请输入赤纬']"
                          outlined
                          color="deep-purple-5"
                        />
                      </div>
                    </div>
                  </div>
                  <div class="form-section-title q-mt-xl">参数设置</div>
                  <q-separator spaced color="deep-purple-2" />
                  <div class="form-center-wrap">
                    <q-form @submit="onSubmit" class="q-gutter-lg">
                      <div class="row q-col-gutter-xl q-mt-lg q-mb-lg">
                        <div class="col-12 col-md-6">
                          <q-input
                            v-model="form.size"
                            label="图像大小 (像素)"
                            type="number"
                            :rules="[val => !!val || '请输入图像大小']"
                            hint="FITS 最大512，JPEG最大3000"
                            outlined
                            color="deep-purple-5"
                          />
                        </div>
                        <div class="col-12 col-md-6">
                          <q-input
                            v-model="form.pixscale"
                            label="像元比例 (角秒/像素)"
                            type="number"
                            :rules="[val => !!val || '请输入像元比例']"
                            hint="默认：0.262"
                            outlined
                            color="deep-purple-5"
                          />
                        </div>
                      </div>
                      <div class="row q-col-gutter-xl q-mb-lg">
                        <div class="col-12 col-md-6">
                          <q-select
                            v-model="form.bands"
                            :options="bandOptions"
                            label="波段"
                            multiple
                            use-chips
                            :rules="[val => val.length > 0 || '请至少选择一个波段']"
                            :disable="form.format.value === 'jpeg'"
                            outlined
                            color="deep-purple-5"
                          />
                        </div>
                        <div class="col-12 col-md-6">
                          <q-select
                            v-model="form.format"
                            :options="formatOptions"
                            label="图像格式"
                            :rules="[val => !!val || '请选择格式']"
                            outlined
                            color="deep-purple-5"
                          />
                        </div>
                      </div>
                      <div v-if="form.format.value === 'fits'" class="row q-col-gutter-xl q-mb-lg">
                        <div class="col-12 col-md-6">
                          <q-checkbox
                            v-model="form.createRGB"
                            label="生成RGB图像"
                            color="deep-purple-6"
                          />
                        </div>
                        <div v-if="form.createRGB" class="col-12">
                          <q-card flat bordered class="q-mt-md">
                            <q-card-section>
                              <div class="text-subtitle2 q-mb-md">RGB 参数</div>
                              <div class="row q-col-gutter-xl">
                                <div class="col-12 col-md-4">
                                  <q-input
                                    v-model="form.luptonMinimum"
                                    label="最小值"
                                    type="number"
                                    step="0.01"
                                    hint="默认：0.01"
                                    outlined
                                    color="deep-purple-5"
                                  />
                                </div>
                                <div class="col-12 col-md-4">
                                  <q-input
                                    v-model="form.luptonStretch"
                                    label="拉伸"
                                    type="number"
                                    step="0.01"
                                    hint="默认：0.1"
                                    outlined
                                    color="deep-purple-5"
                                  />
                                </div>
                                <div class="col-12 col-md-4">
                                  <q-input
                                    v-model="form.luptonQ"
                                    label="Q"
                                    type="number"
                                    step="0.1"
                                    hint="默认：1.0"
                                    outlined
                                    color="deep-purple-5"
                                  />
                                </div>
                              </div>
                              <div class="row q-mt-sm">
                                <div class="col-12">
                                  <q-checkbox
                                    v-model="form.performBgSubtraction"
                                    label="执行背景扣除"
                                    color="deep-purple-6"
                                  />
                                </div>
                              </div>
                            </q-card-section>
                          </q-card>
                        </div>
                      </div>
                    </q-form>
                  </div>
                  <div class="form-section-title q-mt-xl">保存设置</div>
                  <q-separator spaced color="deep-purple-2" />
                  <div class="form-center-wrap">
                    <div class="row q-col-gutter-xl q-mt-lg q-mb-lg">
                      <div class="col-12">
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
                    <q-separator spaced color="deep-purple-2" />
                    <div class="row justify-center q-mt-xl">
                      <q-btn
                        @click="onSubmit"
                        color="deep-purple-6"
                        label="开始下载"
                        :loading="loading"
                        class="download-btn"
                        unelevated
                        rounded
                        size="lg"
                        icon="cloud_download"
                      />
                    </div>
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
                    :columns="columns"
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
import { defineComponent, ref, watch, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'DESIPage',

  setup () {
    const $q = useQuasar()
    const router = useRouter()
    const loading = ref(false)
    const downloadHistory = ref([])
    const csvFile = ref(null)
    const csvData = ref([])
    const currentTaskId = ref(null)
    const statusCheckInterval = ref(null)
    const uploadStatus = ref(null)

    const form = ref({
      ra: null,
      dec: null,
      size: 128,
      pixscale: 0.262,
      bands: ['g', 'r', 'z'],
      format: { label: 'FITS', value: 'fits' },
      saveDir: 'desi_downloads',
      createRGB: true,
      luptonMinimum: 0.01,
      luptonStretch: 0.1,
      luptonQ: 1.0,
      performBgSubtraction: false
    })

    const bandOptions = ['g', 'r', 'z']
    const formatOptions = [
      { label: 'FITS', value: 'fits' },
      { label: 'JPEG', value: 'jpeg' }
    ]

    // Watch format changes to update bands
    watch(() => form.value.format, (newFormat) => {
      if (newFormat.value === 'jpeg') {
        form.value.bands = ['g'] // JPEG only supports single band
        form.value.createRGB = false // 禁用 RGB 选项
      } else if (newFormat.value === 'fits') {
        form.value.bands = ['g', 'r', 'z'] // Reset to default for FITS
        form.value.createRGB = true // 启用 RGB 选项
      }
    }, { immediate: true })

    const columns = [
      { name: 'id', label: 'ID', field: 'id', align: 'left' },
      { name: 'timestamp', label: 'Time', field: 'timestamp', align: 'left' },
      { name: 'coordinates', label: 'Coordinates', field: 'coordinates', align: 'left' },
      { name: 'bands', label: 'Bands', field: 'bands', align: 'left' },
      { name: 'format', label: 'Format', field: 'format', align: 'left' },
      { name: 'progress', label: 'Progress', field: 'progress', align: 'left' },
      { name: 'status', label: 'Status', field: 'status', align: 'left' }
    ]

    const getStatusColor = (status) => {
      switch (status) {
        case 'completed': return 'positive'
        case 'failed': return 'negative'
        case 'running': return 'warning'
        default: return 'grey'
      }
    }

    const clearCsvFile = () => {
      csvFile.value = null
      uploadStatus.value = null
      csvData.value = []
    }

    const handleFileUpload = async (file) => {
      if (!file) {
        clearCsvFile()
        return
      }

      try {
        uploadStatus.value = { color: 'text-grey', message: 'Parsing CSV file...' }
        const text = await file.text()
        const rows = text.split('\n')
        const headers = rows[0].toLowerCase().split(',').map(h => h.trim())

        // 验证必需的列
        const requiredColumns = ['ra', 'dec']
        const missingColumns = requiredColumns.filter(col => !headers.includes(col))
        if (missingColumns.length > 0) {
          throw new Error(`CSV file is missing required columns: ${missingColumns.join(', ')}`)
        }

        // 获取列索引
        const raIndex = headers.indexOf('ra')
        const decIndex = headers.indexOf('dec')
        const targetIdIndex = headers.indexOf('target_id')

        // 解析数据行
        const newTargets = []
        for (let i = 1; i < rows.length; i++) {
          if (!rows[i].trim()) continue // 跳过空行

          const values = rows[i].split(',').map(v => v.trim())
          if (values.length < headers.length) continue // 跳过格式不正确的行

          const ra = parseFloat(values[raIndex])
          const dec = parseFloat(values[decIndex])
          const targetId = targetIdIndex >= 0 ? values[targetIdIndex] : `${ra}_${dec}`

          if (isNaN(ra) || isNaN(dec)) {
            console.warn(`Skipping row ${i + 1}: Invalid coordinates`)
            continue
          }

          newTargets.push({ ra, dec, targetId })
        }

        if (newTargets.length === 0) {
          throw new Error('No valid targets found in CSV file')
        }

        // 更新数据
        csvData.value = newTargets

        uploadStatus.value = {
          color: 'text-positive',
          message: `Successfully imported ${newTargets.length} targets`
        }
      } catch (error) {
        uploadStatus.value = {
          color: 'text-negative',
          message: `CSV file parsing error: ${error.message}`
        }
        csvData.value = []
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
              message: 'Download completed successfully'
            })
          } else {
            $q.notify({
              color: 'negative',
              message: `Download failed: ${data.error || 'Unknown error'}`
            })
          }
        }
      } catch (error) {
        console.error('Error checking task status:', error)
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
      }, 2000) // Check every 2 seconds
    }

    const onSubmit = async () => {
      try {
        loading.value = true

        // Validate size limits
        if (form.value.format.value === 'fits' && form.value.size > 512) {
          throw new Error('FITS format maximum size is 512 pixels')
        } else if (form.value.format.value === 'jpeg' && form.value.size > 3000) {
          throw new Error('JPEG format maximum size is 3000 pixels')
        }

        // Prepare request data
        const requestData = {
          size: form.value.size,
          pixscale: form.value.pixscale,
          bands: form.value.bands,
          format: form.value.format.value || form.value.format.value,
          saveDir: form.value.saveDir,
          createRGB: form.value.createRGB,
          luptonMinimum: form.value.luptonMinimum,
          luptonStretch: form.value.luptonStretch,
          luptonQ: form.value.luptonQ,
          performBgSubtraction: form.value.performBgSubtraction
        }

        // Add targets from CSV or manual input
        if (csvFile.value) {
          requestData.targets = csvData.value.map(row => ({
            ra: parseFloat(row.ra),
            dec: parseFloat(row.dec),
            targetId: row.targetId || `${row.ra}_${row.dec}`
          }))
        } else {
          requestData.targets = [{
            ra: parseFloat(form.value.ra),
            dec: parseFloat(form.value.dec),
            targetId: `${form.value.ra}_${form.value.dec}`
          }]
        }

        const response = await fetch('http://localhost:5003/api/desi/download', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        })

        const data = await response.json()
        if (data.status === 'success') {
          currentTaskId.value = data.task_id

          // Add to history
          downloadHistory.value.unshift({
            id: data.task_id,
            timestamp: new Date().toLocaleString(),
            coordinates: csvFile.value ? `${requestData.targets.length} targets` : `${form.value.ra}, ${form.value.dec}`,
            bands: form.value.bands.join(', '),
            format: form.value.format.value || form.value.format.value,
            status: 'running',
            progress: 0
          })

          // Start status check
          startStatusCheck()

          $q.notify({
            color: 'positive',
            message: 'Download started successfully'
          })
        } else {
          throw new Error(data.message)
        }
      } catch (error) {
        $q.notify({
          color: 'negative',
          message: `Error: ${error.message}`
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

    // Clean up interval when component is unmounted
    onUnmounted(() => {
      if (statusCheckInterval.value) {
        clearInterval(statusCheckInterval.value)
      }
    })

    return {
      form,
      loading,
      bandOptions,
      formatOptions,
      columns,
      downloadHistory,
      getStatusColor,
      onSubmit,
      csvFile,
      handleFileUpload,
      openFilesPage,
      uploadStatus,
      clearCsvFile,
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
