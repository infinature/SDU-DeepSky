<template>
  <Bar :data="chartData" :options="chartOptions" style="height: 400px;" />
</template>

<script lang="ts">
import { defineComponent, PropType, computed } from 'vue';
import { Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  type ChartData,
  type ChartOptions
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

interface ProbabilityItem {
  class_name: string;
  probability: number;
}

export default defineComponent({
  name: 'ProbabilityBarChart',
  components: {
    Bar,
  },
  props: {
    probabilities: {
      type: Array as PropType<ProbabilityItem[]>,
      required: true,
    },
    titleText: {
        type: String,
        default: '预测概率分布'
    }
  },
  setup(props) {
    const chartData = computed(() => ({
      labels: props.probabilities.map(p => p.class_name),
      datasets: [
        {
          label: '概率 (%)',
          backgroundColor: '#42A5F5', // Quasar primary color or similar
          data: props.probabilities.map(p => p.probability),
          borderColor: '#1E88E5',
          borderWidth: 1,
        },
      ],
    } as ChartData<"bar">));

    const chartOptions = computed(() => ({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false, // 通常单个数据集不需要图例
        },
        title: {
          display: true,
          text: props.titleText,
        },
        tooltip: {
            callbacks: {
                label: function(context) {
                    let label = context.dataset.label || '';
                    if (label) {
                        label += ': ';
                    }
                    if (context.parsed.y !== null) {
                        label += context.parsed.y.toFixed(2) + '%';
                    }
                    return label;
                }
            }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100, // 概率最大为100%
          title: {
            display: true,
            text: '概率 (%)'
          }
        },
        x: {
            title: {
                display: true,
                text: '恒星类别'
            }
        }
      },
    } as ChartOptions<"bar">));

    return {
      chartData,
      chartOptions,
    };
  },
});
</script>

<style scoped>
/* Add any specific styles for your chart component here if needed */
</style> 