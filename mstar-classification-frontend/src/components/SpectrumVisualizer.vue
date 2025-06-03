<template>
  <q-card>
    <q-card-section>
      <div class="text-h6">光谱查看器</div>
      <div v-if="!props.hideInternalUploader && !isLoadedFromPath" class="q-mb-md">
        <q-file
          v-model="fitsFile"
          label="选择 FITS 光谱文件"
          accept=".fits,.fit,.fts"
          filled
          @update:model-value="handleFileChange"
        >
          <template v-slot:prepend>
            <q-icon name="attach_file" />
          </template>
        </q-file>
      </div>
      <div v-if="isLoadedFromPath && spectrumPathFromRoute" class="q-mb-md">
        <q-banner rounded class="bg-blue-1 text-primary">
          <template v-slot:avatar>
            <q-icon name="link" />
          </template>
          正在显示光谱: <strong>{{ spectrumPathFromRoute }}</strong>
          <template v-slot:action>
            <q-btn flat color="primary" label="选择其他文件" @click="clearPathAndShowUploader" dense />
          </template>
        </q-banner>
      </div>
    </q-card-section>

    <q-card-section v-if="loading">
      <div class="row justify-center q-my-md">
        <q-spinner-dots color="primary" size="40px" />
        <p class="q-ml-sm text-primary">正在加载光谱数据...</p>
      </div>
    </q-card-section>

    <q-card-section v-if="errorMessage">
      <q-banner inline-actions class="text-white bg-red" rounded>
        <template v-slot:avatar>
          <q-icon name="error" />
        </template>
        {{ errorMessage }}
      </q-banner>
    </q-card-section>

    <q-card-section v-if="!loading && !errorMessage && chartData.labels && chartData.labels.length > 0">
      <LineChart :data="chartData" :options="chartOptions" style="height: 400px;" />
    </q-card-section>
    <q-card-section v-else-if="!loading && !errorMessage && (!chartData.labels || chartData.labels.length === 0) && (fitsFile || isLoadedFromPath || props.externalFileToLoad)">
      <q-banner class="bg-grey-3">
        <template v-slot:avatar>
          <q-icon name="info" color="info" />
        </template>
        成功加载 FITS 文件，但未在其中找到可显示的光谱数据。
      </q-banner>
    </q-card-section>
    <q-card-section v-else-if="!loading && !errorMessage && !fitsFile && !isLoadedFromPath && !props.externalFileToLoad">
      <p class="text-grey-7 text-center q-pa-md">请选择一个 FITS 文件或通过有效路径访问以显示光谱。</p>
    </q-card-section>
  </q-card>
</template>

<script lang="ts" setup>
import { ref, watch, onMounted, PropType } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { QCard, QCardSection, QFile, QIcon, QSpinnerDots, QBanner, QBtn, useQuasar } from 'quasar';
import axios from 'axios';
import { Line as LineChart } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  type ChartData,
  type ChartOptions,
} from 'chart.js';

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement
);

declare var astro: any;

const props = defineProps({
  externalFileToLoad: {
    type: Object as PropType<File | null>,
    default: null,
  },
  hideInternalUploader: {
    type: Boolean,
    default: false,
  }
});

const fitsFile = ref<File | null>(null);
const loading = ref(false);
const errorMessage = ref<string | null>(null);

const route = useRoute();
const router = useRouter();
const $q = useQuasar();
const API_BASE_URL = 'http://localhost:5002';
const spectrumPathFromRoute = ref<string | null>(null);
const isLoadedFromPath = ref(false);

const chartData = ref<ChartData<'line', number[], string>>({
  labels: [] as string[],
  datasets: [
    {
      label: 'Flux',
      backgroundColor: '#42A5F5',
      borderColor: '#1E88E5',
      data: [] as number[],
      fill: false,
      tension: 0.1,
      pointRadius: 0,
    },
  ],
});

const chartOptions = ref<ChartOptions<'line'>>({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      title: {
        display: true,
        text: 'Wavelength (Angstrom)',
      },
    },
    y: {
      title: {
        display: true,
        text: 'Flux',
      },
       ticks: {
          callback: function(value: string | number) {
            if (typeof value === 'number') {
                 return value.toExponential(2);
            }
            return value;
          }
        }
    },
  },
  plugins: {
    legend: {
      display: true,
    },
    tooltip: {
      mode: 'index',
      intersect: false,
      callbacks: {
            label: function(context) {
                let label = context.dataset.label || '';
                if (label) {
                    label += ': ';
                }
                if (context.parsed.y !== null) {
                    label += context.parsed.y.toExponential(3);
                }
                return label;
            }
        }
    },
  },
  animation: {
    duration: 0,
  },
});

