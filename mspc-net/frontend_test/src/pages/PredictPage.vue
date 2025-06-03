<template>
  <div class="page-container">
    <!-- 装饰性背景 -->
    <div class="background-decoration">
      <div class="decoration-circle circle-1"></div>
      <div class="decoration-circle circle-2"></div>
      <div class="decoration-circle circle-3"></div>
    </div>

    <!-- 左侧操作面板 -->
    <div class="left-panel">
      <div class="panel-content">
        <div class="title-wrapper">
          <q-icon name="analytics" size="2.5rem" class="title-icon" />
          <div class="title-text">光谱文件预测</div>
        </div>

        <div class="upload-section">
          <q-select
            v-model="selectedFile"
            :options="availableFiles"
            label="📂 选择已有光谱文件"
            outlined
            dense
            clearable
            emit-value
            map-options
            class="glass-select"
          />

          <q-uploader
            label="📁 上传光谱文件（支持批量 CSV）"
            :multiple="true"
            accept=".csv"
            auto-upload
            flat
            bordered
            class="glass-uploader"
            @added="handleFilesAdded"
          />

          <q-uploader
            label="🧠 上传模型权重文件（可选）"
            accept=".ckpt"
            :multiple="false"
            auto-upload
            flat
            bordered
            class="glass-uploader"
            @added="handleCkptUpload"
          />

          <q-btn
            label="🚀 开始预测"
            color="primary"
            class="predict-button"
            :loading="loading"
            unelevated
            size="lg"
            no-caps
            @click="runPrediction"
          >
            <template v-slot:loading>
              <q-spinner-ios size="20px" class="q-mr-sm" />
              正在预测...
            </template>
          </q-btn>
        </div>
      </div>
    </div>

    <!-- 右侧结果面板 -->
    <div class="right-panel">
      <div class="panel-content">
        <template v-if="results.length">
          <div class="result-header">
            <div class="result-title">
              <q-icon name="analytics" size="2rem" class="result-icon" />
              <span>🎯 预测结果</span>
            </div>
            <div class="result-actions">
              <q-btn
                outline
                color="positive"
                icon="save"
                label="导出 CSV"
                @click="exportCSV"
                class="action-btn"
              />
              <q-btn
                outline
                color="info"
                icon="description"
                label="导出 TXT"
                @click="exportTXT"
                class="action-btn"
              />
            </div>
          </div>

          <q-table
            :rows="results"
            :columns="columns"
            flat
            bordered
            dense
            row-key="filename"
            separator="horizontal"
            table-class="text-grey-9"
            class="result-table"
          />
        </template>
        <template v-else>
          <div class="empty-state">
            <div class="empty-state-content">
              <q-icon name="science" size="5rem" class="empty-icon" />
              <h2 class="empty-title">欢迎使用光谱预测平台</h2>
              <p class="empty-description">
                在左侧上传您的光谱文件，我们将为您提供准确的预测结果。
              </p>
              <div class="feature-list">
                <div class="feature-item">
                  <q-icon name="upload_file" size="1.5rem" />
                  <span>批量上传光谱CSV</span>
                </div>
                <div class="feature-item">
                  <q-icon name="psychology" size="1.5rem" />
                  <span>智能模型预测</span>
                </div>
                <div class="feature-item">
                  <q-icon name="analytics" size="1.5rem" />
                  <span>详细的结果分析</span>
                </div>
                <div class="feature-item">
                  <q-icon name="download" size="1.5rem" />
                  <span>多种格式导出</span>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import axios from 'axios'

const $q = useQuasar()

const selectedFile = ref('')
const uploadedFiles = ref([])
const loading = ref(false)
const results = ref([])
const ckptFile = ref(null)

const availableFiles = [
  { label: 'spec-0613-52345-0363.csv', value: 'spec-0613-52345-0363.csv' },
  { label: 'spec-0845-52385-0456.csv', value: 'spec-0845-52385-0456.csv' },
]

const columns = [
  { name: 'filename', label: '文件名', field: 'filename', align: 'left' },
  { name: 'class', label: '预测类别', field: 'class' },
  { name: 'confidence', label: '置信度', field: 'confidence', format: (val) => val.toFixed(4) },
]

function handleFilesAdded(files) {
  uploadedFiles.value = files
}

async function runPrediction() {
  loading.value = true
  results.value = []

  const formData = new FormData()
  uploadedFiles.value.forEach((file) => formData.append('files', file))
  if (selectedFile.value) {
    formData.append('selected_file', selectedFile.value)
  }
  if (ckptFile.value) formData.append('ckpt', ckptFile.value)

  try {
    const response = await axios.post('http://localhost:5001/predict', formData)
    results.value = response.data.results
  } catch (err) {
    console.error('请求失败:', err)
    $q.notify({ type: 'negative', message: '预测失败，请检查服务端或文件格式' })
  } finally {
    loading.value = false
  }
}

