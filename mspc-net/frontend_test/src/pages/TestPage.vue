<template>
  <div class="q-pa-md page-container">
    <!-- 标题栏 -->
    <div class="q-mb-md flex items-center">
      <q-icon name="science" size="32px" class="text-primary q-mr-sm" />
      <div class="text-h5 text-weight-bold text-primary">MSPC-Net 模型训练</div>
    </div>

    <!-- 参数配置卡片 -->
    <q-card class="main-card q-mb-xl">
      <q-card-section>
        <div class="text-subtitle1 text-primary q-mb-sm">
          ⚙️ 训练参数配置
        </div>

        <!-- 数据集路径 -->
        <q-input
          filled
          dense
          v-model="dataDir"
          label="📁 数据集路径（如 D:/MyData/kfold_0）"
          placeholder="请输入你的本地数据集文件夹路径"
          class="q-mb-md"
          color="primary"
        />

        <!-- 折叠参数项 -->
        <q-expansion-item icon="tune" label="训练超参数" expand-separator default-opened>
          <div class="row q-col-gutter-md q-mt-sm">
            <q-input v-model.number="params.lr" label="学习率 (lr)" type="number" filled dense class="col-4" />
            <q-input v-model.number="params.batch_size" label="Batch Size" type="number" filled dense class="col-4" />
            <q-input v-model.number="params.epochs" label="训练轮数 (Epochs)" type="number" filled dense class="col-4" />
          </div>
        </q-expansion-item>

        <q-expansion-item icon="dns" label="数据设置" expand-separator>
          <div class="row q-col-gutter-md q-mt-sm">
            <q-input v-model="params.class_names" label="类别名（英文逗号分隔）" filled dense class="col-6" />
            <q-input v-model.number="params.num_classes" label="类别数量" type="number" filled dense class="col-6" />
            <q-input v-model.number="params.spectrum_length" label="光谱长度" type="number" filled dense class="col-6" />
          </div>
        </q-expansion-item>

        <q-expansion-item icon="settings" label="系统配置" expand-separator>
          <div class="row q-col-gutter-md q-mt-sm">
            <q-input v-model="params.device_list" label="设备列表（如 [0]）" filled dense class="col-6" />
            <q-input v-model.number="params.num_workers" label="数据加载线程数" type="number" filled dense class="col-6" />
          </div>
        </q-expansion-item>

        <!-- 启动按钮 -->
        <div class="row q-mt-lg q-gutter-md justify-start">
          <q-btn
            label="🚀启动训练"
            color="primary"
            icon="play_arrow"
            :disable="training"
            @click="startTraining"
            unelevated
            no-caps
          />
          <q-btn
            v-if="training"
            label="⛔终止训练"
            color="red"
            icon="stop"
            flat
            @click="stopTraining"
            no-caps
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- 日志输出区 -->
    <q-card v-if="training || logContent" class="log-card">
      <q-card-section>
        <div class="text-subtitle2 text-primary">📜 训练日志</div>
        <div ref="logBox" class="log-box q-mt-sm">
          <pre class="log-output">{{ logContent }}</pre>
        </div>
      </q-card-section>
    </q-card>

    <!-- 训练结果展示 -->
    <q-card v-if="result && result.accuracy" flat class="result-card q-mt-lg">
      <q-card-section>
        <div class="text-h6 text-green-8">✅ 准确率 Accuracy: {{ result.accuracy }}%</div>
        <q-linear-progress :value="result.accuracy / 100" color="green" size="10px" class="q-mt-sm" />
      </q-card-section>
      <q-separator />
      <q-card-section>
        <div class="text-subtitle2 text-grey-8 q-mb-sm">📊 其他指标</div>
        <q-list dense bordered separator>
          <q-item v-for="(val, key) in otherMetrics" :key="key">
            <q-item-section>{{ key }}</q-item-section>
            <q-item-section side>
              <q-badge color="primary" :label="val + '%'" />
            </q-item-section>
          </q-item>
        </q-list>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick } from 'vue'
import { useQuasar } from 'quasar'
import axios from 'axios'

const $q = useQuasar()
const dataDir = ref('')
const training = ref(false)
const result = ref(null)
const logContent = ref('')
const logBox = ref(null)
let eventSource = null

const params = reactive({
  lr: 0.001,
  batch_size: 32,
  epochs: 10,
  class_names: "O,B,A,F,G,K,M",
  num_classes: 7,
  spectrum_length: 3584,
  device_list: "[0]",
  num_workers: 2
})

function startTraining() {
  if (!dataDir.value) {
    $q.notify({ type: 'warning', message: '请填写数据集路径！' })
    return
  }

  training.value = true
  result.value = null
  logContent.value = ''

  axios.post('http://localhost:5001/train', {
    data_dir: dataDir.value,
    parameters: params
  }).then(() => {
    eventSource = new EventSource('http://localhost:5001/train/log')
    eventSource.onmessage = (e) => {
      logContent.value += e.data + '\n'
      nextTick(() => {
        if (logBox.value) logBox.value.scrollTop = logBox.value.scrollHeight
      })
      if (e.data.startsWith('{') && e.data.includes('accuracy')) {
        try {
          result.value = JSON.parse(e.data)
          training.value = false
          eventSource.close()
          $q.notify({ type: 'positive', message: '训练完成 🎉' })
        } catch (e) {
          console.error('JSON 解析失败:', e)
        }
      }
    }
    eventSource.onerror = () => {
      training.value = false
      eventSource?.close()
      $q.notify({ type: 'warning', message: '连接中断或训练结束' })
    }
  }).catch((err) => {
    training.value = false
    $q.notify({ type: 'negative', message: '训练启动失败' })
    console.error(err)
  })
}

function stopTraining() {
  axios.post('http://localhost:5001/train/stop')
  training.value = false
  eventSource?.close()
  $q.notify({ type: 'negative', message: '训练终止请求已发送 🛑' })
}

const otherMetrics = computed(() => {
  if (!result.value) return {}
  return {
    'F1 Score': result.value.f1,
    Precision: result.value.precision,
    Recall: result.value.recall
  }
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: var(--md-sys-color-surface);
}

.main-card {
  background-color: var(--md-sys-color-surface-container);
  border-radius: 16px;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.06);
}

.log-card {
  background-color: var(--md-sys-color-surface-container-low);
  border-radius: 14px;
}

.result-card {
  background-color: var(--md-sys-color-surface-container);
  border-radius: 16px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
}

.log-box {
  max-height: 300px;
  overflow-y: auto;
  padding: 10px;
  background-color: var(--md-sys-color-surface);
  border-radius: 10px;
  border: 1px solid var(--md-sys-color-outline-variant);
  font-family: 'Cascadia Code', Consolas, monospace;
  font-size: 13px;
  color: var(--md-sys-color-on-surface);
}

.log-output {
  font-family: 'Cascadia Code', Consolas, 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
  color: #2e2e2e;
}
</style>
