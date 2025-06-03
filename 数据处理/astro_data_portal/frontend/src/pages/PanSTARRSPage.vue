<template>
  <div class="timeline-bg">
    <div class="timeline-container single">
      <div class="timeline-content">
        <div class="timeline-card timeline-detail-card">
          <q-btn flat color="deep-purple-6" icon="arrow_back" label="返回导航页" class="q-mb-lg nav-btn" @click="returnToNavigationPortal" />
          <div class="timeline-title text-h4 q-mb-md">Pan-STARRS 数据集</div>
          <div class="timeline-desc q-mb-xl">Pan-STARRS 拥有大面积的深度巡天数据，广泛应用于变星、超新星等领域。</div>
          <div class="row q-col-gutter-xl responsive-row">
            <!-- 左侧表单区 -->
            <div class="col-12 col-md-4">
              <q-card class="option-card q-pa-xl">
                <q-card-section class="q-pa-none">
                  <div class="form-section-title">目标上传</div>
                  <q-separator spaced color="deep-purple-2" />
                  <q-card class="upload-card q-mb-xl q-mt-md">
                    <q-card-section>
                      <div class="text-body2 q-mb-md">
                        上传包含 <b>ID, RA, DEC</b> 列的 CSV 文件，或手动输入目标。
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
                      <div class="text-subtitle2 q-mb-sm">或手动输入目标坐标：</div>
                      <div class="row q-col-gutter-xl">
                        <div class="col-12 col-md-4">
                          <q-input
                            v-model="manualEntry.id"
                            label="目标 ID"
                            :rules="manualEntryRules.id"
                            :error="manualEntryErrors.id"
                            @update:model-value="clearManualEntryError('id')"
                            outlined
                            color="deep-purple-5"
                          />
                        </div>
                        <div class="col-12 col-md-4">
                          <q-input
                            v-model="manualEntry.ra"
                            label="赤经 (度)"
                            type="number"
                            :rules="manualEntryRules.ra"
                            :error="manualEntryErrors.ra"
                            @update:model-value="clearManualEntryError('ra')"
                            outlined
                            color="deep-purple-5"
                          />
                        </div>
                        <div class="col-12 col-md-4">
                          <q-input
                            v-model="manualEntry.dec"
                            label="赤纬 (度)"
                            type="number"
                            :rules="manualEntryRules.dec"
                            :error="manualEntryErrors.dec"
                            @update:model-value="clearManualEntryError('dec')"
                            outlined
                            color="deep-purple-5"
                          />
                        </div>
                      </div>
                      <div class="row justify-end q-mt-md">
                        <q-btn
                          color="deep-purple-6"
                          label="添加目标"
                          @click="addManualTarget"
                          :disable="!isManualEntryValid"
                          class="download-btn"
                          unelevated
                          rounded
                          size="md"
                          icon="add_circle"
                        />
                      </div>
                    </q-card-section>
                  </q-card>
                  <div class="form-section-title q-mt-xl">参数设置</div>
                  <q-separator spaced color="deep-purple-2" />
                  <div class="form-center-wrap">
                    <q-form @submit="onSubmit" class="q-gutter-lg q-mt-lg">
                      <div class="row q-col-gutter-xl q-mb-lg">
                        <div class="col-12 col-md-6">
                          <q-select
                            v-model="form.bands"
                            :options="bandOptions"
                            label="波段"
                            multiple
                            use-chips
                            :rules="[val => val.length > 0 || '请至少选择一个波段']"
                            outlined
                            color="deep-purple-5"
                          >
                            <template v-slot:option="scope">
                              <q-item v-bind="scope.itemProps">
                                <q-item-section>
                                  <q-item-label>{{ scope.opt.label }}</q-item-label>
                                  <q-item-label caption>
                                    {{ getBandDescription(scope.opt.value) }}
                                  </q-item-label>
                                </q-item-section>
                              </q-item>
                            </template>
                          </q-select>
                        </div>
                        <div class="col-12 col-md-6">
                          <q-input
                            v-model.number="form.size"
                            label="图像大小 (像素)"
                            type="number"
                            :rules="[
                              val => !!val || '请输入图像大小',
                              val => val >= 100 || '图像大小不能小于 100 像素',
                              val => val <= 1000 || '图像大小不能大于 1000 像素'
                            ]"
                            outlined
                            color="deep-purple-5"
                          />
                        </div>
                      </div>
                      <div class="row q-col-gutter-xl q-mb-lg">
                        <div class="col-12 col-md-6">
                          <q-select
                            v-model="form.visualization"
                            :options="visualizationOptions"
                            label="可视化方式"
                            :rules="[val => !!val || '请选择可视化方式']"
                            outlined
                            color="deep-purple-5"
                          >
                            <template v-slot:option="scope">
                              <q-item v-bind="scope.itemProps">
                                <q-item-section>
                                  <q-item-label>{{ scope.opt.label }}</q-item-label>
                                  <q-item-label caption>
                                    {{ getVisualizationDescription(scope.opt.value) }}
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
                      <div v-if="form.visualization === 'ds9'" class="row q-col-gutter-xl q-mb-lg">
                        <div class="col-12">
                          <q-input
                            v-model="form.ds9Path"
                            label="DS9 路径"
                            :rules="[val => !!val || '请输入 DS9 路径']"
                            outlined
                            color="deep-purple-5"
                          >
                            <template v-slot:append>
                              <q-icon name="search" class="cursor-pointer" @click="selectDS9Path">
                                <q-tooltip>选择 DS9 可执行文件</q-tooltip>
                              </q-icon>
                            </template>
                          </q-input>
                          <div class="text-caption q-mt-sm">
                            请选择 SAOImage DS9 可执行文件的路径。通常在以下位置：
                            <ul>
                              <li>Windows: C:\Program Files\SAOImageDS9\ds9.exe</li>
                              <li>Linux: /usr/bin/ds9</li>
                              <li>macOS: /Applications/SAOImageDS9.app/Contents/MacOS/ds9</li>
                            </ul>
                          </div>
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
                  <div class="text-h6 q-mb-md">目标列表</div>
                  <q-table
                    :rows="targets"
                    :columns="targetColumns"
                    row-key="id"
                    :pagination="{ rowsPerPage: 5 }"
                    flat
                    bordered
                    class="history-table"
                  >
                    <template v-slot:body-cell-actions="props">
                      <q-td :props="props">
                        <q-btn
                          flat
                          round
                          color="negative"
                          icon="delete"
                          @click="removeTarget(props.row.id)"
                        />
                      </q-td>
                    </template>
                  </q-table>
                  <q-separator spaced color="deep-purple-2" class="q-my-lg" />
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
  name: 'PanSTARRSPage',

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

    const manualEntry = ref({
      id: '',
      ra: null,
      dec: null
    })

    const manualEntryErrors = ref({
      id: false,
      ra: false,
      dec: false
    })

    const manualEntryRules = {
      id: [val => !!val || 'ID is required'],
      ra: [
        val => !!val || 'RA is required',
        val => val >= 0 && val <= 360 || 'RA must be between 0 and 360 degrees'
      ],
      dec: [
        val => !!val || 'Dec is required',
        val => val >= -90 && val <= 90 || 'Dec must be between -90 and 90 degrees'
      ]
    }

    const form = ref({
      bands: ['g', 'r', 'i', 'z', 'y'],
      size: 240,
      visualization: 'matplotlib',
      saveDir: 'panstarrs_downloads',
      ds9Path: ''
    })

    const bandOptions = [
      { label: 'g', value: 'g' },
      { label: 'r', value: 'r' },
      { label: 'i', value: 'i' },
      { label: 'z', value: 'z' },
      { label: 'y', value: 'y' }
    ]

    const visualizationOptions = [
      { label: 'Matplotlib', value: 'matplotlib' },
      { label: 'DS9', value: 'ds9' }
    ]

    const targetColumns = [
      { name: 'id', label: 'ID', field: 'id', align: 'left' },
      { name: 'ra', label: 'RA', field: 'ra', align: 'left' },
      { name: 'dec', label: 'Dec', field: 'dec', align: 'left' },
      { name: 'actions', label: 'Actions', field: 'actions', align: 'center' }
    ]

    const historyColumns = [
      { name: 'id', label: 'ID', field: 'id', align: 'left' },
      { name: 'timestamp', label: '时间', field: 'timestamp', align: 'left' },
      { name: 'targets', label: '目标', field: 'targets', align: 'left' },
      { name: 'bands', label: '波段', field: 'bands', align: 'left' },
      { name: 'status', label: '状态', field: 'status', align: 'left' },
      { name: 'progress', label: '进度', field: 'progress', align: 'left' }
    ]

    const isManualEntryValid = computed(() => {
      for (const field of ['id', 'ra', 'dec']) {
        const rules = manualEntryRules[field]
        for (const rule of rules) {
          if (!rule(manualEntry.value[field])) {
            return false
          }
        }
      }
      return true
    })

    const validateManualEntry = () => {
      let hasError = false
      for (const field of ['id', 'ra', 'dec']) {
        const rules = manualEntryRules[field]
        for (const rule of rules) {
          if (!rule(manualEntry.value[field])) {
            manualEntryErrors.value[field] = true
            hasError = true
            break
          }
        }
      }
      return !hasError
    }

    const hasTargets = computed(() => targets.value.length > 0)

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
      // 不清除已添加的目标，因为用户可能已经手动添加了其他目标
    }

    const onFileSelected = async (file) => {
      if (file) {
        try {
          uploadStatus.value = { color: 'text-grey', message: '正在解析 CSV 文件...' }
          const text = await file.text()
          const rows = text.split('\n')
          const headers = rows[0].toLowerCase().split(',').map(h => h.trim())

          // 验证必需的列
          const requiredColumns = ['id', 'ra', 'dec']
          const missingColumns = requiredColumns.filter(col => !headers.includes(col))
          if (missingColumns.length > 0) {
            throw new Error(`CSV 文件缺少必需的列: ${missingColumns.join(', ')}`)
          }

          // 获取列索引
          const idIndex = headers.indexOf('id')
          const raIndex = headers.indexOf('ra')
          const decIndex = headers.indexOf('dec')

          // 解析数据行
          const newTargets = []
          for (let i = 1; i < rows.length; i++) {
            if (!rows[i].trim()) continue // 跳过空行

            const values = rows[i].split(',').map(v => v.trim())
            if (values.length < headers.length) continue // 跳过格式不正确的行

            const id = values[idIndex]
            const ra = parseFloat(values[raIndex])
            const dec = parseFloat(values[decIndex])

            if (isNaN(ra) || isNaN(dec)) {
              console.warn(`跳过第 ${i + 1} 行: 无效的坐标值`)
              continue
            }

            newTargets.push({ id, ra, dec })
          }

          if (newTargets.length === 0) {
            throw new Error('CSV 文件中没有有效的目标数据')
          }

          // 添加新目标
          targets.value = [...targets.value, ...newTargets]

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

    const clearManualEntryError = (field) => {
      manualEntryErrors.value[field] = false
    }

    const addManualTarget = () => {
      if (validateManualEntry()) {
        targets.value.push({
          id: manualEntry.value.id,
          ra: manualEntry.value.ra,
          dec: manualEntry.value.dec
        })
        // Reset form
        manualEntry.value = {
          id: '',
          ra: null,
          dec: null
        }
        // Clear errors
        for (const field in manualEntryErrors.value) {
          manualEntryErrors.value[field] = false
        }
      }
    }

    const removeTarget = (id) => {
      targets.value = targets.value.filter(t => t.id !== id)
    }

    const checkTaskStatus = async (taskId) => {
      try {
        const response = await fetch(`http://localhost:5003/api/status/${taskId}`)
        const data = await response.json()

        // 更新下载历史中的状态
        const historyItem = downloadHistory.value.find(h => h.taskId === taskId)
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

    const onSubmit = async () => {
      if (!hasTargets.value) {
        $q.notify({
          color: 'negative',
          message: '请至少添加一个目标'
        })
        return
      }

      try {
        loading.value = true
        const response = await fetch('http://localhost:5003/api/panstarrs/download', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            targets: targets.value,
            ...form.value
          })
        })

        const data = await response.json()
        if (data.status === 'success') {
          // 保存任务ID并开始定期检查状态
          currentTaskId.value = data.task_id

          // 添加到下载历史
          const historyItem = {
            id: Date.now(),
            taskId: data.task_id,
            timestamp: new Date().toLocaleString(),
            targets: targets.value.map(t => t.id).join(', '),
            bands: form.value.bands.map(band => band.value || band).join(', '),
            status: 'running',
            progress: 0
          }
          downloadHistory.value.unshift(historyItem)

          // 开始定期检查状态
          if (statusCheckInterval.value) {
            clearInterval(statusCheckInterval.value)
          }
          statusCheckInterval.value = setInterval(() => {
            checkTaskStatus(data.task_id)
          }, 2000) // 每2秒检查一次

          $q.notify({
            color: 'positive',
            message: '下载已开始'
          })
        } else {
          throw new Error(data.message || '下载请求失败')
        }
      } catch (error) {
        $q.notify({
          color: 'negative',
          message: `错误: ${error.message}`
        })
      } finally {
        loading.value = false
      }
    }

    const getBandDescription = (band) => {
      const descriptions = {
        'g': '绿色波段 (4686 Å)',
        'r': '红色波段 (6166 Å)',
        'i': '近红外波段 (7480 Å)',
        'z': '红外波段 (8932 Å)',
        'y': '远红外波段 (9633 Å)'
      }
      return descriptions[band] || ''
    }

    const getVisualizationDescription = (type) => {
      const descriptions = {
        'matplotlib': '使用 Matplotlib 生成图像，适合快速预览',
        'ds9': '使用 DS9 生成图像，提供更专业的图像处理功能'
      }
      return descriptions[type] || ''
    }

    const openFilesPage = () => {
      router.push('/files')
    }

    const selectDS9Path = async () => {
      try {
        const result = await window.electron.selectFile({
          filters: [
            { name: 'Executable', extensions: ['exe'] }
          ],
          defaultPath: 'C:\\Program Files\\SAOImageDS9\\ds9.exe'
        })
        if (result) {
          form.value.ds9Path = result
        }
      } catch (error) {
        console.error('选择 DS9 路径失败:', error)
      }
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
      manualEntry,
      manualEntryErrors,
      manualEntryRules,
      targets,
      bandOptions,
      visualizationOptions,
      targetColumns,
      historyColumns,
      downloadHistory,
      isManualEntryValid,
      hasTargets,
      getStatusColor,
      onFileSelected,
      addManualTarget,
      removeTarget,
      onSubmit,
      clearCsvFile,
      uploadStatus,
      getBandDescription,
      getVisualizationDescription,
      openFilesPage,
      selectDS9Path,
      clearManualEntryError,
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
.form-center-wrap {
  max-width: 520px;
  margin: 0 auto;
}
</style>
