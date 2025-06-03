export default {
  failed: 'Action failed',
  success: 'Action was successful',
  appName: 'M-Star Classification',
  nav: {
    home: 'Home',
    login: 'Login',
    dataManagement: 'Data Management',
    visualization: 'Visualization',
    modelTraining: 'Model Training',
    prediction: 'Prediction'
  },
  pages: {
    home: {
      welcome: 'Welcome to the M-Star Classification System',
      description: 'A tool for classifying M-type stars based on spectral and image data.',
      explore: 'Start Exploring'
    },
    login: {
      title: 'Login',
      username: 'Username',
      password: 'Password',
      submit: 'Login',
      usernameRequired: 'Please type your username',
      passwordRequired: 'Please type your password',
      loginSuccess: 'Login successful (placeholder)'
    },
    data: {
      title: 'Data Management',
      description: 'View and manage spectral and image data here.',
      tableTitle: 'Star Data',
      columns: {
        name: 'Name',
        ra: 'RA',
        dec: 'Dec',
        type: 'Type',
        actions: 'Actions'
      }
    },
    visualization: {
      title: 'Spectrum/Image Visualization',
      description: 'Select a data point to display its spectrum and image.',
      spectrumCardTitle: 'Spectrum Plot',
      imageCardTitle: 'Image',
      spectrumPlaceholder: 'Spectrum plot area',
      imagePlaceholder: 'Image area'
    },
    training: {
      title: 'Model Training',
      description: 'Configure and start the model training process here.',
      paramsCardTitle: 'Training Parameters',
      selectModel: 'Select Model',
      epochs: 'Epochs',
      batchSize: 'Batch Size',
      learningRate: 'Learning Rate',
      startTraining: 'Start Training',
      logCardTitle: 'Training Log',
      waiting: 'Waiting to start training...',
      starting: 'Starting model training...\n',
      epochComplete: 'Epoch {current}/{total} complete - Accuracy: {accuracy}\n',
      trainingComplete: 'Training complete!',
      notifyTrainingComplete: 'Model training complete'
    },
    predict: {
      title: 'Classification Prediction',
      description: 'Upload data or select existing data for classification prediction.',
      inputCardTitle: 'Input Data',
      uploadSpectrum: 'Upload spectrum file (.fits)',
      uploadImage: 'Upload image file (.jpg, .png)',
      startPrediction: 'Start Prediction',
      resultCardTitle: 'Prediction Result',
      predictedType: 'Predicted Type',
      confidence: 'Confidence',
      errorMissingFiles: 'Please upload both spectrum and image files',
      notifyPredictionComplete: 'Prediction complete'
    }
  }
}; 