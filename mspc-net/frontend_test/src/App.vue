<template>
  <router-view v-slot="{ Component }">
    <transition name="fade" mode="out-in">
      <component :is="Component" />
    </transition>
  </router-view>
</template>

<script setup>
// 组件逻辑已移至 MainLayout.vue
</script>

<style>
/* 引入主题变量，可删除 */
@import 'css/light-theme.css';
/* 注意这个可以修改的，可删除，和上面搭配使用 */
:root {
  /* Material Design 3 颜色系统 */
  --md-sys-color-primary: #4a90e2;
  --md-sys-color-primary-rgb: 74, 144, 226;
  --md-sys-color-secondary: rgb(69 46 74);
  --md-sys-color-secondary-rgb: 80, 227, 194;
  --md-sys-color-surface: #ffffff;
  --md-sys-color-surface-rgb: 255, 255, 255;
  --md-sys-color-background: #f6f9fc;
  --md-sys-color-background-rgb: 246, 249, 252;

  /* 动画延迟 */
  --delay-1: 0.1s;
  --delay-2: 0.2s;
  --delay-3: 0.3s;
  --delay-4: 0.4s;
  --delay-5: 0.5s;
}

/* 全局过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 全局样式 */
body {
  margin: 0;
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans',
    'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 提取常用主题变量做别名映射 */
.bg-surface {
  background-color: var(--md-sys-color-surface) !important;
}

.bg-surface-container {
  background-color: var(--md-sys-color-surface-container) !important;
}

.text-on-surface {
  color: var(--md-sys-color-on-surface) !important;
}

.bg-primary {
  background-color: var(--md-sys-color-primary) !important;
}

.text-on-primary {
  color: var(--md-sys-color-on-primary) !important;
}
</style>
