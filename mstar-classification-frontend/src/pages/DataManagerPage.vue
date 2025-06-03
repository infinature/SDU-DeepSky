<template>
  <q-page padding class="data-manager-page">
    <div class="page-header q-mb-xl">
      <h4 class="page-title text-primary q-mt-none q-mb-sm">数据管理中心</h4>
      <p class="text-subtitle1 text-grey-7">在此浏览、可视化和预测已有的恒星光谱及图像数据。</p>
    </div>

    <q-card flat bordered class="table-card">
      <q-card-section class="q-pa-none">
        <q-table
          title="恒星数据列表"
          :rows="starData"
          :columns="columns"
          row-key="specobjid"
          :loading="isLoading"
          :filter="filter"
          class="data-list-table"
          dense
          :rows-per-page-options="[10, 20, 50, 0]"
        >
          <template v-slot:top-right>
            <q-input
              outlined
              dense
              debounce="300"
              v-model="filter"
              placeholder="搜索..."
              class="table-search-input"
            >
              <template v-slot:prepend>
                <q-icon name="search" />
              </template>
              <template v-slot:append v-if="filter">
                <q-icon name="clear" class="cursor-pointer" @click="filter = ''" />
              </template>
            </q-input>
          </template>

          <template v-slot:body-cell-actions="props">
            <q-td :props="props" class="action-buttons-cell">
              <q-btn
                flat
                label="详情"
                @click="showStarDetails(props.row)"
                class="q-mr-sm"
                color="primary"
                size="sm"
              >
                <q-tooltip content-class="bg-primary">查看详情</q-tooltip>
              </q-btn>
              <q-btn
                flat
                label="光谱"
                @click="visualizeSpectrum(props.row)"
                class="q-mr-sm"
                color="secondary"
                size="sm"
              >
                <q-tooltip content-class="bg-secondary">可视化光谱</q-tooltip>
              </q-btn>
              <q-btn
                flat
                label="图像"
                @click="visualizeImage(props.row)"
                class="q-mr-sm"
                color="accent"
                size="sm"
              >
                 <q-tooltip content-class="bg-accent">查看图像</q-tooltip>
              </q-btn>
              <q-btn
                flat
                label="预测"
                @click="goToPrediction(props.row)"
                color="info"
                size="sm"
              >
                <q-tooltip content-class="bg-info">进行分类预测</q-tooltip>
              </q-btn>
            </q-td>
          </template>

          <template v-slot:no-data>
            <div class="full-width row flex-center text-grey-6 q-gutter-sm q-pa-lg">
              <q-icon size="3em" name="sentiment_very_dissatisfied" />
              <span class="text-subtitle1">
                数据加载失败或列表为空
              </span>
              <q-btn flat color="primary" label="重新加载" @click="fetchStarData" class="q-ml-md" icon="refresh"/>
            </div>
          </template>

           <template v-slot:loading>
            <q-inner-loading showing color="primary" label="正在努力加载数据..." label-style="font-size: 1.1em;" />
          </template>
        </q-table>
      </q-card-section>
    </q-card>

    <!-- 图像预览对话框 -->
    <q-dialog v-model="imageDialogVisible">
      <q-card class="image-preview-dialog" style="min-width: 50vw; max-height: 90vh;">
        <q-bar class="bg-primary text-white">
          <q-icon name="mdi-image-area" class="q-mr-sm" />
          <div>图像预览: {{ currentImageFileName }}</div>
          <q-space />
          <q-btn dense flat icon="close" v-close-popup>
            <q-tooltip class="bg-white text-primary">关闭</q-tooltip>
          </q-btn>
        </q-bar>
        <q-separator />
        <q-card-section class="scroll" style="max-height: 80vh;">
          <q-img
            :src="currentImageSrc"
            alt="图像预览"
            spinner-color="primary"
            fit="contain"
            style="min-height: 300px;"
          >
            <template v-slot:error>
              <div class="absolute-full flex flex-center bg-negative text-white text-center">
                <div>
                  <q-icon name="error_outline" size="lg" />
                  <p>无法加载图像</p>
                  <p class="text-caption">{{ currentImageSrc }}</p>
                </div>
              </div>
            </template>
          </q-img>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- 恒星详细信息对话框 -->
    <q-dialog v-model="starDetailsDialogVisible">
      <q-card class="star-details-dialog" style="min-width: 60vw; max-width: 900px; max-height: 90vh;">
         <q-bar class="bg-primary text-white">
          <q-icon name="mdi-star-face" class="q-mr-sm" />
          <div>恒星详情: {{ selectedStarForDetails?.specobjid }}</div>
          <q-space />
          <q-btn dense flat icon="close" v-close-popup>
            <q-tooltip class="bg-white text-primary">关闭</q-tooltip>
          </q-btn>
        </q-bar>
        <q-separator />

        <q-card-section class="scroll" style="max-height: calc(90vh - 50px);">
          <div class="q-gutter-y-lg">
            <div>
              <h6 class="details-section-title">基本信息</h6>
              <q-list bordered separator dense class="rounded-borders">
                <q-item v-for="(value, key) in selectedStarForDetails" :key="key" class="dense-item">
                  <q-item-section side style="min-width: 120px; max-width: 180px;">
                    <q-item-label caption class="text-weight-medium text-grey-8">{{ key }}:</q-item-label>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label class="text-body2" style="word-wrap: break-word; word-break: break-all;">{{ value }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <div>
              <h6 class="details-section-title">图像预览</h6>
              <q-img
                v-if="selectedStarForDetails && selectedStarForDetails.image_path"
                :src="`${IMAGES_BASE_URL}/${selectedStarForDetails.image_path}`"
                class="rounded-borders"
                style="max-height: 400px; max-width: 100%; border: 1px solid #eee"
                fit="contain"
                spinner-color="primary"
              >
                <template v-slot:error>
                  <div class="absolute-full flex flex-center bg-grey-3 text-grey-7 text-center">
                     <div>
                      <q-icon name="mdi-image-off-outline" size="lg" />
                      <p>无法加载图像</p>
                    </div>
                  </div>
                </template>
              </q-img>
              <p v-else class="text-grey-6 q-pa-md text-center">
                <q-icon name="mdi-image-remove-outline" size="md" class="q-mr-sm" />无可用图像路径。
              </p>
            </div>

            <div>
              <h6 class="details-section-title">光谱数据</h6>
              <div v-if="loadingSpectrumDetails" class="flex items-center text-grey-7 q-gutter-sm q-pa-md">
                <q-spinner-gears color="secondary" size="2.5em" />
                <span class="text-subtitle1">光谱数据努力加载中...</span>
              </div>
              <div v-else-if="currentSpectrumData && currentSpectrumData.wavelength && currentSpectrumData.flux && currentSpectrumData.wavelength.length > 0">
                <div class="row q-col-gutter-sm q-mb-sm text-caption text-grey-7">
                  <div class="col-auto">波长数据点: {{ currentSpectrumData.wavelength.length }}</div>
                  <div class="col-auto">流量数据点: {{ currentSpectrumData.flux.length }}</div>
                </div>
                <div class="spectrum-chart-container bg-grey-1 rounded-borders q-pa-sm">
                  <!-- TODO: 在此集成光谱图表库 (例如 Chart.js) -->
                  <div style="border: 1px dashed #ccc; padding: 20px; text-align: center; color: #aaa; min-height: 200px;" class="flex flex-center">
                     <q-icon name="mdi-chart-line" size="lg" class="q-mr-md"/> 光谱图表渲染区域
                  </div>
                </div>
              </div>
              <p v-else-if="selectedStarForDetails && selectedStarForDetails.spectrum_path" class="text-negative q-pa-md text-center rounded-borders bg-red-1">
                <q-icon name="mdi-alert-circle-outline" size="md" class="q-mr-sm"/>未能加载光谱数据。请检查文件路径或后端服务。
              </p>
              <p v-else class="text-grey-6 q-pa-md text-center">
                <q-icon name="mdi-chart-bar-stacked" size="md" class="q-mr-sm"/>无可用光谱文件路径。
              </p>
            </div>
          </div>
        </q-card-section>

        <q-separator />
        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="关闭" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

  </q-page>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { useQuasar, QTableColumn } from 'quasar';

interface StarDataItem {
  specobjid: string;
  objid: string;
  ra: number;
  dec: number;
  subclass: string;
  spectrum_path: string; // 相对于 SPECTRA_DIR
  image_path: string;    // 相对于 IMAGES_DIR
  // ... 其他来自 CSV 的字段
  [key: string]: any; // 允许其他任意字段
}

const $q = useQuasar();
const router = useRouter();

const starData = ref<StarDataItem[]>([]);
const isLoading = ref(false);
const filter = ref('');

const API_BASE_URL = 'http://localhost:5002'; // 更新为正确的后端端口
const SPECTRA_BASE_URL = `${API_BASE_URL}/static/spectra`; // 后端需要配置静态文件服务
const IMAGES_BASE_URL = `${API_BASE_URL}/static/images`;   // 后端需要配置静态文件服务

const imageDialogVisible = ref(false);
const currentImageSrc = ref('');
const currentImageFileName = ref('');

// 新增: 恒星详情相关状态
const starDetailsDialogVisible = ref(false);
const selectedStarForDetails = ref<StarDataItem | null>(null);
const currentSpectrumData = ref<{ wavelength: number[], flux: number[] } | null>(null);
const loadingSpectrumDetails = ref(false);

const columns = computed<QTableColumn<StarDataItem>[]>(() => [
  {
    name: 'specobjid',
    required: true,
    label: 'Spectrum ID',
    align: 'left',
    field: row => row.specobjid,
    format: val => `${val}`,
    sortable: true,
    headerStyle: 'font-weight: 600;'
  },
  {
    name: 'objid',
    label: 'Object ID',
    align: 'left',
    field: row => row.objid,
    sortable: true,
    headerStyle: 'font-weight: 600;'
  },
  {
    name: 'subclass',
    label: 'Subclass',
    align: 'left',
    field: row => row.subclass,
    sortable: true,
    headerStyle: 'font-weight: 600;'
  },
  {
    name: 'ra',
    label: 'RA',
    align: 'right',
    field: row => row.ra,
    format: val => typeof val === 'number' ? val.toFixed(6) : val,
    sortable: true,
    headerStyle: 'font-weight: 600;'
  },
  {
    name: 'dec',
    label: 'Dec',
    align: 'right',
    field: row => row.dec,
    format: val => typeof val === 'number' ? val.toFixed(6) : val,
    sortable: true,
    headerStyle: 'font-weight: 600;'
  },
  // 可以根据需要添加更多来自CSV的列
  // 例如： { name: 'psfMag_r', label: 'r mag', field: 'psfMag_r', sortable: true, align: 'right' },
  {
    name: 'spectrum_path',
    label: '光谱文件',
    align: 'left',
    field: row => row.spectrum_path,
    style: 'max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;',
    headerStyle: 'font-weight: 600;'
  },
  {
    name: 'image_path',
    label: '图像文件',
    align: 'left',
    field: row => row.image_path,
    style: 'max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;',
    headerStyle: 'font-weight: 600;'
  },
  {
    name: 'actions',
    label: '操作',
    align: 'center',
    field: 'actions',
    style: 'min-width: 170px; width: 170px; padding-right: 0;', // Adjusted width
    headerStyle: 'font-weight: 600; text-align: center;'
  }
]);

const fetchStarData = async () => {
  isLoading.value = true;
  try {
    const response = await axios.get<StarDataItem[]>(`${API_BASE_URL}/api/star_data`);
    // 确保所有行都有 specobjid，对于缺失的情况可以考虑赋一个唯一值或过滤掉
    starData.value = response.data.map(item => ({
      ...item,
      specobjid: item.specobjid || `generated-${Math.random().toString(36).substr(2, 9)}` // 或其他处理方式
    }));
    if (response.data.length === 0 && !$q.dialog) {
      $q.notify({
        type: 'info',
        icon: 'mdi-information-outline',
        message: '从服务器加载的恒星数据为空。请检查CSV文件和关联的光谱/图像文件是否正确配置。',
        position: 'top'
      });
    }
  } catch (error) {
    console.error('Error fetching star data:', error);
    $q.notify({
      type: 'negative',
      icon: 'mdi-alert-circle-outline',
      message: '加载恒星数据列表失败。请检查后端服务及CSV文件配置，并确保网络连接正常。',
      multiLine: true,
      position: 'top'
    });
    starData.value = [];
  }
  isLoading.value = false;
};

const visualizeSpectrum = (row: StarDataItem) => {
  if (!row.spectrum_path) {
    $q.notify({ type: 'warning', message: '该条目没有光谱文件路径。', icon: 'mdi-alert-outline' });
    return;
  }
  router.push({ path: '/visualize', query: { spectrumPath: row.spectrum_path } });
};

const visualizeImage = (row: StarDataItem) => {
  if (!row.image_path) {
    $q.notify({ type: 'warning', message: '该条目没有关联的图像路径。', icon: 'mdi-alert-outline' });
    return;
  }
  currentImageSrc.value = `${IMAGES_BASE_URL}/${row.image_path}`;
  currentImageFileName.value = row.image_path.split('/').pop() || '图像';
  imageDialogVisible.value = true;
};

const onImageError = () => {
  console.error('Failed to load image:', currentImageSrc.value);
  // $q.notify({type: 'negative', message: `无法加载图像: ${currentImageFileName.value}`});
  // Error display is now inside q-img slot
}

const goToPrediction = (row: StarDataItem) => {
  if (!row.spectrum_path || !row.image_path) {
    $q.notify({ type: 'warning', message: '需要同时具有光谱和图像文件路径才能进行预测。', icon: 'mdi-alert-outline'});
    return;
  }
  router.push({
    path: '/predict',
    query: {
      spectrumPath: row.spectrum_path,
      imagePath: row.image_path
    }
  });
};

// 新增: 显示恒星详情的方法
const showStarDetails = (row: StarDataItem) => {
  selectedStarForDetails.value = row;
  starDetailsDialogVisible.value = true;
  currentSpectrumData.value = null; // 重置旧数据
  loadingSpectrumDetails.value = false;
  if (row.spectrum_path) {
    fetchSpectrumForDetails(row.spectrum_path);
  } else {
    // 如果没有 spectrum_path，也应清除旧的光谱数据和加载状态
    currentSpectrumData.value = null;
    loadingSpectrumDetails.value = false;
  }
};

// 新增: 获取并解析光谱数据的方法 (用于详情弹窗)
const fetchSpectrumForDetails = async (spectrumPath: string) => {
  if (!spectrumPath) {
    currentSpectrumData.value = null;
    loadingSpectrumDetails.value = false;
    return;
  }
  loadingSpectrumDetails.value = true;
  try {
    const formData = new FormData();
    formData.append('spectrum_path', spectrumPath);

    const response = await axios.post<{ wavelength: number[], flux: number[] }>(
      `${API_BASE_URL}/api/parse_spectrum`,
      formData,
    );
    if (response.data && response.data.wavelength && response.data.flux) {
        currentSpectrumData.value = response.data;
    } else {
        currentSpectrumData.value = null; // Ensure it's reset if data is invalid
        $q.notify({type: 'warning', message: '接收到的光谱数据格式不正确或为空。', icon: 'mdi-alert-outline'})
    }
  } catch (error) {
    console.error('Error fetching or parsing spectrum data for details:', error);
    currentSpectrumData.value = null;
    let errorMessage = '加载或解析光谱数据失败。';
    if (axios.isAxiosError(error) && error.response) {
      errorMessage += ` 错误: ${error.response.data.detail || error.message}`;
    } else if (error instanceof Error) {
      errorMessage += ` 错误: ${error.message}`;
    }
    $q.notify({
      type: 'negative',
      icon: 'mdi-alert-circle-outline',
      message: errorMessage,
      multiLine: true,
      timeout: 7000 
    });
  } finally {
    loadingSpectrumDetails.value = false;
  }
};

onMounted(() => {
  fetchStarData();
});

</script>

<style lang="scss" scoped>
.data-manager-page {
  // background-color: $grey-1; // Optional: a very light grey background for the page
}

.page-header {
  // border-bottom: 1px solid $grey-3;
  // padding-bottom: 16px;
}

.page-title {
  font-weight: 500;
}

.table-card {
  // box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24); // Softer shadow
}
.data-list-table {
  thead th {
    // background-color: $grey-2; // Light grey for table header
    color: $grey-8;
    font-weight: 600; // Already set in column definition
    font-size: 0.8rem;
    text-transform: uppercase;
  }
  // tbody td {
  //   font-size: 0.875rem;
  // }
  // .q-table__title {
  //   font-size: 1.25rem;
  //   color: $primary;
  // }
}

.table-search-input {
  min-width: 250px;
}

.action-buttons-cell {
  white-space: nowrap; 
  overflow: visible; 
  text-align: right; // Align buttons to the right of the cell
  .q-btn {
    // Slightly reduce opacity until hover for a softer look
    // opacity: 0.8;
    // &:hover {
    //   opacity: 1;
    // }
  }
}

.image-preview-dialog, .star-details-dialog {
  .q-bar {
    // Slightly taller bar for a more modern feel
    // min-height: 48px; 
  }
}

.details-section-title {
  font-size: 1rem;
  font-weight: 500;
  color: $primary;
  margin-top: 12px;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid $grey-3;
}

.dense-item .q-item__section--side {
   padding-right: 8px; // Reduce space for dense list key
}

.spectrum-chart-container {
  // border: 1px solid $grey-3;
  // padding: 8px;
}

// General dialog styling
.q-dialog {
  .q-card {
    border-radius: $generic-border-radius; // Use Quasar's generic border radius
  }
}

</style> 