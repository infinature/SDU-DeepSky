export default {
  failed: '操作失败',
  success: '操作成功',
  appName: 'M型星分类',
  nav: {
    home: '首页',
    login: '登录',
    dataManagement: '数据管理',
    visualization: '可视化',
    modelTraining: '模型训练',
    prediction: '分类预测'
  },
  pages: {
    home: {
      welcome: '欢迎使用M型星分类系统',
      description: '一个基于光谱和图像数据分类M型星的工具。',
      explore: '开始探索'
    },
    login: {
      title: '登录',
      username: '用户名',
      password: '密码',
      submit: '登录',
      usernameRequired: '请输入用户名',
      passwordRequired: '请输入密码',
      loginSuccess: '登录成功（占位符）'
    },
    data: {
      title: '数据管理',
      description: '在这里查看和管理光谱及图像数据。',
      tableTitle: '恒星数据',
      columns: {
        name: '名称',
        ra: '赤经',
        dec: '赤纬',
        type: '类型',
        actions: '操作'
      }
    },
    visualization: {
      title: '光谱/图像可视化',
      description: '选择一个数据点以显示其光谱和图像。',
      spectrumCardTitle: '光谱图',
      imageCardTitle: '图像',
      spectrumPlaceholder: '光谱图区域',
      imagePlaceholder: '图像区域'
    },
    training: {
      title: '模型训练',
      description: '在这里配置和启动模型训练过程。',
      paramsCardTitle: '训练参数',
      selectModel: '选择模型',
      epochs: '训练轮次',
      batchSize: '批量大小',
      learningRate: '学习率',
      startTraining: '开始训练',
      logCardTitle: '训练日志',
      waiting: '等待开始训练...',
      starting: '开始训练模型...\n',
      epochComplete: '轮次 {current}/{total} 完成 - 准确率: {accuracy}\n',
      trainingComplete: '训练完成！',
      notifyTrainingComplete: '模型训练完成'
    },
    predict: {
      title: '分类预测',
      description: '上传数据或选择现有数据进行分类预测。',
      inputCardTitle: '输入数据',
      uploadSpectrum: '上传光谱文件 (.fits)',
      uploadImage: '上传图像文件 (.jpg, .png)',
      startPrediction: '开始预测',
      resultCardTitle: '预测结果',
      predictedType: '预测类型',
      confidence: '置信度',
      errorMissingFiles: '请同时上传光谱和图像文件',
      notifyPredictionComplete: '预测完成'
    }
  }
}; 