<template>
  <q-layout view="lHh Lpr lFf">
    <!-- 顶部导航栏 -->
    <q-header elevated class="bg-primary text-on-primary" style="background-color: rgb(19, 54, 101) !important;">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          :icon="drawer ? 'menu_open' : 'menu'"
          @click="drawer = !drawer"
          class="q-mr-sm menu-btn text-white"
        />
        <q-toolbar-title class="text-white">
          SDU-DeepSky - MSPC-Net
        </q-toolbar-title>
        <div class="text-white">SDU</div>
      </q-toolbar>
    </q-header>

    <!-- 左侧导航抽屉 -->
    <q-drawer
      v-model="drawer"
      show-if-above
      side="left"
      bordered
      width="260"
    >
      <div class="drawer-header">
        <div class="text-h5 font-bold flex items-center">
          <span class="brand-name">🌌 MSPC-Net</span>
        </div>
        <div class="text-caption sidebar-subtitle">多光谱星型分类平台</div>
      </div>
      <q-list class="menu-list">
        <!-- EssentialLink equivalent structure -->
        <q-item
          v-for="link in essentialLinks"
          :key="link.title"
          clickable
          v-ripple
          :to="link.link"
          :href="link.href"
          :target="link.target"
          item-class="menu-item" 
          active-class="menu-item-active" 
          @click="link.action ? link.action() : null"
        >
          <q-item-section v-if="link.icon" avatar>
            <q-icon :name="link.icon" />
          </q-item-section>
          <q-item-section>
            <q-item-label>{{ link.title }}</q-item-label>
            <q-item-label caption>{{ link.caption }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <!-- 页面主体容器 -->
    <q-page-container>
      <transition name="page-transition" mode="out-in">
        <router-view />
      </transition>
    </q-page-container>

  </q-layout>
</template>

<script setup>
import { ref } from 'vue'

const drawer = ref(false) // Default to closed like others

// Adapted to EssentialLinkProps structure
const essentialLinks = [
  {
    title: '模型训练',
    icon: 'science',
    link: '/main/test', // Changed path to link
    caption: '模型测试与验证', // Changed description to caption
  },
  {
    title: '论文查看',
    icon: 'article',
    link: '/main/paper',
    caption: '相关论文研究',
  },
  {
    title: '模型预测',
    icon: 'analytics',
    link: '/main/predict',
    caption: '智能预测分析',
  },
  {
    title: '代码仓库',
    icon: 'code',
    caption: '访问项目源码',
    action: () => {
      window.open('https://github.com/qintianjian-lab/MSPC-Net', '_blank')
    },
  },
  {
    title: '返回导航门户',
    icon: 'exit_to_app',
    caption: '访问主导航页面',
    // For external links, href and target are better if not using action
    href: 'http://localhost:8000/',
    target: '_self',
    action: undefined, // Clear action if href is used
  },
]
</script>

<style scoped>
/* Styles adapted from astroyolo/mstar to simplify mspc-net */

.menu-list { /* Added to q-list */
  padding: 0.5rem;
}

/* These classes are intended for q-item via item-class and active-class props */
.menu-item {
  margin: 0.3rem 0;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.menu-item:hover {
  background: rgba(0, 0, 0, 0.05); /* Adapted: light grey for hover */
  transform: translateX(5px);
}

.menu-item-active {
  background: rgba(19, 54, 101, 0.15); /* Adapted: Lighter shade of primary */
}

/* Targeting icons within q-item-section--avatar */
.menu-item .q-item__section--avatar .q-icon {
  font-size: 1.2rem;
  transition: all 0.3s ease;
}

.menu-item:hover .q-item__section--avatar .q-icon {
  transform: scale(1.1);
}

/* Page transitions */
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

/* Drawer Header Styles - simplified */
.drawer-header {
  padding: 1rem;
  border-bottom: 1px solid rgba(0,0,0,0.12);
  background: #f9f9f9;
}

/* Custom scrollbar styles - simplified */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #cccccc;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #aaaaaa;
}

/* Responsive design adjustments for menu items on smaller screens */
@media (max-width: 600px) {
  .menu-item {
    margin: 0.3rem 0.5rem; /* Slightly reduce horizontal margin for smaller screens */
    padding-left: 0.75rem; /* Adjust padding if necessary */
    padding-right: 0.75rem;
  }
}
</style>