const resetState = (keepPathLoadedStatus = false) => {
  loading.value = false;
  errorMessage.value = null;
  chartData.value = {
    labels: [] as string[],
    datasets: [
      {
        label: 'Flux',
        backgroundColor: '#42A5F5',
        borderColor: '#1E88E5',
        data: [] as number[],
        fill: false,
        tension: 0.1,
        pointRadius: 0,
      },
    ],
  };
  if (!keepPathLoadedStatus) {
    isLoadedFromPath.value = false;
    spectrumPathFromRoute.value = null;
  }
};

const fetchSpectrumByPath = async (path: string) => {
  resetState(true);
  loading.value = true;
  isLoadedFromPath.value = true;
  spectrumPathFromRoute.value = path;
  fitsFile.value = null;

  try {
    const formData = new FormData();
    formData.append('spectrum_path', path);

    const response = await axios.post<{ wavelength: number[], flux: number[] }>(
      `${API_BASE_URL}/api/parse_spectrum`,
      formData
    );

    if (response.data && response.data.wavelength && response.data.flux) {
      if (response.data.wavelength.length === 0 || response.data.flux.length === 0) {
        errorMessage.value = `光谱数据为空 (波长: ${response.data.wavelength.length}, 流量: ${response.data.flux.length})。`;
        $q.notify({ type: 'warning', message: errorMessage.value });
        chartData.value = {
          labels: [],
          datasets: [{ ...chartData.value.datasets[0], data: [] }]
        };
      } else {
        chartData.value = {
          labels: response.data.wavelength.map(w => typeof w === 'number' ? w.toFixed(2) : String(w)),
          datasets: [
            {
              ...chartData.value.datasets[0],
              data: response.data.flux,
            },
          ],
        };
        errorMessage.value = null;
      }
    } else {
      errorMessage.value = '从API获取的光谱数据格式不正确或为空。';
       $q.notify({ type: 'negative', message: errorMessage.value });
    }
  } catch (error) {
    console.error('Error fetching spectrum by path:', error);
    if (axios.isAxiosError(error) && error.response) {
      errorMessage.value = `无法加载光谱: ${error.response.data.detail || error.message}`;
    } else if (error instanceof Error) {
      errorMessage.value = `无法加载光谱: ${error.message}`;
    } else {
      errorMessage.value = '加载光谱时发生未知错误。';
    }
    $q.notify({ type: 'negative', message: errorMessage.value, multiLine: true });
  } finally {
    loading.value = false;
  }
};

