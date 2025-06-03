<template>
  <q-page padding>
    <h4 class="q-my-md">光谱可视化</h4>
    <p class="text-subtitle1">在此处上传并查看 FITS 光谱文件的内容。</p>

    <div class="q-mt-lg">
      <spectrum-visualizer />
    </div>

    <!-- 图像可视化部分可以稍后添加或保留 -->
    <!-- 
    <h4 class="q-my-lg">图像查看</h4>
    <div class="row q-col-gutter-md">
      <div class="col-12 col-md-6">
        <q-card>
          <q-card-section>
            <div class="text-h6">图像</div>
          </q-card-section>
          <q-card-section>
            <q-img src="https://cdn.quasar.dev/img/parallax2.jpg" style="height: 300px;">
              <div class="absolute-bottom text-subtitle1 text-center">
                图像区域 (待实现)
              </div>
            </q-img>
          </q-card-section>
        </q-card>
      </div>
    </div>
    -->
  </q-page>
</template>

<script lang="ts" setup>
// 使用 <script setup> 语法，更简洁
import SpectrumVisualizer from 'src/components/SpectrumVisualizer.vue';

// 如果将来需要其他 setup 逻辑，可以在这里添加
</script>

<style scoped>
/* Page specific styles if needed */
</style> 