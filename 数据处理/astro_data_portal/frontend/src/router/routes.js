const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: 'desi', component: () => import('pages/DESIPage.vue') },
      { path: 'jplus', component: () => import('pages/JPlusPage.vue') },
      { path: 'panstarrs', component: () => import('pages/PanSTARRSPage.vue') },
      { path: 'files', component: () => import('../pages/FilesPage.vue') }
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes
