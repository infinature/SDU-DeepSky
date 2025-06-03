<template>
  <q-page padding>
    <h4 class="q-my-md">登录</h4>
    <q-form @submit.prevent="onSubmit" class="q-gutter-md">
      <q-input
        filled
        v-model="username"
        label="用户名"
        lazy-rules
        :rules="[ val => val && val.length > 0 || '请输入用户名']"
      />

      <q-input
        filled
        type="password"
        v-model="password"
        label="密码"
        lazy-rules
        :rules="[ val => val && val.length > 0 || '请输入密码']"
      />

      <div>
        <q-btn label="登录" type="submit" color="primary"/>
      </div>
    </q-form>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useQuasar } from 'quasar';

export default defineComponent({
  name: 'LoginPage',
  setup() {
    const $q = useQuasar();
    const username = ref('');
    const password = ref('');

    const onSubmit = () => {
      // 实际登录逻辑
      $q.notify({
        color: 'green-4',
        textColor: 'white',
        icon: 'cloud_done',
        message: '登录成功（占位符）'
      });
    };

    return {
      username,
      password,
      onSubmit,
    };
  },
});
</script> 