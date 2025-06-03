const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: 'single-detection', component: () => import('pages/SingleDetection.vue') },
      { path: 'batch-detection', component: () => import('pages/BatchDetection.vue') },
      { path: 'results', component: () => import('pages/ResultsManagement.vue') },
      { path: 'results/:taskId', component: () => import('pages/ResultDisplayPage.vue'), name: 'ResultDisplay' },
      { path: 'batch-results/:taskId', component: () => import('pages/BatchResultsPage.vue'), name: 'BatchResults' }
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