const processFitsFile = (file: File) => {
  if (props.externalFileToLoad !== file) {
    resetState(isLoadedFromPath.value);
  } else {
    // For external files, resetState is called in the watcher before processFitsFile
  }
  loading.value = true;
  if (props.externalFileToLoad === file) {
  isLoadedFromPath.value = false;
  spectrumPathFromRoute.value = null;
    fitsFile.value = null;
  }

  if (!file) {
    errorMessage.value = '未选择文件';
    loading.value = false;
    return;
  }

  if (typeof astro === 'undefined' || typeof astro.FITS === 'undefined') {
    errorMessage.value = 'FITS 解析库 (fits.js) 未加载。请确保已将其正确引入。';
    loading.value = false;
    console.error('astro or astro.FITS is not defined.');
    return;
  }

  new astro.FITS(file, (fitsObject: any) => {
    if (!fitsObject || !fitsObject.hdus || fitsObject.hdus.length === 0) {
      errorMessage.value = '无法解析 FITS 文件或文件不包含 HDU。';
      loading.value = false;
      return;
    }

    let spectrumFound = false;

    const tryLoadHDUData = async (hduIndex: number) => {
      if (hduIndex >= fitsObject.hdus.length || spectrumFound) {
        if (!spectrumFound && !errorMessage.value) {
          errorMessage.value = '在 FITS 文件中未找到可识别的光谱数据 (支持的 BINTABLE 或 1D IMAGE HDU)。';
        }
        loading.value = false;
        return;
      }

      const currentHdu = fitsObject.getHDU(hduIndex);
      if (!currentHdu || !currentHdu.header) {
        console.warn(`HDU at index ${hduIndex} is invalid or has no header.`);
        tryLoadHDUData(hduIndex + 1);
        return;
      }

      const header = currentHdu.header;
      const xtension = header.get('XTENSION')?.trim().toUpperCase();
      const simple = header.get('SIMPLE');
      const naxis = header.get('NAXIS');

      try {
        if (xtension === 'BINTABLE') {
          console.log(`Processing BINTABLE HDU at index ${hduIndex}`);
          const tfields = header.get('TFIELDS') || 0;
          let fluxColName: string | null = null;
          let waveColName: string | null = null;
          let waveColType: string | null = null;

          for (let i = 1; i <= tfields; i++) {
            const ttypeRaw = header.get(`TTYPE${i}`);
            if (!ttypeRaw) continue;
            const ttypeUpper = ttypeRaw.toUpperCase();
            if (ttypeUpper === 'FLUX') fluxColName = ttypeRaw;
            if (ttypeUpper === 'WAVELENGTH' || ttypeUpper === 'WAVE' || ttypeUpper === 'LOGLAM') {
              waveColName = ttypeRaw;
              waveColType = ttypeUpper;
            }
          }

          if (fluxColName) {
            currentHdu.data.getColumn(fluxColName, (fluxDataUntyped: any) => {
              if (!fluxDataUntyped || fluxDataUntyped.length === 0) {
                console.warn(`Column '${fluxColName}' in BINTABLE HDU ${hduIndex} is empty. Trying next HDU.`);
                tryLoadHDUData(hduIndex + 1);
                return;
              }
              const fluxData = Array.from(fluxDataUntyped as number[]);

              if (waveColName) {
                currentHdu.data.getColumn(waveColName, (waveDataUntyped: any) => {
                  if (!waveDataUntyped || waveDataUntyped.length === 0) {
                     console.warn(`Wavelength column '${waveColName}' is empty. Trying WCS or pixel index. HDU ${hduIndex}`);
                  } else {
                    let wavelengths = Array.from(waveDataUntyped as number[]);
                    if (waveColType === 'LOGLAM') {
                      wavelengths = wavelengths.map(loglam => Math.pow(10, loglam));
                      chartOptions.value.scales!.x!.title!.text = 'Wavelength (Angstrom - from LOGLAM)';
                    } else {
                      chartOptions.value.scales!.x!.title!.text = 'Wavelength (Angstrom)';
                    }
                    chartData.value = { labels: wavelengths.map(w => w.toFixed(2)), datasets: [{ ...chartData.value.datasets[0], data: fluxData }] };
                    spectrumFound = true;
                    loading.value = false;
                    return;
                  }
                  finalizePlotWithFlux(fluxData, header, hduIndex);
                });
              } else {
                finalizePlotWithFlux(fluxData, header, hduIndex);
              }
            });
          } else {
            console.warn(`BINTABLE HDU at index ${hduIndex} does not contain a 'FLUX' column. Trying next HDU.`);
            tryLoadHDUData(hduIndex + 1);
          }
        } else if (xtension === 'IMAGE' || (simple && naxis != null && naxis > 0 && !xtension)) {
          console.log(`Processing IMAGE HDU or Primary Image HDU at index ${hduIndex}`);
          if (naxis === 1) {
            const naxis1 = header.get('NAXIS1');
            if (!naxis1 || naxis1 === 0) {
                console.warn(`1D Image HDU at index ${hduIndex} has NAXIS1=0 or undefined. Skipping.`);
                tryLoadHDUData(hduIndex + 1);
                return;
            }
            currentHdu.data.getFrame(0, (fluxDataUntyped: any) => {
              if (!fluxDataUntyped || fluxDataUntyped.length === 0) {
                 console.warn(`1D Image HDU at index ${hduIndex} returned no data from getFrame. Trying next HDU.`);
                 tryLoadHDUData(hduIndex + 1);
                 return;
              }
              const fluxData = Array.from(fluxDataUntyped as number[]);
              finalizePlotWithFlux(fluxData, header, hduIndex, naxis1);
            });
          } else {
            console.warn(`IMAGE HDU at index ${hduIndex} is not 1D (NAXIS=${naxis}). Trying next HDU.`);
            tryLoadHDUData(hduIndex + 1);
          }
        } else if (simple && naxis === 0 && !xtension) {
          console.log(`Primary HDU at index ${hduIndex} has no data (NAXIS=0). Skipping.`);
          tryLoadHDUData(hduIndex + 1);
        } else {
          console.log(`HDU at index ${hduIndex} is not a BINTABLE or recognized IMAGE (XTENSION: ${xtension}, SIMPLE: ${simple}, NAXIS: ${naxis}). Skipping.`);
          tryLoadHDUData(hduIndex + 1);
        }
      } catch (error: any) {
        console.error(`Error processing HDU at index ${hduIndex}:`, error);
        errorMessage.value = `处理 HDU ${hduIndex} (类型: ${xtension || 'PRIMARY'}) 失败: ${error.message || error.toString()}`;
        if (!spectrumFound) tryLoadHDUData(hduIndex + 1);
        else loading.value = false;
      }
    };

    const finalizePlotWithFlux = (fluxData: number[], header: any, hduIndex: number, naxis1_img?:number) => {
        const crval1 = header.get('CRVAL1');
        const cdelt1 = header.get('CDELT1') || header.get('CD1_1');
        let crpix1 = header.get('CRPIX1');
        const dataLength = naxis1_img != null ? naxis1_img : fluxData.length;

        if (crval1 != null && cdelt1 != null && dataLength > 0) {
          crpix1 = crpix1 == null ? 1.0 : parseFloat(crpix1);
          const wavelengths = Array.from({ length: dataLength }, (_, i) => parseFloat(crval1) + (i - (crpix1 - 1)) * parseFloat(cdelt1));
          chartData.value = { labels: wavelengths.map(w => w.toFixed(2)), datasets: [{ ...chartData.value.datasets[0], data: fluxData }] };
          chartOptions.value.scales!.x!.title!.text = 'Wavelength (Angstrom - Calculated from WCS)';
        } else if (dataLength > 0) {
          chartData.value = { labels: fluxData.map((_, i) => (i + 1).toString()), datasets: [{ ...chartData.value.datasets[0], data: fluxData }] };
          chartOptions.value.scales!.x!.title!.text = 'Pixel Index';
          console.warn(`HDU ${hduIndex}: Flux data found, but no wavelength column or WCS keywords for wavelength calculation. Plotting against pixel index.`);
        } else {
          console.warn(`HDU ${hduIndex}: No valid flux data to plot.`);
          tryLoadHDUData(hduIndex + 1);
          return;
        }
        spectrumFound = true;
        loading.value = false;
    };

    tryLoadHDUData(0);
  });
};

