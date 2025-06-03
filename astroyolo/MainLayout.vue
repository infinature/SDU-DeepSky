<template>
  <q-layout view="lHh Lpr lFf">
    <q-header>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          color="white"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title class="text-white">
          AstroYOLO 天体检测系统
        </q-toolbar-title>

        <div class="text-caption text-white">Quasar v{{ $q.version }}</div>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
    >
      <q-list>
        <q-item-label
          header
        >
          Essential Links
        </q-item-label>

        <EssentialLink
          v-for="link in linksList"
          :key="link.title"
          v-bind="link"
        />
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
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
    title: '结果管理',
    caption: '查看历史检测结果',
    icon: 'assessment',
    to: '/results'
  },
  {
    title: '返回导航门户',
    caption: '访问主导航页面',
    icon: 'exit_to_app',
    href: 'http://localhost:8000/',
    target: '_self'
  }
]

const leftDrawerOpen = ref(false)

function toggleLeftDrawer () {
  leftDrawerOpen.value = !leftDrawerOpen.value
}
</script>
