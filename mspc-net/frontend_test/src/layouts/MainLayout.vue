<template>
  <q-layout view="hHh Lpr fFf" class="light-medium-contrast bg-surface text-on-surface">
    <!-- 顶部导航栏 -->
    <q-header elevated class="bg-primary text-on-primary header-transition">
      <q-toolbar class="toolbar-container">
        <q-btn
          flat
          dense
          round
          :icon="drawer ? 'menu_open' : 'menu'"
          @click="drawer = !drawer"
          class="q-mr-sm menu-btn"
        />
        <q-toolbar-title class="text-h6 text-weight-bold">
          <div class="row items-center">
            <div class="logo-wrapper">
              <q-icon name="science" size="2rem" class="logo-icon" />
            </div>
            <span class="platform-title">MSPC-Net 综合平台</span>
          </div>
        </q-toolbar-title>
        <div class="header-actions">
          <q-btn flat round dense icon="notifications" class="action-btn">
            <q-badge color="red" floating>2</q-badge>
            <q-tooltip>通知中心</q-tooltip>
          </q-btn>
          <q-btn flat round dense icon="help" class="action-btn">
            <q-tooltip>帮助中心</q-tooltip>
          </q-btn>
          <q-btn flat round dense icon="person" class="action-btn">
            <q-tooltip>个人中心</q-tooltip>
          </q-btn>
        </div>
      </q-toolbar>
    </q-header>

    <!-- 左侧导航抽屉 -->
    <q-drawer
      v-model="drawer"
      show-if-above
      side="left"
      bordered
      width="260"
      class="bg-surface-container text-on-surface drawer-transition"
    >
      <div class="drawer-header">
        <div class="text-h5 font-bold flex items-center">
          <span class="brand-name">🌌 MSPC-Net</span>
          <q-icon name="verified" size="sm" class="q-ml-sm text-positive" />
        </div>
        <div class="text-caption sidebar-subtitle">多光谱星型分类平台</div>
      </div>
      <q-list padding class="menu-list">
        <q-item
          v-for="item in menuItems"
          :key="item.path || item.title"
          :to="item.path"
          clickable
          v-ripple
          class="menu-item"
          :class="{ 'menu-item-active': $route.path === item.path }"
          @click="item.action"
        >
          <q-item-section avatar>
            <q-icon :name="item.icon" class="menu-icon" />
          </q-item-section>
          <q-item-section>
            <div class="menu-item-content">
              <div class="menu-title">{{ item.title }}</div>
              <div class="menu-description">{{ item.description }}</div>
            </div>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <!-- 页面主体容器 -->
    <q-page-container>
      <div class="page-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="page-transition" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </q-page-container>

    <!-- 页脚 -->
    <q-footer elevated class="bg-surface-container text-on-surface">
      <q-toolbar>
        <q-toolbar-title class="text-caption text-center">
          <div class="footer-content">
            <span>© 2025 MSPC-Net. All rights reserved.</span>
            <span class="footer-divider">|</span>
            <span>Version 2.0</span>
          </div>
        </q-toolbar-title>
      </q-toolbar>
    </q-footer>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'

const drawer = ref(true)

const menuItems = [
  {
    title: '模型训练',
    icon: 'science',
    path: '/main/test',
    description: '模型测试与验证',
  },
  {
    title: '论文查看',
    icon: 'article',
    path: '/main/paper',
    description: '相关论文研究',
  },
  {
    title: '模型预测',
    icon: 'analytics',
    path: '/main/predict',
    description: '智能预测分析',
  },
  {
    title: '代码仓库',
    icon: 'code',
    description: '访问项目源码',
    action: () => {
      window.open('https://github.com/qintianjian-lab/MSPC-Net', '_blank')
    },
  },
  {
    title: '返回导航门户',
    icon: 'exit_to_app',
    description: '访问主导航页面',
    action: () => {
      window.location.href = 'http://localhost:8000/';
    },
  },
]
</script>

<style scoped>
.toolbar-container {
  padding: 0.5rem 1rem;
  background: linear-gradient(45deg, var(--md-sys-color-primary), var(--md-sys-color-secondary));
}

.logo-wrapper {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 0.5rem;
  margin-right: 1rem;
  transition: all 0.3s ease;
}

.logo-wrapper:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(15deg);
}

.platform-title {
  font-size: 1.4rem;
  letter-spacing: 0.5px;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.drawer-header {
  padding: 1rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  background: var(--md-sys-color-surface-container-high);
}

.drawer-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  text-align: center;
}

.menu-list {
  padding: 0.5rem;
}

.menu-item {
  margin: 0.3rem 0;
  border-radius: 8px;
  transition: all 0.3s ease;
  padding: 0.5rem;
}

.menu-item:hover {
  background: var(--md-sys-color-surface-container-high);
  transform: translateX(5px);
}

.menu-item-active {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
}

.menu-icon {
  font-size: 1.2rem;
  transition: all 0.3s ease;
}

.menu-item:hover .menu-icon {
  transform: scale(1.1);
}

.menu-item-content {
  display: flex;
  flex-direction: column;
}

.menu-title {
  font-weight: 500;
  font-size: 0.95rem;
}

.menu-description {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 0.1rem;
}

.page-wrapper {
  padding: 2rem;
  min-height: calc(100vh - 130px);
}

.page-transition-enter-active,
.page-transition-leave-active {
  transition: all 0.3s ease;
}

.page-transition-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.page-transition-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.footer-content {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.footer-divider {
  opacity: 0.5;
}

/* 自定义滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--md-sys-color-surface-container);
}

::-webkit-scrollbar-thumb {
  background: var(--md-sys-color-outline-variant);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--md-sys-color-outline);
}

/* 响应式设计 */
@media (max-width: 600px) {
  .platform-title {
    font-size: 1.1rem;
  }

  .page-wrapper {
    padding: 1rem;
  }

  .menu-item {
    margin: 0.3rem 0.5rem;
  }
}
</style>
