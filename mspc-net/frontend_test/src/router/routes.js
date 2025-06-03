import WelcomePage from 'pages/WelcomePage.vue'
import MainLayout from 'layouts/MainLayout.vue'

const routes = [
  {
    path: '/',
    component: WelcomePage,
  },
  {
    path: '/main',
    component: MainLayout,
    children: [
      {
        path: '',
        redirect: '/main/test',
      },
      {
        path: 'test',
        component: () => import('pages/TestPage.vue'),
      },
      {
        path: 'paper',
        component: () => import('pages/PaperPage.vue'),
      },
      {
        path: 'predict',
        component: () => import('pages/PredictPage.vue'),
      },
    ],
  },
]

export default routes
