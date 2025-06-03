import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue'), name: 'home' },
      { path: 'login', component: () => import('pages/LoginPage.vue'), name: 'login' },
      { path: 'data', component: () => import('pages/DataManagerPage.vue'), name: 'data' },
      { path: 'visualize', component: () => import('pages/VisualizationPage.vue'), name: 'visualize' },
      { path: 'train', component: () => import('pages/TrainingPage.vue'), name: 'train' },
      { path: 'predict', component: () => import('pages/PredictPage.vue'), name: 'predict' },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes; 