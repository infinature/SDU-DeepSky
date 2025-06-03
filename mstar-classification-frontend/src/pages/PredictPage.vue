<template>
  <q-page padding>
    <h4 class="q-my-md">分类预测</h4>
    <p v-if="!loadedSpectrumPathFromRoute && !loadedImagePathFromRoute">上传光谱、图像和自定义模型权重文件进行分类预测。</p>
    <p v-else>使用来自数据管理页面的文件进行预测。您也可以 <a href="javascript:void(0)" @click="clearAllFiles">手动上传新文件</a>。</p>

    <q-card class="input-card">
      <q-card-section>
        <div class="text-h6">输入数据</div>
      </q-card-section>
      <q-card-section class="q-gutter-md">
        <q-file 
          v-model="modelFile" 
          label="上传模型权重文件 (.pth)" 
          accept=".pth" 
          filled
          counter 
          :disable="isPredicting"
          bottom-slots
        >
          <template v-slot:prepend>
            <q-icon name="mdi-weight-lifter" />
          </template>
        </q-file>

        <!-- Spectrum File Input -->
        <div v-if="loadedSpectrumPathFromRoute && singleSpectrumFileFromRoute" class="q-mb-md">
          <q-banner inline-actions rounded class="bg-grey-2 text-grey-8">
            <template v-slot:avatar><q-icon name="mdi-check-circle" color="positive" /></template>
            预加载光谱: <strong>{{ singleSpectrumFileFromRoute.name }}</strong>
            <template v-slot:action>
              <q-btn flat dense round icon="mdi-close-circle" @click="clearLoadedSpectrumFileFromRoute" title="清除预加载的光谱文件" v-if="!isPredicting"/>
            </template>
          </q-banner>
        </div>
        <q-file 
          v-else
          v-model="spectrumFile" 
          label="上传光谱文件 (.fits, .fit, .fts)"
          accept=".fits,.fit,.fts" 
          filled 
          counter 
          :disable="isPredicting"
        >
          <template v-slot:prepend>
            <q-icon name="mdi-chart-scatter-plot" />
          </template>
        </q-file>
        
        <!-- Image File Input -->
        <div v-if="loadedImagePathFromRoute && singleImageFileFromRoute" class="q-mb-md">
           <q-banner inline-actions rounded class="bg-grey-2 text-grey-8">
            <template v-slot:avatar><q-icon name="mdi-check-circle" color="positive" /></template>
            预加载图像: <strong>{{ singleImageFileFromRoute.name }}</strong>
            <template v-slot:action>
              <q-btn flat dense round icon="mdi-close-circle" @click="clearLoadedImageFileFromRoute" title="清除预加载的图像文件" v-if="!isPredicting"/>
            </template>
          </q-banner>
        </div>
        <q-file 
          v-else
          v-model="imageFile" 
          label="上传图像文件 (.jpg, .png, .jpeg)"
          accept=".jpg,.jpeg,.png" 
          filled 
          counter 
          :disable="isPredicting"
        >
          <template v-slot:prepend>
            <q-icon name="mdi-image" />
          </template>
        </q-file>

      </q-card-section>
      <q-card-actions align="right">
        <q-btn 
          label="开始预测" 
          color="primary" 
          @click="startPrediction" 
          :loading="isPredicting" 
          :disable="!modelFile || (!spectrumFile && !singleSpectrumFileFromRoute) || (!imageFile && !singleImageFileFromRoute)" 
        />
      </q-card-actions>
    </q-card>

    <!-- Spectrum Visualizer Section -->
    <q-card v-if="spectrumFileForVisualizer" class="q-mt-md visualizer-card">
      <q-card-section>
        <SpectrumVisualizer 
          :externalFileToLoad="spectrumFileForVisualizer"
          :hideInternalUploader="true"
        />
      </q-card-section>
    </q-card>

    <div v-if="predictionResult && !isPredicting" class="results-container q-mt-md">
      <h5 class="q-my-md text-center">预测结果</h5>
        <q-card>
          <q-card-section>
            <q-item-label header class="text-subtitle1">
              文件: {{ predictionResult.spectrum_filename }} / {{ predictionResult.image_filename }}
            </q-item-label>
            <div v-if="predictionResult.error" class="text-negative q-pa-md">
              <p><strong>处理错误:</strong></p>
              <p>{{ predictionResult.error }}</p>
            </div>
            <div v-else-if="predictionResult.class_probabilities && predictionResult.class_probabilities.length > 0">
              <ProbabilityBarChart 
                :probabilities="predictionResult.class_probabilities" 
                :title-text="`概率分布: ${predictionResult.spectrum_filename || '光谱'}`" 
              />
            </div>
            <div v-else class="q-pa-md">
              <p>无预测数据或概率信息不可用。</p>
            </div>
          </q-card-section>
        </q-card>
    </div>

    <q-banner v-if="globalError && !isPredicting" class="text-white bg-red q-mt-md" rounded>
      <template v-slot:avatar>
        <q-icon name="error" />
      </template>
      预测过程中发生错误: {{ globalError }}
    </q-banner>

  </q-page>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useQuasar } from 'quasar';
