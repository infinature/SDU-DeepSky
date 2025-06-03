<template>
  <div class="timeline-bg">
    <div class="timeline-container single">
      <div class="timeline-content">
        <div class="timeline-card timeline-detail-card">
          <q-btn flat color="deep-purple-6" icon="arrow_back" label="返回导航页" class="q-mb-lg nav-btn" @click="returnToNavigationPortal" />
          <div class="timeline-title text-h4 q-mb-md">下载文件管理器</div>
          <div class="timeline-desc q-mb-xl">查看和下载已处理的天文数据文件</div>

          <!-- 目录导航 -->
          <div class="breadcrumbs-wrapper q-mb-xl">
            <q-card class="breadcrumb-card">
              <q-card-section class="q-pa-md">
                <div class="form-section-title q-mb-md">当前位置</div>
                <q-breadcrumbs class="breadcrumbs-custom">
                  <q-breadcrumbs-el label="根目录" icon="home" @click="navigateTo('')" />
                  <template v-for="(folder, index) in pathParts" :key="index">
                    <q-breadcrumbs-el
                      :label="folder"
                      @click="navigateTo(pathParts.slice(0, index + 1).join('/'))"
                    />
                  </template>
                </q-breadcrumbs>
              </q-card-section>
            </q-card>
          </div>

          <!-- 文件列表 -->
          <q-card class="files-card">
            <q-card-section class="q-pa-none">
              <div class="form-section-title q-pa-lg">文件列表</div>
              <q-separator color="deep-purple-2" />
              <q-table
                :rows="files"
                :columns="columns"
                row-key="name"
                :loading="loading"
                :pagination="{ rowsPerPage: 0 }"
                flat
                bordered
                class="files-table"
              >
                <template v-slot:body="props">
                  <q-tr :props="props" class="file-row">
                    <q-td key="name" :props="props" class="file-name-cell">
                      <q-item clickable v-ripple @click="handleItemClick(props.row)" class="file-item">
                        <q-item-section avatar>
                          <q-icon
                            :name="props.row.is_dir ? 'folder' : getFileIcon(props.row.name)"
                            :color="props.row.is_dir ? 'deep-purple-6' : 'blue-grey-6'"
                            size="md"
                          />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label class="file-name">{{ props.row.name }}</q-item-label>
                          <q-item-label caption v-if="!props.row.is_dir" class="file-path">
                            {{ props.row.path }}
                          </q-item-label>
                        </q-item-section>
                      </q-item>
                    </q-td>
                    <q-td key="size" :props="props" class="size-cell">
                      <span v-if="!props.row.is_dir" class="file-size">{{ props.row.size_formatted }}</span>
                      <span v-else class="folder-indicator">—</span>
                    </q-td>
                    <q-td key="modified" :props="props" class="date-cell">
                      <span class="modified-date">{{ props.row.modified }}</span>
                    </q-td>
                    <q-td key="actions" :props="props" class="actions-cell">
                      <q-btn
                        v-if="!props.row.is_dir"
                        flat
                        round
                        dense
                        icon="cloud_download"
                        color="deep-purple-6"
                        @click.stop="downloadFile(props.row)"
                        class="download-file-btn"
                      >
                        <q-tooltip>下载文件</q-tooltip>
                      </q-btn>
                    </q-td>
                  </q-tr>
                </template>

                <template v-slot:no-data>
                  <div class="full-width row flex-center q-pa-xl text-grey-6">
                    <div class="text-center">
                      <q-icon name="folder_open" size="4rem" class="q-mb-md" color="grey-4" />
                      <div class="text-h6 q-mb-sm">此目录没有文件</div>
                      <div class="text-body2">文件夹为空或正在加载</div>
                    </div>
                  </div>
                </template>

                <template v-slot:loading>
                  <div class="full-width row flex-center q-pa-xl">
                    <q-spinner-dots color="deep-purple-6" size="3rem" />
                    <span class="q-ml-md text-h6">正在加载...</span>
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
      { name: 'name', label: '名称', field: 'name', align: 'left', style: 'width: 50%' },
      { name: 'size', label: '大小', field: 'size_formatted', align: 'left', style: 'width: 15%' },
      { name: 'modified', label: '修改时间', field: 'modified', align: 'left', style: 'width: 25%' },
      { name: 'actions', label: '操作', field: 'actions', align: 'center', style: 'width: 10%' }
    ]

    const pathParts = computed(() => {
      if (!currentDirectory.value) return []
      return currentDirectory.value.split('/')
    })

    const getFileIcon = (fileName) => {
      const extension = fileName.split('.').pop().toLowerCase()
      const iconMap = {
        'fits': 'image',
        'fit': 'image',
        'png': 'image',
        'jpg': 'image',
        'jpeg': 'image',
        'gif': 'image',
        'csv': 'table_chart',
        'txt': 'description',
        'log': 'list_alt',
        'zip': 'archive',
        'tar': 'archive',
        'gz': 'archive'
      }
      return iconMap[extension] || 'insert_drive_file'
    }

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
          icon: 'error',
          position: 'top'
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
        icon: 'cloud_download',
        position: 'top'
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
      returnToNavigationPortal,
      getFileIcon
    }
  }
})
</script>