watch(() => route.query.spectrumPath, (newPath) => {
  if (newPath && typeof newPath === 'string') {
    fetchSpectrumByPath(newPath);
  } else {
    if (isLoadedFromPath.value && !props.externalFileToLoad) {
        resetState();
        fitsFile.value = null;
    }
  }
}, { immediate: true });

watch(() => props.externalFileToLoad, (newFile) => {
  if (newFile) {
    fitsFile.value = null;
    isLoadedFromPath.value = false;
    spectrumPathFromRoute.value = null;
    resetState();
    processFitsFile(newFile);
  } else {
    if (!isLoadedFromPath.value && !fitsFile.value) {
      resetState();
    }
  }
}, { immediate: true, deep: true });

const handleFileChange = (newFile: File | null) => {
  if (newFile) {
    if (props.externalFileToLoad) {
      console.warn("Internal file selected while externalFileToLoad is also present. Prioritizing internal file.");
    }
    isLoadedFromPath.value = false;
    spectrumPathFromRoute.value = null;
    resetState();
    processFitsFile(newFile);
  } else {
    if (!isLoadedFromPath.value && !props.externalFileToLoad) {
    resetState();
    }
  }
};

const clearPathAndShowUploader = () => {
  resetState();
  fitsFile.value = null;
  isLoadedFromPath.value = false;
  spectrumPathFromRoute.value = null;
  if (props.externalFileToLoad) {
    console.warn("Clearing path to show uploader, but an external file is still provided via props. The external file will still be shown if not cleared by parent.");
  }
  $q.notify({type: 'info', message: '已清除路径加载，现在可以通过文件选择器上传。'});
};

onMounted(() => {
});

</script>

<style scoped>
.q-card {
  margin: 0 auto;
}
.q-banner {
  margin-top: 10px;
}
</style> 