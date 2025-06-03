<template>
  <q-page padding class="result-display-page">
    <div v-if="isLoading" class="loading-state row items-center justify-center">
      <q-spinner-dots color="secondary" size="3em" />
      <div class="q-ml-md text-h6">正在加载结果...</div>
    </div>

    <div v-else-if="error" class="error-state text-center">
      <q-icon name="error_outline" color="negative" size="4em" />
      <div class="text-h6 q-mt-md text-negative">加载结果失败</div>
      <p class="q-mt-sm">{{ error }}</p>
      <q-btn label="返回批量检测" color="secondary" @click="goBack" />
    </div>

    <div v-else-if="taskData" class="result-content">
      <q-card class="q-mb-lg result-summary-card">
        <q-card-section>
          <div class="row justify-between items-center">
            <div class="col">
              <h1 class="page-title q-my-none flex items-center">
                <q-icon name="analytics" size="md" class="q-mr-sm text-secondary" />
                检测结果: {{ taskData.task_id }}
              </h1>
              <div class="page-subtitle text-grey-4 q-mt-xs">
                检测于: {{ new Date(taskData.timestamp * 1000).toLocaleString() }}
              </div>
            </div>
            <div class="col-auto">
              <q-btn label="返回批量检测" color="secondary" outline @click="goBack" />
            </div>
          </div>
           <q-separator class="q-my-md" />
          <div class="row q-col-gutter-md text-center">
            <div class="col-md-6 col-12">
              <q-card flat bordered class="info-metric">
                <q-card-section>
                  <div class="text-h4 text-secondary">{{ taskData.files_count }}</div>
                  <div class="text-caption text-grey">处理文件总数</div>
                </q-card-section>
              </q-card>
            </div>
            <div class="col-md-6 col-12">
              <q-card flat bordered class="info-metric">
                <q-card-section>
                  <div class="text-h4 text-secondary">{{ taskData.detection_count }}</div>
                  <div class="text-caption text-grey">检测目标总数</div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </q-card-section>
      </q-card>

      <div class="text-h6 q-mb-md section-title">详细检测结果</div>
      <div v-if="taskData.results && taskData.results.length > 0" class="row q-col-gutter-lg">
        <div v-for="(fileResult, index) in taskData.results" :key="index" class="col-12 col-md-6 col-lg-4">
          <q-card class="result-item-card" flat bordered>
            <q-img 
              v-if="fileResult.result_filename"
              :src="getResultImageUrl(taskData.task_id, fileResult.result_filename)"
              :alt="fileResult.filename"
              spinner-color="secondary"
              style="height: 250px; background-color: #1e293b;"
              fit="contain"
            >
              <template v-slot:error>
                <div class="absolute-full flex flex-center bg-negative text-white">
                  无法加载图片
                </div>
              </template>
            </q-img>
             <q-item-label v-else header class="text-center q-py-xl">
                <q-icon name="image_not_supported" size="xl" color="grey-7" />
                 <div class="text-grey-7 q-mt-sm">无结果图片</div>
            </q-item-label>


            <q-card-section>
              <div class="text-subtitle1 ellipsis">{{ fileResult.filename }}</div>
              <q-chip dense :color="fileResult.detection_count > 0 ? 'positive' : 'grey-7'" text-color="white" icon="api">
                检测到 {{ fileResult.detection_count }} 个目标
              </q-chip>
            </q-card-section>

            <q-separator />

            <q-card-section v-if="fileResult.boxes && fileResult.boxes.length > 0">
              <div class="text-caption text-grey q-mb-xs">检测框信息:</div>
              <q-scroll-area style="height: 100px;">
                <div v-for="(box, bIndex) in fileResult.boxes" :key="bIndex" class="box-info q-mb-xs">
                  <span class="text-weight-medium">目标 {{ bIndex + 1 }}:</span>
                  Conf: {{ box.confidence.toFixed(2) }} 
                  (x1: {{ box.x1.toFixed(0)}}, y1: {{box.y1.toFixed(0)}}, x2: {{ box.x2.toFixed(0)}}, y2: {{ box.y2.toFixed(0)}})
                </div>
              </q-scroll-area>
            </q-card-section>
            <q-card-section v-else class="text-center text-grey">
              未在该图像中检测到明确目标。
            </q-card-section>
          </q-card>
        </div>
      </div>
      <div v-else class="text-center q-pa-xl">
        <q-icon name="info" size="lg" color="grey-7" />
        <p class="text-grey-7 q-mt-md">此任务没有详细的检测结果文件。</p>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { Notify as QNotify } from 'quasar'; // 使用与 BatchDetection.vue 相同的导入方式

