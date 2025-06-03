// 导入并注册Quasar插件
import { Notify } from 'quasar'

// 这是Quasar的启动文件，在应用启动前运行
export default async ({ app }) => {
  // 只能通过这种方式注册Notify服务
  // 在组合式API中，仍然需要通过useQuasar()获取$q对象
  app.config.globalProperties.$q = app.config.globalProperties.$q || {}
  app.config.globalProperties.$q.notify = Notify.create
}
