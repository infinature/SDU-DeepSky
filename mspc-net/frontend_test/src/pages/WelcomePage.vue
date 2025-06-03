<template>
  <div class="welcome-page">
    <!-- 背景动画元素 -->
    <div class="background-animation">
      <div
        v-for="n in 6"
        :key="n"
        class="floating-circle"
        :style="{ '--delay': `${n * 0.5}s` }"
      ></div>
    </div>

    <div class="welcome-content">
      <!-- Logo 部分 -->
      <div class="logo-section">
        <div class="logo-container">
          <div class="logo-circle">
            <q-icon name="science" size="5rem" class="logo-icon" />
          </div>
          <div class="logo-rings">
            <div class="ring ring-1"></div>
            <div class="ring ring-2"></div>
            <div class="ring ring-3"></div>
          </div>
        </div>
      </div>

      <!-- 标题部分 -->
      <div class="title-section">
        <h1 class="welcome-title">
          <span class="title-text">MSPC-Net</span>
        </h1>
        <p class="welcome-subtitle">智能预测分析</p>
        <div class="feature-tags">
          <span class="tag">深度学习</span>
          <span class="tag">智能预测</span>
          <span class="tag">数据分析</span>
        </div>
      </div>

      <!-- 按钮部分 -->
      <div class="button-section">
        <q-btn class="enter-btn" color="primary" size="lg" @click="enterApp" :loading="loading">
          <template v-slot:default>
            <span class="btn-content">
              <span class="btn-text">进入系统</span>
              <q-icon name="arrow_forward" class="btn-icon" />
            </span>
          </template>
          <template v-slot:loading>
            <q-spinner-dots color="white" />
          </template>
        </q-btn>
      </div>

      <!-- 页脚信息 -->
      <div class="footer-info">
        <p class="version">Version 2.0</p>
        <p class="copyright">© 2025 MSPC-Net. All rights reserved.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)

const enterApp = async () => {
  loading.value = true
  await new Promise((resolve) => setTimeout(resolve, 1000))
  router.push('/main')
}
</script>

<style scoped>
.welcome-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(
    135deg,
    var(--md-sys-color-surface-container-low) 0%,
    var(--md-sys-color-surface-container) 100%
  );
  position: relative;
  overflow: hidden;
}

.background-animation {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 0;
}

.floating-circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(45deg, var(--md-sys-color-primary), var(--md-sys-color-secondary));
  opacity: 0.15;
  animation: float 15s infinite;
  animation-delay: var(--md-sys-color-secondary);
}

.floating-circle:nth-child(1) {
  width: 300px;
  height: 300px;
  top: -150px;
  left: -150px;
}
.floating-circle:nth-child(2) {
  width: 200px;
  height: 200px;
  top: 20%;
  right: -100px;
}
.floating-circle:nth-child(3) {
  width: 150px;
  height: 150px;
  bottom: 10%;
  left: 10%;
}
.floating-circle:nth-child(4) {
  width: 250px;
  height: 250px;
  bottom: -125px;
  right: 15%;
}
.floating-circle:nth-child(5) {
  width: 180px;
  height: 180px;
  top: 30%;
  left: 20%;
}
.floating-circle:nth-child(6) {
  width: 220px;
  height: 220px;
  bottom: 30%;
  right: 25%;
}

.welcome-content {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 2rem;
  max-width: 800px;
  width: 100%;
}

.logo-section {
  margin-bottom: 3rem;
}

.logo-container {
  position: relative;
  width: 150px;
  height: 150px;
  margin: 0 auto;
}

.logo-circle {
  width: 100%;
  height: 100%;
  background: var(--md-sys-color-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 2;
  animation: pulse 2s infinite;
}

.logo-icon {
  color: var(--md-sys-color-on-primary);
  animation: rotate 20s linear infinite;
}

.logo-rings {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
}

.ring {
  position: absolute;
  border: 2px solid var(--md-sys-color-primary);
  border-radius: 50%;
  animation: expand 3s infinite;
}

.ring-1 {
  width: 100%;
  height: 100%;
  animation-delay: 0s;
}
.ring-2 {
  width: 100%;
  height: 100%;
  animation-delay: 1s;
}
.ring-3 {
  width: 100%;
  height: 100%;
  animation-delay: 2s;
}

.title-section {
  margin-bottom: 3rem;
}

.welcome-title {
  font-size: 4.5rem;
  font-weight: 800;
  margin: 1rem 0;
  line-height: 1.2;
  text-align: center;
}

.title-text {
  background: linear-gradient(45deg, var(--md-sys-color-primary), var(--md-sys-color-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: fadeInUp 1s ease-out;
  display: inline-block;
  position: relative;
}

.title-text::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 4px;
  background: linear-gradient(45deg, var(--md-sys-color-primary), var(--md-sys-color-secondary));
  border-radius: 2px;
  animation: expandWidth 1s ease-out 0.5s forwards;
  opacity: 0;
}

.welcome-subtitle {
  font-size: 1.8rem;
  color: var(--md-sys-color-on-surface);
  margin: 2rem 0;
  opacity: 0;
  animation: fadeIn 1s ease-out 0.6s forwards;
  font-weight: 500;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.feature-tags {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 2rem;
}

.tag {
  padding: 0.8rem 2rem;
  background: var(--md-sys-color-surface-container-high);
  color: var(--md-sys-color-on-surface);
  border-radius: 50px;
  font-size: 1.1rem;
  opacity: 0;
  animation: fadeIn 0.5s ease-out forwards;
  font-weight: 500;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
  background: var(--md-sys-color-surface-container-highest);
}

.button-section {
  margin: 3rem 0;
}

.enter-btn {
  padding: 1.2rem 4rem;
  border-radius: 50px;
  font-size: 1.3rem;
  opacity: 0;
  animation: fadeIn 1s ease-out 1.5s forwards;
  transition: all 0.3s ease;
  background: linear-gradient(45deg, var(--md-sys-color-primary), var(--md-sys-color-secondary));
  color: white;
  font-weight: 600;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.enter-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.btn-icon {
  transition: transform 0.3s ease;
}

.enter-btn:hover .btn-icon {
  transform: translateX(6px);
}

.footer-info {
  margin-top: 4rem;
  opacity: 0;
  animation: fadeIn 1s ease-out 2s forwards;
}

.version {
  font-size: 0.9rem;
  color: var(--md-sys-color-on-surface);
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.copyright {
  font-size: 0.8rem;
  color: var(--md-sys-color-on-surface);
  font-weight: 500;
}

@keyframes float {
  0%,
  100% {
    transform: translate(0, 0) rotate(0deg);
  }
  25% {
    transform: translate(10px, 10px) rotate(5deg);
  }
  50% {
    transform: translate(0, 20px) rotate(0deg);
  }
  75% {
    transform: translate(-10px, 10px) rotate(-5deg);
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(var(--md-sys-color-primary-rgb), 0.4);
  }
  70% {
    transform: scale(1.05);
    box-shadow: 0 0 0 20px rgba(var(--md-sys-color-primary-rgb), 0);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(var(--md-sys-color-primary-rgb), 0);
  }
}

@keyframes expand {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes expandWidth {
  from {
    width: 0;
    opacity: 0;
  }
  to {
    width: 60%;
    opacity: 1;
  }
}
</style>