<style scoped>
.timeline-bg {
  min-height: 100vh;
  background: linear-gradient(120deg, #e0e7ff 0%, #ede9fe 100%);
  padding-top: 32px;
}
.timeline-container.single {
  display: flex;
  flex-direction: row;
  max-width: 96vw;
  margin: 32px auto;
  position: relative;
  padding: 16px 0;
}
.timeline-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 48px;
  margin-left: 0;
}
.timeline-card.timeline-detail-card {
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 4px 32px rgba(120, 87, 255, 0.12);
  padding: 48px 56px 40px 56px;
  margin-bottom: 20px;
  position: relative;
  transition: box-shadow 0.2s, transform 0.2s;
}
.timeline-card.timeline-detail-card:hover {
  box-shadow: 0 8px 48px rgba(120, 87, 255, 0.18);
  transform: translateY(-4px) scale(1.01);
}
.timeline-title {
  font-size: 2.2rem;
  font-weight: bold;
  margin-bottom: 18px;
  color: #5b21b6;
  letter-spacing: 1px;
}
.timeline-desc {
  color: #444;
  font-size: 1.15rem;
  margin-bottom: 28px;
  line-height: 1.7;
}
.breadcrumb-card, .files-card {
  border-radius: 16px;
  box-shadow: 0 2px 16px rgba(120, 87, 255, 0.08);
  border: none;
}
.breadcrumbs-custom .q-breadcrumbs__el {
  color: #7c3aed;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
}
.breadcrumbs-custom .q-breadcrumbs__el:hover {
  color: #5b21b6;
  transform: translateY(-1px);
}
.nav-btn {
  font-size: 1.1rem;
  font-weight: bold;
  border-radius: 10px;
  padding: 0 20px;
  min-width: 120px;
  letter-spacing: 1px;
}
.files-table {
  border-radius: 12px;
  overflow: hidden;
  font-size: 1.05rem;
}
.files-table .q-table th {
  background: #ede9fe;
  color: #5b21b6;
  font-weight: bold;
  font-size: 1.08rem;
}
.files-table .q-table td {
  font-size: 1.05rem;
}
.form-section-title {
  font-size: 1.18rem;
  font-weight: bold;
  color: #7c3aed;
  margin-bottom: 8px;
  margin-top: 8px;
  letter-spacing: 1px;
}
.file-row {
  transition: all 0.3s ease;
}
.file-row:hover {
  background: rgba(120, 87, 255, 0.05);
}
.file-item {
  padding: 8px 0;
  border-radius: 8px;
  transition: all 0.3s ease;
}
.file-item:hover {
  background: rgba(120, 87, 255, 0.08);
}
.file-name {
  font-weight: 500;
  color: #2d3748;
}
.file-path {
  color: #718096;
  font-size: 0.85rem;
}
.file-size {
  font-weight: 500;
  color: #4a5568;
  background: rgba(120, 87, 255, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.85rem;
}
.folder-indicator {
  color: #a0aec0;
  font-size: 1.2rem;
}
.modified-date {
  color: #718096;
  font-size: 0.9rem;
}
.download-file-btn {
  transition: all 0.3s ease;
}
.download-file-btn:hover {
  transform: translateY(-2px) scale(1.1);
  box-shadow: 0 4px 15px rgba(120, 87, 255, 0.4);
}
@media (max-width: 1024px) {
  .timeline-card.timeline-detail-card {
    padding: 24px 8px 24px 8px;
  }
  .timeline-container.single {
    max-width: 98vw;
    padding: 0;
  }
}
@media (max-width: 768px) {
  .timeline-card.timeline-detail-card {
    padding: 12px 2vw 12px 2vw;
  }
  .file-name-cell {
    max-width: 200px;
  }
  .file-name {
    font-size: 0.9rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>