defineOptions({
  name: 'ResultDisplayPage'
});

const route = useRoute();
const router = useRouter();
// 如果页面中需要使用Quasar通知等功能，请取消下面这行的注释
// const $q = useQuasar();

const isLoading = ref(true);
const taskData = ref(null);
const error = ref('');
const apiBaseUrl = process.env.API_URL || 'http://localhost:5000';

const taskId = ref(route.params.taskId);

const fetchTaskData = async () => {
  isLoading.value = true;
  error.value = '';
  try {
    // 后端需要实现 /api/task/:taskId 端点
    const response = await axios.get(`${apiBaseUrl}/api/task/${taskId.value}`);
    if (response.data) {
      taskData.value = response.data;
    } else {
      throw new Error('未找到任务数据或响应格式不正确');
    }
  } catch (err) {
    console.error('获取任务数据失败:', err);
    error.value = err.response?.data?.message || err.message || '加载任务详细信息时发生未知错误。';
    QNotify.create({
      color: 'negative',
      message: error.value,
      position: 'top',
      icon: 'error'
    });
    taskData.value = null; // 确保在出错时清除旧数据
  } finally {
    isLoading.value = false;
  }
};

// 构造结果图片的URL，假设后端在 /detection_results/<task_id>/<filename> 提供服务
// 你需要根据实际的后端设置调整此函数
const getResultImageUrl = (currentTaskId, filename) => {
  return `${apiBaseUrl}/results/${currentTaskId}/${filename}`; // 更新路径以匹配后端
};

const goBack = () => {
  router.push('/batch-detection'); // 使用正确的路由路径
};

onMounted(() => {
  if (taskId.value) {
    fetchTaskData();
  } else {
    error.value = '任务ID未提供。';
    isLoading.value = false;
     QNotify.create({
      color: 'negative',
      message: error.value,
      position: 'top',
      icon: 'error'
    });
  }
});
</script>

<style lang="scss" scoped>
.result-display-page {
  padding: 24px;
  background-color: #0a1220; // 深邃的背景色
  color: #e0e0e0;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: white;
  letter-spacing: 0.5px;
}

.page-subtitle {
  font-size: 0.9rem;
  letter-spacing: 0.3px;
  opacity: 0.8;
}

.loading-state, .error-state {
  height: calc(100vh - 100px); /* 视口高度减去一些padding和header */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.result-summary-card, .result-item-card {
  background-color: rgba(14, 23, 41, 0.85); // 半透明深色卡片背景
  border: 1px solid rgba(80, 200, 175, 0.15); // 主题色边框
  backdrop-filter: blur(8px);
  border-radius: 8px;
  color: #e0e0e0;
}

.info-metric {
   background-color: rgba(14, 23, 41, 0.7);
   border: 1px solid rgba(80, 200, 175, 0.1);
   border-radius: 6px;
}

.section-title {
  color: $secondary;
  border-bottom: 2px solid $secondary;
  padding-bottom: 8px;
  display: inline-block;
}

.result-item-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.3);
  }
}

.box-info {
  font-size: 0.8rem;
  padding: 2px 4px;
  background-color: rgba(255,255,255,0.05);
  border-radius: 3px;
}

.ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
