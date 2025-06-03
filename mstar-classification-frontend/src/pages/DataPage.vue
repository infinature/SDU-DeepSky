<template>
  <q-page padding>
    <h4 class="q-my-md">数据管理</h4>
    <p>这里将展示和管理光谱及图像数据。</p>
    <!-- 表格、筛选、上传等功能占位 -->
    <q-table
      title="恒星数据"
      :rows="rows"
      :columns="columns"
      row-key="name"
    />
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

const columns = [
  { name: 'name', required: true, label: '名称', align: 'left', field: (row: { name: string; }) => row.name, sortable: true },
  { name: 'ra', align: 'center', label: '赤经 (RA)', field: 'ra', sortable: true },
  { name: 'dec', label: '赤纬 (Dec)', field: 'dec', sortable: true },
  { name: 'type', label: '类型', field: 'type', sortable: true },
  { name: 'actions', label: '操作', field: 'actions' }
];

const sampleRows = [
  { name: 'SDSS J000001.00+000001.0', ra: '00:00:01.00', dec: '+00:00:01.0', type: 'M2' },
  { name: 'SDSS J000002.00+000002.0', ra: '00:00:02.00', dec: '+00:00:02.0', type: 'M5' },
];

export default defineComponent({
  name: 'DataPage',
  setup() {
    return {
      columns,
      rows: ref(sampleRows)
    };
  },
});
</script> 