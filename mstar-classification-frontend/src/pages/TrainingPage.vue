<template>
  <q-page padding>
    <h4 class="q-my-md">模型训练</h4>
    <p>在这里配置和启动模型训练过程。</p>
    <!-- 训练配置和状态显示占位 -->
    <q-card>
      <q-card-section>
        <div class="text-h6">训练参数</div>
      </q-card-section>
      <q-card-section class="q-gutter-md">
        <q-select v-model="modelType" :options="['Model V1', 'Model V2']" label="选择模型" />
        <q-input v-model.number="epochs" type="number" label="训练轮次 (Epochs)" />
        <q-input v-model.number="batchSize" type="number" label="批量大小 (Batch Size)" />
        <q-input v-model.number="learningRate" type="number" step="0.0001" label="学习率 (Learning Rate)" />
      </q-card-section>
      <q-card-actions align="right">
        <q-btn label="开始训练" color="primary" @click="startTraining" />
      </q-card-actions>
    </q-card>

    <q-card class="q-mt-md">
      <q-card-section>
        <div class="text-h6">训练日志</div>
      </q-card-section>
      <q-card-section>
        <q-linear-progress :value="trainingProgress" class="q-mb-sm" v-if="isTraining" />
        <pre>{{ trainingLog }}</pre>
      </q-card-section>
    </q-card>

  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useQuasar } from 'quasar';

export default defineComponent({
  name: 'TrainingPage',
  setup() {
    const $q = useQuasar();
    const modelType = ref('Model V1');
    const epochs = ref(100);
    const batchSize = ref(32);
    const learningRate = ref(0.001);
    const trainingLog = ref('等待开始训练...');
    const trainingProgress = ref(0);
    const isTraining = ref(false);

    const startTraining = () => {
      isTraining.value = true;
      trainingLog.value = '开始训练模型...\n';
      trainingProgress.value = 0;
      // 模拟训练过程
      let currentEpoch = 0;
      const interval = setInterval(() => {
        currentEpoch++;
        trainingProgress.value = currentEpoch / epochs.value;
        trainingLog.value += `Epoch ${currentEpoch}/${epochs.value} 完成 - 准确率: ${(Math.random() * 0.2 + 0.7).toFixed(4)}\n`;
        if (currentEpoch >= epochs.value) {
          clearInterval(interval);
          trainingLog.value += '训练完成！';
          isTraining.value = false;
          $q.notify({ message: '模型训练完成', color: 'positive' });
        }
      }, 500);
    };

    return {
      modelType,
      epochs,
      batchSize,
      learningRate,
      trainingLog,
      trainingProgress,
      isTraining,
      startTraining,
    };
  },
});
</script> 