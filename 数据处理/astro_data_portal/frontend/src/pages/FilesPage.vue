<template>
  <div class="timeline-bg">
    <div class="timeline-container single">
      <div class="timeline-content">
        <div class="timeline-card timeline-detail-card">
          <q-btn flat color="primary" icon="arrow_back" label="返回导航页" class="q-mb-md" @click="returnToNavigationPortal" />
          <div class="timeline-title text-h5 q-mb-md">下载文件管理器</div>
          <div class="timeline-desc q-mb-lg">查看和下载已处理的天文数据文件</div>

          <!-- 目录导航 -->
          <q-breadcrumbs class="q-mb-md">
            <q-breadcrumbs-el label="根目录" icon="home" @click="navigateTo('')" />
            <template v-for="(folder, index) in pathParts" :key="index">
              <q-breadcrumbs-el 
                :label="folder" 
                @click="navigateTo(pathParts.slice(0, index + 1).join('/'))" 
              />
            </template>
          </q-breadcrumbs>

          <!-- 文件列表 -->
          <q-card>
            <q-card-section>
              <q-table
                :rows="files"
                :columns="columns"
                row-key="name"
                :loading="loading"
                :pagination="{ rowsPerPage: 0 }"
                flat
                bordered
              >
                <template v-slot:body="props">
                  <q-tr :props="props">
                    <q-td key="name" :props="props">
                      <q-item clickable v-ripple @click="handleItemClick(props.row)">
                        <q-item-section avatar>
                          <q-icon :name="props.row.is_dir ? 'folder' : 'insert_drive_file'" :color="props.row.is_dir ? 'amber' : 'grey'" />
                        </q-item-section>
                        <q-item-section>{{ props.row.name }}</q-item-section>
                      </q-item>
                    </q-td>
                    <q-td key="size" :props="props">{{ props.row.is_dir ? '-' : props.row.size_formatted }}</q-td>
                    <q-td key="modified" :props="props">{{ props.row.modified }}</q-td>
                    <q-td key="actions" :props="props" class="text-right">
                      <q-btn
                        v-if="!props.row.is_dir"
                        flat
                        round
                        dense
                        icon="cloud_download"
                        color="primary"
                        @click="downloadFile(props.row)"
                      >
                        <q-tooltip>下载</q-tooltip>
                      </q-btn>
                    </q-td>
                  </q-tr>
                </template>

                <template v-slot:no-data>
                  <div class="full-width row flex-center q-pa-md text-grey">
                    <div v-if="loading">正在加载...</div>
                    <div v-else>此目录没有文件</div>
                  </div>
                </template>
              </q-table>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'

export default defineComponent({
  name: 'FilesPage',
  
  setup() {
    const $q = useQuasar()
    
    const loading = ref(false)
    const files = ref([])
    const currentDirectory = ref('')
    
    const columns = [
      { name: 'name', label: '名称', field: 'name', align: 'left' },
      { name: 'size', label: '大小', field: 'size_formatted', align: 'left' },
      { name: 'modified', label: '修改时间', field: 'modified', align: 'left' },
      { name: 'actions', label: '操作', field: 'actions', align: 'center' }
    ]
    
    const pathParts = computed(() => {
      if (!currentDirectory.value) return []
      return currentDirectory.value.split('/')
    })
    
    const navigateTo = async (path) => {
      currentDirectory.value = path
      await loadFiles()
    }
    
    const loadFiles = async () => {
      loading.value = true
      try {
        const response = await fetch(`http://localhost:5003/api/files?subdir=${encodeURIComponent(currentDirectory.value)}`)
        const data = await response.json()
        
        if (data.status === 'success') {
          files.value = data.items
        } else {
          throw new Error(data.message || '加载文件失败')
        }
      } catch (error) {
        $q.notify({
          color: 'negative',
          message: `错误: ${error.message}`,
          icon: 'error'
        })
      } finally {
        loading.value = false
      }
    }
    
    const handleItemClick = (item) => {
      if (item.is_dir) {
        navigateTo(item.path)
      } else {
        downloadFile(item)
      }
    }
    
    const downloadFile = (file) => {
      // 创建一个隐藏的a标签，用于触发浏览器下载
      const link = document.createElement('a')
      link.href = `http://localhost:5003/api/download/${encodeURIComponent(file.path)}`
      link.download = file.name
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      $q.notify({
        color: 'positive',
        message: `开始下载: ${file.name}`,
        icon: 'cloud_download'
      })
    }
    
    const returnToNavigationPortal = () => {
      window.location.href = 'http://localhost:8000/'
    }
    
    onMounted(() => {
      loadFiles()
    })
    
    return {
      loading,
      files,
      columns,
      currentDirectory,
      pathParts,
      navigateTo,
      handleItemClick,
      downloadFile,
      returnToNavigationPortal
    }
  }
})
</script>

<style scoped>
.timeline-bg {
  min-height: 100vh;
  background: #0a0a23;
  padding-top: 60px;
}
.timeline-container.single {
  display: flex;
  flex-direction: row;
  max-width: 900px;
  margin: 0 auto;
  position: relative;
}
.timeline-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 40px;
  margin-left: 0;
}
.timeline-card.timeline-detail-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 16px rgba(160, 132, 232, 0.08);
  padding: 32px 40px;
  margin-bottom: 20px;
  position: relative;
}
.timeline-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 10px;
}
.timeline-desc {
  color: #333;
  font-size: 1rem;
  margin-bottom: 18px;
}
</style>
