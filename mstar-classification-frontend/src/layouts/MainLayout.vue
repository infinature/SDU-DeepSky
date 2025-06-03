<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title>
          M-Star Classification
        </q-toolbar-title>

        <div>Quasar v{{ $q.version }}</div>
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
          导航
        </q-item-label>

        <EssentialLink
          v-for="link in essentialLinks"
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