function handleCkptUpload(files) {
  ckptFile.value = files[0]
}

function exportCSV() {
  let content = 'filename,class,confidence\n'
  results.value.forEach((item) => {
    content += `${item.filename},${item.class},${item.confidence}\n`
  })
  downloadFile(content, 'prediction_result.csv')
}

function exportTXT() {
  let content = ''
  results.value.forEach((item) => {
    content += `文件：${item.filename}，预测：${item.class}，置信度：${item.confidence}\n`
  })
  downloadFile(content, 'prediction_result.txt')
}

function downloadFile(content, filename) {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  display: flex;
  background: linear-gradient(135deg, var(--md-sys-color-background) 0%, #eef2f7 100%);
  position: relative;
  overflow: hidden;
}

.background-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  filter: blur(80px);
}

.circle-1 {
  width: 800px;
  height: 800px;
  background: #4a90e2;
  top: -300px;
  right: -200px;
}

.circle-2 {
  width: 600px;
  height: 600px;
  background: #50e3c2;
  bottom: -200px;
  left: -200px;
}

.circle-3 {
  width: 500px;
  height: 500px;
  background: #f5a623;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.left-panel {
  width: 400px;
  min-height: 100vh;
  background: rgba(240, 242, 245, 0.95);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 1;
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.05);
}

.right-panel {
  flex: 1;
  min-height: 100vh;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
}

.panel-content {
  padding: 2rem;
  height: 100%;
}

.title-wrapper {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.title-icon {
  color: var(--md-sys-color-primary);
  background: rgba(var(--md-sys-color-primary-rgb), 0.1);
  padding: 1rem;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(var(--md-sys-color-primary-rgb), 0.15);
}

.title-text {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(45deg, var(--md-sys-color-primary), var(--md-sys-color-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.upload-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.glass-select,
.glass-uploader {
  border-radius: 16px;
  background-color: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.glass-select:hover,
.glass-uploader:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
  background-color: rgba(255, 255, 255, 0.8);
}

.predict-button {
  width: 100%;
  border-radius: 16px;
  font-weight: 600;
  font-size: 1.1rem;
  letter-spacing: 0.5px;
  transition: all var(--delay-3) ease;
  background: linear-gradient(45deg, var(--md-sys-color-primary), var(--md-sys-color-secondary));
  box-shadow: 0 8px 20px rgba(var(--md-sys-color-primary-rgb), 0.2);
  margin-top: 1rem;
}

.predict-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(var(--md-sys-color-primary-rgb), 0.3);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.result-title {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: #2a2a2a;
}

.result-icon {
  color: var(--md-sys-color-primary);
  background: rgba(var(--md-sys-color-primary-rgb), 0.1);
  padding: 0.8rem;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(var(--md-sys-color-primary-rgb), 0.15);
}

.result-actions {
  display: flex;
  gap: 1rem;
}

.action-btn {
  border-radius: 12px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.result-table {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.result-table :deep(th) {
  background: rgba(240, 243, 248, 0.8);
  font-weight: 600;
  font-size: 0.9rem;
  padding: 1rem;
  color: #2a2a2a;
}

.result-table :deep(td) {
  font-size: 0.9rem;
  padding: 1rem;
  color: #4a4a4a;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.empty-state-content {
  text-align: center;
  max-width: 600px;
  padding: 3rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 24px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.empty-icon {
  color: var(--md-sys-color-primary);
  background: rgba(var(--md-sys-color-primary-rgb), 0.1);
  padding: 1.5rem;
  border-radius: 50%;
  margin-bottom: 1.5rem;
  box-shadow: 0 8px 32px rgba(var(--md-sys-color-primary-rgb), 0.15);
}

.empty-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2a2a2a;
  margin-bottom: 1rem;
  background: linear-gradient(45deg, var(--md-sys-color-primary), var(--md-sys-color-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.empty-description {
  font-size: 1.1rem;
  color: #666;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.feature-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-top: 2rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.feature-item .q-icon {
  color: var(--md-sys-color-primary);
  background: rgba(var(--md-sys-color-primary-rgb), 0.1);
  padding: 0.5rem;
  border-radius: 8px;
}

.feature-item span {
  font-size: 1rem;
  color: #4a4a4a;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .page-container {
    flex-direction: column;
  }

  .left-panel {
    width: 100%;
    min-height: auto;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  }

  .right-panel {
    min-height: auto;
  }

  .panel-content {
    padding: 1.5rem;
  }

  .title-text {
    font-size: 1.3rem;
  }

  .result-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .result-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .feature-list {
    grid-template-columns: 1fr;
  }

  .empty-state-content {
    padding: 2rem;
  }

  .empty-title {
    font-size: 1.5rem;
  }

  .empty-description {
    font-size: 1rem;
  }
}
</style>
