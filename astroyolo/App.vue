<template>
  <router-view />
</template>

<script setup>
// 直接在全局样式中处理
</script>

<style>
/* 全局样式覆盖 - 强力覆盖所有黑色背景 */
.q-table,
.q-table__container,
.q-table__middle,
.q-table__bottom,
.q-table__control,
.q-table thead,
.q-table tbody,
.q-table td,
.q-table th,
.q-table tr,
.q-table__grid-content,
body .q-table__container,
body .q-table thead,
body .q-table tbody tr, 
body .q-table tr, 
body .q-table th, 
body .q-table td,
body [class*="q-table"],
body tr[class*="q-tr"],
body td[class*="q-td"],
body th[class*="q-th"] {
  background-color: #ffffff !important;
  color: #333333 !important;
}

/* 表头样式 */
body .q-table th,
body th[class*="q-th"],
body .q-table thead,
body .q-table thead tr {
  background-color: #f0f4f8 !important;
  color: #133665 !important;
  font-weight: 600 !important;
}

/* 覆盖所有深色组件 */
body .q-dark,
body [class*="bg-"],
body .q-menu,
body .q-dark,
body .bg-dark,
body .bg-black,
body [style*="background-color: rgb(33, 33, 33)"],
body [style*="background-color: #212121"],
body [style*="background-color: black"],
body [style*="background-color: #000"],
body .q-field__native,
body .q-field__input,
body input,
body .q-chip {
  background-color: #ffffff !important;
  color: #333333 !important;
}

/* 保留特定颜色 */
body .bg-blue-1,
body .bg-green-1,
body .bg-purple-1,
body .bg-orange-1,
body .bg-white {
  background-color: inherit !important;
}

/* 添加更多的选择器来覆盖结果页面的任何黑色区域 */
body .q-page[data-v-*],
body .q-page > div,
body .q-page .q-card,
body .q-page .q-table,
body .q-card__section,
body .q-tooltip,
body .q-menu,
body .q-field__control {
  background-color: #ffffff !important;
  color: #333333 !important;
}

/* 解决常见的黑色表格行问题 */
body tbody,
body tbody tr,
body tbody td,
body .q-table__bottom {
  background-color: #ffffff !important;
  color: #333333 !important;
  border-color: #e0e0e0 !important;
}

/* 按钮和复选框 */
body .q-checkbox__inner {
  color: #1976d2 !important;
}
</style>
