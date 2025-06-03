<template>
  <q-page class="index-page q-pa-md">
    <div class="row justify-center q-mt-lg q-mb-xl">
      <div class="col-12 col-md-10 text-center">
        <h1 class="text-h3 q-mb-md">AstroYOLO 天体检测系统</h1>
        <p class="text-subtitle1 q-mb-xl text-grey-8">
          利用先进的YOLO技术，快速精准检测和定位天体目标。
        </p>
        <div class="q-gutter-md q-mb-xl">
          <q-btn 
            label="单目标检测"
            icon="photo" 
            to="/single-detection" 
            color="primary" 
            />
          <q-btn 
            label="批量检测与分析"
            icon="photo_library" 
            to="/batch-detection" 
            color="primary" 
            />
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="q-pa-md">
      <div class="text-h5 text-center q-mb-md">核心功能</div>
      <div class="row q-col-gutter-md justify-center">
        <div class="col-xs-12 col-sm-4" v-for="(feature, index) in features" :key="index">
          <q-card class="q-mb-md">
            <q-card-section>
              <div class="row items-center no-wrap">
                <div class="col-auto">
                  <q-icon :name="feature.icon" size="sm" color="primary" />
                </div>
                <div class="col">
                  <div class="text-subtitle1">{{ feature.title }}</div>
                </div>
              </div>
              <div class="text-body2 q-mt-sm text-grey-8">{{ feature.description }}</div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <!-- System Description Section -->
    <div class="q-pa-md bg-grey-1">
      <div class="row justify-center">
        <div class="col-12 col-md-10">
          <div class="text-h5 q-mb-md">系统详情</div>
          
          <q-card flat bordered>
            <q-tabs v-model="tab" class="text-grey-8 bg-white">
              <q-tab name="overview" label="系统总览" />
              <q-tab name="usage" label="使用说明" />
            </q-tabs>
            
            <q-separator />
            
            <q-tab-panels v-model="tab" animated>
              <q-tab-panel name="overview">
                <div class="text-body2">
                  AstroYOLO 是一款基于深度学习的天体目标智能检测系统。它能够实时分析天文图像，自动识别天体目标的位置和形态特征。
                  <p class="q-mt-md"><strong>论文原文链接：</strong> <a href="https://academic.oup.com/pasj/article-abstract/75/6/1311/7330817?redirectedFrom=fulltext&login=false" target="_blank" class="text-primary">AstroYOLO: Real-time Detection and Localization of Astronomical Objects</a></p>
                </div>
              </q-tab-panel>
              <q-tab-panel name="usage">
                <div class="text-body2">
                  用户可以通过上传单张天文图片或指定图片文件夹进行批量检测。系统将返回带有标注框的结果图像，并提供详细的检测报告。
                </div>
              </q-tab-panel>
            </q-tab-panels>
          </q-card>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <q-footer class="bg-white text-center q-pa-sm">
      <div>
        <p class="text-grey-8 q-mb-none text-caption">© {{ new Date().getFullYear() }} AstroYOLO 天体目标检测系统</p>
      </div>
    </q-footer>
  </q-page>
</template>

<script setup>
import { ref } from 'vue';

defineOptions({
  name: 'IndexPage'
});

const tab = ref('overview');

const features = ref([
  {
    icon: 'mdi-rocket-launch-outline',
    title: '快速目标检测',
    description: '利用优化的YOLO算法，实现对天文图像中天体目标的快速识别。'
  },
  {
    icon: 'mdi-image-filter-hdr',
    title: '高精度定位',
    description: '准确标注天体目标位置，并提供详细的置信度分析。'
  },
  {
    icon: 'mdi-chart-areaspline',
    title: '结果可视化',
    description: '直观展示检测结果，支持批量处理和数据导出，便于进一步分析。'
  }
]);

</script>

<style>
/* 简化的样式 */
</style>
