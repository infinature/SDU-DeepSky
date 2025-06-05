<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated class="bg-primary">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          :icon="leftDrawerOpen ? 'menu_open' : 'menu'"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title>
          SDU-DeepSky - MSTAR
        </q-toolbar-title>

        <div>SDU</div>
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
            <span class="brand-name">🌠 MSTAR</span>
            <!-- Verified icon can be added here if needed: <q-icon name="verified" size="sm" class="q-ml-sm text-positive" /> -->
          </div>
          <div class="text-caption sidebar-subtitle">M-Star 分类</div>
        </div>

        <EssentialLink
          v-for="link in essentialLinks"
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

<script lang="ts">
import { defineComponent, ref } from 'vue';
import EssentialLink from 'components/EssentialLink.vue';
import { useQuasar } from 'quasar';

interface EssentialLinkProps {
  title: string;
  caption?: string;
  icon?: string;
  link?: string;
  routeName?: string;
}

const linksList: EssentialLinkProps[] = [
  {
    title: '首页',
    caption: '项目主页',
    icon: 'home',
    link: '/'
  },
  {
    title: '登录',
    caption: '用户登录',
    icon: 'login',
    link: '/login'
  },
  {
    title: '数据管理',
    caption: '浏览和管理数据',
    icon: 'mdi-database-cog-outline',
    link: '/data'
  },
  // {
  //   title: '光谱/图像可视化',
  //   icon: 'mdi-chart-scatter-plot',
  //   link: '/visualization'
  // },
  {
    title: '分类预测',
    caption: '使用模型进行预测',
    icon: 'online_prediction',
    link: '/predict'
  },
  {
    title: '返回导航门户',
    caption: '访问主导航页面',
    icon: 'exit_to_app',
    href: 'http://localhost:8000/',
    target: '_self'
  },
  // {
  //   title: '关于',
  //   icon: 'mdi-information-outline',
  // },
];

export default defineComponent({
  name: 'MainLayout',

  components: {
    EssentialLink
  },

  setup () {
    const $q = useQuasar();
    const leftDrawerOpen = ref(false);
    console.log('Runtime essentialLinks:', linksList);

    return {
      $q,
      essentialLinks: linksList,
      leftDrawerOpen,
      toggleLeftDrawer () {
        leftDrawerOpen.value = !leftDrawerOpen.value;
      }
    };
  }
});
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
  /* Attempt to use Quasar's primary color if available, otherwise a generic one */
  /* background: var(--q-primary-light, rgba(0, 0, 0, 0.1)); */ /* This project might not have --q-primary-light */
  background: rgba(19, 54, 101, 0.15); /* Using a known primary-like color from other projects as a placeholder */
  /* color: var(--q-on-primary-container, black); Ensure text is readable */
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

/* .brand-name can be styled if needed */


</style> 