import axios from 'axios';
import ProbabilityBarChart from '../components/ProbabilityBarChart.vue';
import SpectrumVisualizer from '../components/SpectrumVisualizer.vue';

interface ProbabilityItem {
  class_name: string;
  probability: number;
}

interface PredictionResultData {
  spectrum_filename: string | null;
  image_filename: string | null;
  class_probabilities: ProbabilityItem[] | null;
  error: string | null;
}

const $q = useQuasar();
const route = useRoute();

const modelFile = ref<File | null>(null);
const spectrumFile = ref<File | null>(null); // 单个文件
const imageFile = ref<File | null>(null);    // 单个文件

const singleSpectrumFileFromRoute = ref<File | null>(null);
const singleImageFileFromRoute = ref<File | null>(null);
const loadedSpectrumPathFromRoute = ref<string | null>(null);
const loadedImagePathFromRoute = ref<string | null>(null);

const spectrumFileForVisualizer = ref<File | null>(null); // For SpectrumVisualizer

const predictionResult = ref<PredictionResultData | null>(null); // 单个结果对象
const globalError = ref<string | null>(null); 
const isPredicting = ref(false);

const API_BASE_URL = 'http://localhost:5002';

async function fetchFileFromPath(relativePath: string, fileType: 'spectrum' | 'image'): Promise<File | null> {
  if (!relativePath) return null;
  const defaultFileName = relativePath.split('/').pop() || (fileType === 'spectrum' ? 'spectrum.fits' : 'image.jpg');
  $q.loading.show({ message: `正在加载 ${defaultFileName} (API)...` });
  try {
    const response = await axios.get(`${API_BASE_URL}/api/fetch_file/${fileType}/${relativePath}`, {
      responseType: 'blob',
    });
    if (response.status < 200 || response.status >= 300) {
      throw new Error(`下载文件失败: ${response.status} ${response.statusText}`);
    }
    const blob = response.data as Blob;
    let mimeType = 'application/octet-stream';
    if (fileType === 'spectrum' && (defaultFileName.endsWith('.fits') || defaultFileName.endsWith('.fit') || defaultFileName.endsWith('.fts'))) {
      mimeType = 'application/fits'; 
    } else if (fileType === 'image') {
      if (defaultFileName.endsWith('.jpg') || defaultFileName.endsWith('.jpeg')) mimeType = 'image/jpeg';
      else if (defaultFileName.endsWith('.png')) mimeType = 'image/png';
    }
    return new File([blob], defaultFileName, { type: mimeType });
  } catch (error) {
    console.error(`Error fetching file ${relativePath} (type: ${fileType}) via API:`, error);
    let errorMessage = `加载 ${defaultFileName} (API) 失败.`;
    if (axios.isAxiosError(error)) {
      const serverError = error.response?.data?.detail || error.response?.statusText || error.message;
      errorMessage += ` 错误: ${error.response?.status || 'N/A'} - ${serverError}`;
    } else if (error instanceof Error) {
        errorMessage += ` 错误: ${error.message}`;
    } else {
        errorMessage += ' 未知错误.';
    }
    $q.notify({ type: 'negative', message: errorMessage, multiLine: true, timeout: 7000 });
    return null;
  } finally {
    $q.loading.hide();
  }
}

