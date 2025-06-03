<template>
  <div class="timeline-bg">
    <div class="timeline-container">
      <!-- 时间轴 -->
      <div class="timeline">
        <div class="timeline-dot" style="top: 80px;"></div>
        <div class="timeline-dot" style="top: 340px;"></div>
        <div class="timeline-dot" style="top: 600px;"></div>
        <div class="timeline-line"></div>
      </div>
      <!-- 卡片内容 -->
      <div class="timeline-content">
        <div class="timeline-card" @click="goTo('/desi')">
          <div class="timeline-date">
            2024年5月 <span class="timeline-tag">数据集</span>
          </div>
          <div class="timeline-title">DESI 数据集</div>
          <div class="timeline-desc">DESI（暗能量光谱仪）项目的数据集，包含丰富的光谱观测数据，适用于宇宙学和星系研究。</div>
          <q-btn color="primary" label="进入 DESI" class="timeline-btn" />
        </div>
        <div class="timeline-card" @click="goTo('/jplus')">
          <div class="timeline-date">
            2024年1月 <span class="timeline-tag">数据集</span>
          </div>
          <div class="timeline-title">J-PLUS 数据集</div>
          <div class="timeline-desc">J-PLUS 项目提供多波段成像数据，适合恒星、星系等天体的多色测光分析。</div>
          <q-btn color="primary" label="进入 J-PLUS" class="timeline-btn" />
        </div>
        <div class="timeline-card" @click="goTo('/panstarrs')">
          <div class="timeline-date">
            2023年12月 <span class="timeline-tag">数据集</span>
          </div>
          <div class="timeline-title">Pan-STARRS 数据集</div>
          <div class="timeline-desc">Pan-STARRS 拥有大面积的深度巡天数据，广泛应用于变星、超新星等领域。</div>
          <q-btn color="primary" label="进入 Pan-STARRS" class="timeline-btn" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
function goTo(path) {
  router.push(path)
}
</script>

<style scoped>
.timeline-bg {
  min-height: 100vh;
  background: #0a0a23;
  padding-top: 60px;
}
.timeline-container {
  display: flex;
  flex-direction: row;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
}
.timeline {
  width: 80px;
  position: relative;
}
.timeline-line {
  position: absolute;
  left: 38px;
  top: 60px;
  width: 4px;
  height: 600px;
  background: #a084e8;
  border-radius: 2px;
}
.timeline-dot {
  position: absolute;
  left: 30px;
  width: 20px;
  height: 20px;
  background: #a084e8;
  border-radius: 50%;
  border: 4px solid #fff;
  z-index: 2;
}
.timeline-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 40px;
  margin-left: 40px;
}
.timeline-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 16px rgba(160, 132, 232, 0.08);
  padding: 32px 40px;
  margin-bottom: 20px;
  position: relative;
  cursor: pointer;
  transition: transform 0.2s;
}
.timeline-card:hover {
  transform: translateY(-10px) scale(1.03);
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
.timeline-date {
  color: #a084e8;
  font-weight: bold;
  font-size: 1.1rem;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.timeline-tag {
  background: #e0e0e0;
  color: #555;
  border-radius: 6px;
  font-size: 0.8rem;
  padding: 2px 8px;
  margin-left: 8px;
}
.timeline-title {
  font-size: 1.3rem;
  font-weight: bold;
  margin-bottom: 10px;
}
.timeline-desc {
  color: #333;
  font-size: 1rem;
  margin-bottom: 18px;
}
.timeline-btn {
  font-size: 1rem;
}
</style>
