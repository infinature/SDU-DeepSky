<template>
  <router-view />
</template>

<script setup>
// 使用light-mc.css的配色方案
</script>

<style>
/* 使用light-mc.css的整体配色方案 */
:root {
  /* 直接买入light-mc.css的变量类 */
  --md-sys-color-primary: rgb(19, 54, 101);
  --md-sys-color-surface-tint: rgb(65, 95, 145);
  --md-sys-color-on-primary: rgb(255, 255, 255);
  --md-sys-color-primary-container: rgb(80, 109, 160);
  --md-sys-color-on-primary-container: rgb(255, 255, 255);
  --md-sys-color-secondary: rgb(46, 54, 71);
  --md-sys-color-on-secondary: rgb(255, 255, 255);
  --md-sys-color-secondary-container: rgb(100, 109, 128);
  --md-sys-color-on-secondary-container: rgb(255, 255, 255);
  --md-sys-color-tertiary: rgb(69, 46, 74);
  --md-sys-color-on-tertiary: rgb(255, 255, 255);
  --md-sys-color-tertiary-container: rgb(127, 100, 132);
  --md-sys-color-on-tertiary-container: rgb(255, 255, 255);
  --md-sys-color-error: rgb(116, 0, 6);
  --md-sys-color-on-error: rgb(255, 255, 255);
  --md-sys-color-error-container: rgb(207, 44, 39);
  --md-sys-color-on-error-container: rgb(255, 255, 255);
  --md-sys-color-background: rgb(249, 249, 255);
  --md-sys-color-on-background: rgb(25, 28, 32);
  --md-sys-color-surface: rgb(249, 249, 255);
  --md-sys-color-on-surface: rgb(15, 17, 22);
  --md-sys-color-surface-variant: rgb(224, 226, 236);
  --md-sys-color-on-surface-variant: rgb(51, 54, 62);
  --md-sys-color-outline: rgb(79, 82, 90);
  --md-sys-color-outline-variant: rgb(106, 109, 117);
  --md-sys-color-shadow: rgb(0, 0, 0);
  --md-sys-color-scrim: rgb(0, 0, 0);
  --md-sys-color-inverse-surface: rgb(46, 48, 54);
  --md-sys-color-inverse-on-surface: rgb(240, 240, 247);
  --md-sys-color-inverse-primary: rgb(170, 199, 255);
  --md-sys-color-surface-dim: rgb(197, 198, 205);
  --md-sys-color-surface-bright: rgb(249, 249, 255);
  --md-sys-color-surface-container-lowest: rgb(255, 255, 255);
  --md-sys-color-surface-container-low: rgb(243, 243, 250);
  --md-sys-color-surface-container: rgb(231, 232, 238);
  --md-sys-color-surface-container-high: rgb(220, 220, 227);
  --md-sys-color-surface-container-highest: rgb(209, 209, 216);
}

/* 全局样式定义 - 所有组件共享 */
body {
  background-color: var(--md-sys-color-background);
  color: var(--md-sys-color-on-background);
  font-family: 'Rajdhani', sans-serif;
}

/* 表格样式统一 */
.q-table {
  background-color: var(--md-sys-color-surface-container-lowest) !important;
  color: var(--md-sys-color-on-background) !important;
}

/* 表头样式 */
.q-table thead tr,
.q-table thead th {
  background-color: var(--md-sys-color-surface-container-low) !important;
  color: var(--md-sys-color-primary) !important;
  font-weight: 600 !important;
}

/* 表格行样式 */
.q-table tbody tr {
  background-color: var(--md-sys-color-surface-container-lowest) !important;
  color: var(--md-sys-color-on-background) !important;
}

/* 表格单元格样式 */
.q-table td {
  color: var(--md-sys-color-on-background) !important;
}

/* 卡片样式 */
.q-card {
  background-color: var(--md-sys-color-surface-container-lowest) !important;
  color: var(--md-sys-color-on-background) !important;
}

/* 输入框样式 */
.q-field__control,
.q-field__native,
.q-field__input {
  background-color: var(--md-sys-color-surface-container-lowest) !important;
  color: var(--md-sys-color-on-background) !important;
}

/* 允许自定义颜色类生效 */
[class*="bg-astroyolo-"],
[class*="text-astroyolo-"],
[class*="border-astroyolo-"] {
  background-color: inherit;
  color: inherit;
  border-color: inherit;
}

/* 复选框和单选框颜色 */
.q-checkbox__inner {
  color: var(--md-sys-color-primary) !important;
}

/* 下拉菜单和弹出框 */
.q-menu {
  background-color: var(--md-sys-color-surface-container-lowest) !important;
  color: var(--md-sys-color-on-background) !important;
}
</style>
