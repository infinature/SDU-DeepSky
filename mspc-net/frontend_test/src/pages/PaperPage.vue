<template>
  <div class="q-pa-md column full-height" style="gap: 20px">
    <!-- 标题区域 -->
    <div class="q-mb-md">
      <div class="text-h4 text-weight-bold text-primary flex items-center">
        <q-icon name="article" class="q-mr-sm" />
        论文展示
        <div class="q-ml-md text-h6 text-grey-6">Astronomical Spectra Classification</div>
      </div>
      <div class="text-caption text-grey-7 q-mt-sm flex items-center q-gutter-sm">
        <q-badge
          color="blue"
          label="Multiscale Partial Convolution"
          class="q-px-sm q-py-xs"
          style="border-radius: 4px"
        />
        <div class="flex items-center">
          <q-icon name="description" size="16px" class="q-mr-xs" />
          <span class="text-weight-medium">Wu_2024_AJ_167_260.pdf</span>
          <q-chip
            size="8px"
            color="green-1"
            text-color="green-8"
            class="q-ml-sm"
            icon="verified"
          >
            Peer Reviewed
          </q-chip>
        </div>
      </div>
    </div>

    <!-- 主内容卡片 -->
    <q-card class="column full-height bg-white shadow-5" style="border-radius: 12px">
      <!-- 顶部控制栏 -->
      <q-bar class="bg-grey-2 q-px-md" style="height: 48px">
        <div class="row items-center q-gutter-xs">
          <div class="window-btn bg-red" @click="hasError = true"></div>
          <div class="window-btn bg-yellow"></div>
          <div class="window-btn bg-green"></div>
        </div>
        <q-space />
        <q-btn
          dense
          unelevated
          icon="download"
          label="下载论文"
          @click="downloadPaper"
          class="bg-primary text-white q-px-md"
          style="border-radius: 8px"
        />
      </q-bar>

      <!-- PDF 显示区域 -->
      <div class="relative-position full-height" style="flex: 1 1 auto">
        <!-- 加载动画 -->
        <transition name="fade">
          <div
            v-if="isLoading"
            class="absolute-full flex flex-center bg-grey-1 z-max column"
            style="gap: 12px"
          >
            <q-spinner-gears size="40px" color="primary" />
            <div class="text-grey-7">正在加载论文内容...</div>
          </div>
        </transition>

        <!-- 加载错误 -->
        <transition name="fade">
          <div
            v-if="hasError"
            class="absolute-full flex flex-center bg-red-1 text-negative z-max column"
            style="gap: 16px"
          >
            <q-icon name="error_outline" size="40px" />
            <div class="text-center">
              <div>论文加载失败</div>
              <div class="text-caption q-mt-xs">请检查网络连接或文件路径</div>
            </div>
            <q-btn
              label="重试加载"
              unelevated
              color="negative"
              @click="handleRetry"
            />
          </div>
        </transition>

        <!-- PDF iframe -->
        <iframe
          src="/Wu_2024_AJ_167_260.pdf"
          class="full-width full-height"
          @load="handleLoad"
          @error="handleError"
          title="论文"
          style="min-height: 600px"
        />
      </div>

      <!-- 底部翻页栏 -->
      <div class="bg-grey-1 q-pa-sm row justify-between items-center border-top-grey">
        <div class="q-gutter-sm">
          <q-btn
            flat
            dense
            icon="chevron_left"
            label="上一页"
            class="btn-pagination"
          />
          <q-btn
            flat
            dense
            icon-right="chevron_right"
            label="下一页"
            class="btn-pagination"
          />
        </div>
        <div class="flex items-center text-grey-7">
          <q-icon name="info" size="16px" class="q-mr-xs" />
          <span>建议使用 Chrome 浏览器获得最佳体验</span>
        </div>
      </div>
    </q-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const isLoading = ref(true)
const hasError = ref(false)

const handleLoad = () => {
  isLoading.value = false
  hasError.value = false
}

const handleError = () => {
  isLoading.value = false
  hasError.value = true
}

const handleRetry = () => {
  isLoading.value = true
  hasError.value = false
  // 这里可以添加重新加载的逻辑
}

const downloadPaper = () => {
  const link = document.createElement('a')
  link.href = '/Wu_2024_AJ_167_260.pdf'
  link.download = 'Wu_2024_AJ_167_260.pdf'
  link.click()
}
</script>

<style scoped>
.window-btn {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s;
}

.window-btn:hover {
  transform: scale(1.1);
}

.btn-pagination {
  border-radius: 6px;
  transition: all 0.3s;
}

.btn-pagination:hover {
  background: rgba(0, 89, 255, 0.1);
  color: var(--q-primary);
}

.border-top-grey {
  border-top: 1px solid rgba(0, 0, 0, 0.12);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

iframe {
  border: none;
  background: white;
}
</style>
