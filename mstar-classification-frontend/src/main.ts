import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { Quasar, Notify, Dialog, Loading } from 'quasar';
import { createPinia } from 'pinia';

// Import icon libraries
import '@quasar/extras/material-icons/material-icons.css';

// Import Quasar css
import 'quasar/src/css/index.sass';

// Assumes your root component is App.vue
// and placed in same folder as main.js
const myApp = createApp(App);

myApp.use(Quasar, {
  plugins: { Notify, Dialog, Loading }, // import Quasar plugins and add here
  /*
  config: {
    brand: {
      // primary: '#e46262',
      // ... or all other brand colors
    },
    notify: {...}, // default set of options for Notify Quasar plugin
    loading: {...}, // default set of options for Loading Quasar plugin
    dialog: {...}, // default set of options for Dialog Quasar plugin
    // DarkMode: 'auto', // If a DarkMode plugin has been QSImported, this will enable it
    //animations: 'all', //animations: [],
  },
  */
});

myApp.use(createPinia());
myApp.use(router);

// Assumes you have a <div id="app"></div> in your index.html
myApp.mount('#q-app'); // Quasar uses #q-app by default 