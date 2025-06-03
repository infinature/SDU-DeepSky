<template>
  <div class="timeline-bg">
    <div class="timeline-container single">
      <div class="timeline-content">
        <div class="timeline-card timeline-detail-card">
          <q-btn flat color="primary" icon="arrow_back" label="返回导航页" class="q-mb-md" @click="returnToNavigationPortal" />
          <div class="timeline-title text-h5 q-mb-md">DESI 数据集</div>
          <div class="timeline-desc q-mb-lg">DESI（暗能量光谱仪）项目的数据集，包含丰富的光谱观测数据，适用于宇宙学和星系研究。</div>
          <!-- Download Options -->
          <q-card class="q-mb-md">
            <q-card-section>
              <div class="text-h6">Download Options</div>
              <q-form @submit="onSubmit" class="q-gutter-md">
                <!-- CSV Upload -->
                <q-card class="q-mb-md">
                  <q-card-section>
                    <div class="text-h6">Target List</div>
                    <div class="text-body2 q-mb-md">
                      Upload a CSV file with the following columns:
                      RA, DEC, TARGET_ID (optional)
                    </div>

                    <q-file
                      v-model="csvFile"
                      label="Target List CSV"
                      accept=".csv"
                      class="q-mb-md"
                      @update:model-value="handleFileUpload"
                      clearable
                    >
                      <template v-slot:prepend>
                        <q-icon name="attach_file" />
                      </template>
                      <template v-slot:append>
                        <q-icon name="close" @click.stop="clearCsvFile" class="cursor-pointer" />
                      </template>
                    </q-file>

                    <!-- Upload Status -->
                    <div v-if="uploadStatus" class="text-caption q-mb-md" :class="uploadStatus.color">
                      {{ uploadStatus.message }}
                    </div>
                  </q-card-section>
                </q-card>

                <!-- Manual Input (only show if no CSV file) -->
                <div v-if="!csvFile" class="row q-col-gutter-md">
                  <div class="col-12 col-md-6">
                    <q-input
                      v-model="form.ra"
                      label="Right Ascension (degrees)"
                      type="number"
                      :rules="[val => !!val || 'RA is required']"
                    />
                  </div>
                  <div class="col-12 col-md-6">
                    <q-input
                      v-model="form.dec"
                      label="Declination (degrees)"
                      type="number"
                      :rules="[val => !!val || 'Dec is required']"
                    />
                  </div>
                </div>

                <!-- Size -->
                <div class="row q-col-gutter-md">
                  <div class="col-12 col-md-6">
                    <q-input
                      v-model="form.size"
                      label="Size (pixels)"
                      type="number"
                      :rules="[val => !!val || 'Size is required']"
                      hint="Max 512 for FITS, 3000 for JPEG"
                    />
                  </div>
                  <div class="col-12 col-md-6">
                    <q-input
                      v-model="form.pixscale"
                      label="Pixel Scale (arcsec/pixel)"
                      type="number"
                      :rules="[val => !!val || 'Pixel scale is required']"
                      hint="Default: 0.262"
                    />
                  </div>
                </div>

                <!-- Bands and Format -->
                <div class="row q-col-gutter-md">
                  <div class="col-12 col-md-6">
                    <q-select
                      v-model="form.bands"
                      :options="bandOptions"
                      label="Bands"
                      multiple
                      use-chips
                      :rules="[val => val.length > 0 || 'At least one band is required']"
                      :disable="form.format.value === 'jpeg'"
                    />
                  </div>
                  <div class="col-12 col-md-6">
                    <q-select
                      v-model="form.format"
                      :options="formatOptions"
                      label="Image Format"
                      :rules="[val => !!val || 'Format is required']"
                    />
                  </div>
                </div>

                <!-- RGB Options (only for FITS) -->
                <div v-if="form.format.value === 'fits'" class="row q-col-gutter-md">
                  <div class="col-12 col-md-6">
                    <q-checkbox
                      v-model="form.createRGB"
                      label="Create RGB Image"
                    />
                  </div>
                  <div v-if="form.createRGB" class="col-12">
                    <q-card flat bordered>
                      <q-card-section>
                        <div class="text-subtitle2">RGB Parameters</div>
                        <div class="row q-col-gutter-md">
                          <div class="col-12 col-md-4">
                            <q-input
                              v-model="form.luptonMinimum"
                              label="Minimum"
                              type="number"
                              step="0.01"
                              hint="Default: 0.01"
                            />
                          </div>
                          <div class="col-12 col-md-4">
                            <q-input
                              v-model="form.luptonStretch"
                              label="Stretch"
                              type="number"
                              step="0.01"
                              hint="Default: 0.1"
                            />
                          </div>
                          <div class="col-12 col-md-4">
                            <q-input
                              v-model="form.luptonQ"
                              label="Q"
                              type="number"
                              step="0.1"
                              hint="Default: 1.0"
                            />
                          </div>
                        </div>
                        <div class="row q-mt-sm">
                          <div class="col-12">
                            <q-checkbox
                              v-model="form.performBgSubtraction"
                              label="Perform Background Subtraction"
                            />
                          </div>
                        </div>
                      </q-card-section>
                    </q-card>
                  </div>
                </div>

                <!-- Save Directory -->
                <div class="row q-col-gutter-md">
                  <div class="col-12">
                    <q-input
                      v-model="form.saveDir"
                      label="Save Directory"
                      :rules="[val => !!val || 'Save directory is required']"
                    >
                      <template v-slot:append>
                        <q-icon name="folder" class="cursor-pointer" @click="openFilesPage">
                          <q-tooltip>Select Directory</q-tooltip>
                        </q-icon>
                      </template>
                    </q-input>
                  </div>
                </div>

                <!-- Submit Button -->
                <div class="row justify-end">
                  <q-btn
                    type="submit"
                    color="primary"
                    label="Download"
                    :loading="loading"
                  />
                </div>
              </q-form>
            </q-card-section>
          </q-card>

          <!-- Download History -->
          <q-card>
            <q-card-section>
              <div class="text-h6">Download History</div>
              <q-table
                :rows="downloadHistory"
                :columns="columns"
                row-key="id"
                :pagination="{ rowsPerPage: 5 }"
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
    };

    const goHome = () => {
      router.push('/')
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
      goHome,
      returnToNavigationPortal
    }
  }
})
</script>

<style scoped>
.timeline-bg {
  min-height: 100vh;
  background: #0a0a23;
  padding-top: 60px;
}
.timeline-container.single {
  display: flex;
  flex-direction: row;
  max-width: 900px;
  margin: 0 auto;
  position: relative;
}
.timeline-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 40px;
  margin-left: 0;
}
.timeline-card.timeline-detail-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 16px rgba(160, 132, 232, 0.08);
  padding: 32px 40px;
  margin-bottom: 20px;
  position: relative;
}
.timeline-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 10px;
}
.timeline-desc {
  color: #333;
  font-size: 1rem;
  margin-bottom: 18px;
}
</style>
