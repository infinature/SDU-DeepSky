<template>
  <q-layout view="lHh Lpr lFf">
    <q-header class="bg-primary">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          :icon="leftDrawerOpen ? 'menu_open' : 'menu'"
          color="white"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title class="text-white">
          SDU-DeepSky - AstroYOLO
        </q-toolbar-title>

        <div class="text-caption text-white">SDU</div>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      side="left"
      width="260"
    >
      <q-list class="menu-list">
        <div class="drawer-header">
          <div class="text-h5 font-bold flex items-center">
            <span class="brand-name">✨ AstroYOLO</span>
            <!-- Verified icon can be added here if needed: <q-icon name="verified" size="sm" class="q-ml-sm text-positive" /> -->
          </div>
          <div class="text-caption sidebar-subtitle">天体检测系统</div>
        </div>

        <EssentialLink
          v-for="link in linksList"
          :key="link.title"
          v-bind="link"
          item-class="menu-item"
          active-class="menu-item-active"
        />
      </q-list>
    </q-drawer>

    <q-page-container>
      <transition name="page-transition" mode="out-in">
        <router-view />
      </transition>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import EssentialLink from 'components/EssentialLink.vue'

const linksList = [
  {
    title: '首页',
    caption: '系统主页',
    icon: 'home',
    to: '/'
  },
  {
    title: '单图检测',
    caption: '检测单张图片',
    icon: 'photo',
    to: '/single-detection'
  },
  {
    title: '批量检测',
    caption: '检测多张图片',
    icon: 'photo_library',
    to: '/batch-detection'
  },
  {
    title: 'AstroYOLO 论文',
    caption: '查看相关研究论文',
    icon: 'article',
    href: '/He 等 - 2023 - AstroYOLO A hybrid CNN–Transformer deep-learning object-detection model for blue horizontal-branch.pdf',
    target: '_blank'
  },
  {
    title: '返回导航门户',
    caption: '访问主导航页面',
    icon: 'exit_to_app',
    href: 'http://localhost:8000/',
    target: '_self'
  }
  // {
  //   title: '结果管理',
  //   caption: '查看历史检测结果',
  //   icon: 'assessment',
  //   to: '/results'
  // }
]

const leftDrawerOpen = ref(false)

function toggleLeftDrawer () {
  leftDrawerOpen.value = !leftDrawerOpen.value
}
</script>

<style scoped>
/* Styles adapted from mspc-net/frontend_test/src/layouts/MainLayout.vue */

.menu-list { /* Added to q-list */
  padding: 0.5rem;
}

/* These classes are intended for EssentialLink via item-class and active-class props */
.menu-item {
  margin: 0.3rem 0;
  border-radius: 8px;
  transition: all 0.3s ease;
  /* padding: 0.5rem; EssentialLink likely has its own padding via q-item */
}

.menu-item:hover {
  background: rgba(0, 0, 0, 0.05); /* Adapted: light grey for hover */
  transform: translateX(5px);
}

.menu-item-active {
  background: rgba(19, 54, 101, 0.15); /* Adapted: Lighter shade of astroyolo primary */
  /* color: var(--md-sys-color-on-primary-container); Ensure text is readable */
}

/* Targeting icons within EssentialLink, assuming it renders a q-icon inside q-item-section--avatar */
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

/* Custom scrollbar styles */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1; /* Adapted: light grey */
}

::-webkit-scrollbar-thumb {
  background: #cccccc; /* Adapted: medium grey */
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #aaaaaa; /* Adapted: darker grey */
}

/* Drawer Header Styles */
.drawer-header {
  padding: 1rem;
  border-bottom: 1px solid rgba(0,0,0,0.12); /* Quasar default separator color */
  background: #f9f9f9; /* A light surface color for the drawer header */
}

/* .brand-name can be styled if needed using Quasar utility classes or specific CSS */
</style>
