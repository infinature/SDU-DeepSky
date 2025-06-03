<template>
  <q-page class="row items-center justify-evenly">
    <div class="text-center">
      <h1 class="text-h3">M-Star 分类系统</h1>
      <p class="text-subtitle1">欢迎使用基于光谱和图像数据的M型星分类工具。</p>
      <div class="q-my-md">
        <p>
          GitHub 仓库:
          <a href="https://github.com/qintianjian-lab/2025-undergrad-astro-frontend" target="_blank">https://github.com/qintianjian-lab/2025-undergrad-astro-frontend</a>
        </p>
        <p>
          相关论文:
          <a href="https://iopscience.iop.org/article/10.1088/1538-3873/acc7ca" target="_blank">https://iopscience.iop.org/article/10.1088/1538-3873/acc7ca</a>
        </p>
      </div>
      <q-btn color="primary" label="开始探索" to="/data" />
    </div>
  </q-page>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'IndexPage',
});
</script> 