const startPrediction = async () => {
  const finalSpectrumFile = singleSpectrumFileFromRoute.value || spectrumFile.value;
  const finalImageFile = singleImageFileFromRoute.value || imageFile.value;

  if (!modelFile.value) {
    $q.notify({ type: 'negative', message: '请上传模型权重文件。' });
    return;
  }
  if (!finalSpectrumFile) {
    $q.notify({ type: 'negative', message: '请上传光谱文件。' });
    return;
  }
  if (!finalImageFile) {
    $q.notify({ type: 'negative', message: '请上传图像文件。' });
    return;
  }

  isPredicting.value = true;
  predictionResult.value = null;
  globalError.value = null;

  const formData = new FormData();
  formData.append('model_file', modelFile.value);
  formData.append('spectrum_file', finalSpectrumFile);
  formData.append('image_file', finalImageFile);
  
  try {
    const response = await axios.post<PredictionResultData>(`${API_BASE_URL}/api/predict`, formData, { 
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    // 后端直接返回单个结果对象，或包含 error 字段的对象
    predictionResult.value = response.data;
    if (response.data.error) {
        $q.notify({ message: `预测处理时发生错误: ${response.data.error}`, color: 'warning', icon: 'warning', multiLine: true });
    } else if (response.data.class_probabilities) {
        $q.notify({ message: '预测成功!', color: 'positive', icon: 'check_circle'});
    } else {
        // Should not happen if backend behaves as expected
        $q.notify({ message: '收到未知的预测响应结构。', color: 'warning', icon: 'warning' });
    }

  } catch (error: any) {
    console.error('Prediction API error:', error);
    if (error.response && error.response.data && error.response.data.error) { // Backend defined error structure
        globalError.value = `错误 ${error.response.status}: ${error.response.data.error}`;
    } else if (error.response && error.response.data && error.response.data.detail) { // FastAPI HTTPValidationErrors
        globalError.value = `错误 ${error.response.status}: ${error.response.data.detail}`;
    } else if (error.request) {
      globalError.value = '无法连接到服务器，请检查后端服务是否运行以及网络连接。';
    } else {
      globalError.value = error.message || '发生未知错误';
    }
    $q.notify({ type: 'negative', message: globalError.value, multiLine: true, timeout: 7000 });
    predictionResult.value = null; // Clear any partial result on global error
  }
  isPredicting.value = false;
};

const processRouteParams = async () => {
  const specPathQuery = route.query.spectrumPath as string | undefined;
  const imgPathQuery = route.query.imagePath as string | undefined;

  clearAllFiles();

  if (specPathQuery && imgPathQuery) {
    $q.notify({ message: '检测到传入路径，尝试加载文件对...', icon: 'info', color: 'info', position: 'top' });
    loadedSpectrumPathFromRoute.value = specPathQuery;
    loadedImagePathFromRoute.value = imgPathQuery;

    const fetchedSpectrumFile = await fetchFileFromPath(specPathQuery, 'spectrum');
    const fetchedImageFile = await fetchFileFromPath(imgPathQuery, 'image');

    if (fetchedSpectrumFile && fetchedImageFile) {
      singleSpectrumFileFromRoute.value = fetchedSpectrumFile;
      singleImageFileFromRoute.value = fetchedImageFile;
      // Clear manual selections if route params are used
      spectrumFile.value = null; 
      imageFile.value = null;
      $q.notify({ message: '文件已从路径加载。请选择模型并开始预测。', color: 'positive'});
    } else {
      $q.notify({ type: 'negative', message: '无法通过API加载一个或两个文件。请检查路径或手动上传。' });
      clearLoadedFilesFromRoute();
    }
  } else {
    clearLoadedFilesFromRoute(); // Ensure these are cleared if no route params
  }
};

const clearLoadedFilesFromRoute = () => {
    loadedSpectrumPathFromRoute.value = null;
    loadedImagePathFromRoute.value = null;
    singleSpectrumFileFromRoute.value = null;
    singleImageFileFromRoute.value = null;
};

const clearLoadedSpectrumFileFromRoute = () => {
    loadedSpectrumPathFromRoute.value = null;
    singleSpectrumFileFromRoute.value = null;
    predictionResult.value = null; // Clear results if input changes
    globalError.value = null;
};
const clearLoadedImageFileFromRoute = () => {
    loadedImagePathFromRoute.value = null;
    singleImageFileFromRoute.value = null;
    predictionResult.value = null; // Clear results if input changes
    globalError.value = null;
};

const clearAllFiles = () => {
  modelFile.value = null;
  spectrumFile.value = null;
  imageFile.value = null;
  clearLoadedFilesFromRoute();
  predictionResult.value = null;
  globalError.value = null;
  spectrumFileForVisualizer.value = null; // Ensure visualizer is also cleared
};

onMounted(async () => {
  await processRouteParams();
});

watch(() => route.query, async (newQuery, oldQuery) => {
  if (newQuery.spectrumPath !== oldQuery.spectrumPath || newQuery.imagePath !== oldQuery.imagePath) {
    await processRouteParams();
  }
}, { deep: true });

// Watch for manual file changes to clear route-loaded files if user interacts
watch(spectrumFile, (newValue) => {
    if (newValue && singleSpectrumFileFromRoute.value) {
        clearLoadedSpectrumFileFromRoute(); 
    }
});
watch(imageFile, (newValue) => {
    if (newValue && singleImageFileFromRoute.value) {
        clearLoadedImageFileFromRoute();
    }
});

// Watch for changes in spectrumFile or singleSpectrumFileFromRoute to update spectrumFileForVisualizer
watch([spectrumFile, singleSpectrumFileFromRoute], ([newSpectrumFile, newSingleSpectrumFileFromRoute]) => {
  if (newSingleSpectrumFileFromRoute) {
    spectrumFileForVisualizer.value = newSingleSpectrumFileFromRoute;
  } else {
    spectrumFileForVisualizer.value = newSpectrumFile;
  }
}, { immediate: true });

</script>

<style scoped>
.input-card {
  max-width: 700px;
  margin: 20px auto;
}
.visualizer-card { /* Added style for visualizer card */
  max-width: 800px; /* Match SpectrumVisualizer's typical max-width if desired */
  margin: 20px auto;
}
.results-container {
  max-width: 900px;
  margin: 20px auto;
}
</style> 