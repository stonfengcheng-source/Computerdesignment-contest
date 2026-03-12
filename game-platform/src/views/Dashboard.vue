<template>
  <div class="dashboard-container">
    <header class="dashboard-header">
      <div class="header-left">
        <h1>深蓝卫士·管理员控制台</h1>
        <p>系统运行状态：<span class="status-online">● 核心多模态引擎运行中</span></p>
      </div>
      <div class="header-right">
        <div class="stat-badge">今日处理流：<span>12,408</span></div>
        <div class="stat-badge alert">拦截违规：<span>342</span></div>
      </div>
    </header>

    <section class="demo-section">
      <div class="section-title">
        <h2>多模态分析靶场 (Demo)</h2>
        <p>上传游戏对局录像，模拟关系流、文本流与行为流的综合净化分析。</p>
      </div>

      <div class="demo-workspace">
        <div class="upload-area" :class="{ 'has-file': videoUrl }">
          <input type="file" accept="video/*" @change="handleFileUpload" class="file-input" />

          <div v-if="!videoUrl" class="upload-placeholder">
            <div class="upload-icon">📁</div>
            <h3>点击或拖拽游戏录像至此处</h3>
            <p>支持 MP4, WebM 格式</p>
          </div>

          <div v-else class="video-preview">
            <video :src="videoUrl" controls class="preview-player"></video>
            <button class="btn-primary start-btn" @click="startAnalysis" :disabled="isAnalyzing">
              {{ isAnalyzing ? '分析引擎运转中...' : '启动多模态深度分析' }}
            </button>
          </div>
        </div>

        <div class="analysis-panel">
          <div class="panel-header">分析链路日志</div>
          <div class="log-container" ref="logContainer">
            <div v-if="processLogs.length === 0" class="empty-log">等待输入多模态数据...</div>
            <div v-for="(log, index) in processLogs" :key="index" class="log-item" :class="log.type">
              <span class="time">[{{ log.time }}]</span>
              <span class="text">{{ log.msg }}</span>
            </div>
          </div>

          <div v-if="analysisResult" class="result-summary">
            <h4>综合评定结果：<span class="danger">检测到违规风险</span></h4>
            <div class="result-tags">
              <span class="tag tag-sarcasm">阴阳怪气: 87%</span>
              <span class="tag tag-behavior">行为异常: 65%</span>
              <span class="tag tag-slang">黑话匹配: 3项</span>
            </div>
            <button class="btn-text" @click="goToModule('/detect')">查看详细检测报告 &rarr;</button>
          </div>
        </div>
      </div>
    </section>

    <section class="modules-section">
      <h2 class="sub-title">系统功能矩阵</h2>
      <div class="modules-grid">
        <div
          v-for="(mod, index) in processedModules"
          :key="index"
          class="module-card"
          @click="goToModule(mod.route)"
        >
          <div class="card-icon">{{ mod.icon }}</div>
          <div class="card-content">
            <h3>{{ mod.title }}</h3>
            <p>{{ mod.desc }}</p>
          </div>
          <div class="card-arrow">&rarr;</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// --- 视频上传与演示逻辑 ---
const videoUrl = ref('');
const isAnalyzing = ref(false);
const processLogs = ref([]);
const analysisResult = ref(false);
const logContainer = ref(null);

// 模拟的分析步骤数据
const mockSteps = [
  { msg: "提取视频流... 成功", type: "info" },
  { msg: "启动多模态分离器 (Audio/Text/Behavior)...", type: "info" },
  { msg: "Wav2Vec2 情感声学特征提取中...", type: "process" },
  { msg: "警告：声纹检测到疑似嘲讽语气！", type: "warn" },
  { msg: "Whisper ASR 语音转文本完成，正在过 BERT 引擎...", type: "process" },
  { msg: "捕获高频对抗性网络黑话词汇。", type: "warn" },
  { msg: "LSTM Autoencoder 比对玩家操作与发言...", type: "process" },
  { msg: "检测到【言行不一】行为特征（消极比赛）。", type: "warn" },
  { msg: "综合决策融合完成，正在生成评级报告...", type: "success" }
];

const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    videoUrl.value = URL.createObjectURL(file);
    processLogs.value = [];
    analysisResult.value = false;
  }
};

const startAnalysis = () => {
  if (isAnalyzing.value) return;
  isAnalyzing.value = true;
  processLogs.value = [];
  analysisResult.value = false;

  let stepIndex = 0;

  // 自定义循环逻辑控制异步推演过程
  const runSimulation = () => {
    let continueProcess = true;
    while (continueProcess) {
      if (stepIndex < mockSteps.length) {
        const step = mockSteps[stepIndex];
        const now = new Date();
        const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;

        processLogs.value.push({
          time: timeStr,
          msg: step.msg,
          type: step.type
        });

        stepIndex++;

        // 滚动到底部
        nextTick(() => {
          if (logContainer.value) {
            logContainer.value.scrollTop = logContainer.value.scrollHeight;
          }
        });

        continueProcess = false; // 退出当前while，等待setTimeout触发下一次
        setTimeout(runSimulation, Math.random() * 800 + 400); // 随机延迟 400-1200ms
      } else {
        isAnalyzing.value = false;
        analysisResult.value = true;
        continueProcess = false;
      }
    }
  };

  runSimulation();
};

// --- 子模块导航数据与处理 ---
const rawModules = [
  { icon: '🕸️', title: '风险溯源拓扑', desc: '利用GAT图神经网络找出污染源与传播路径', route: '/trace' },
  { icon: '🛡️', title: '跨平台信用评级', desc: '异构数据打分，生成用户综合游戏信用画像', route: '/credit' },
  { icon: '🎭', title: '阴阳怪气分析', desc: '情感与语义剥离，识别隐藏嘲讽', route: '/detect' },
  { icon: '📖', title: '网络黑话解析', desc: '对抗性词库与暗语监测挖掘', route: '/detect' },
  { icon: '🎮', title: '言行不一检测', desc: '比对行为流与文本流，定位异常消极行为', route: '/detect' }
];

// 组装最终渲染的数据格式
const processedModules = reactive([]);
let modIndex = 0;
while (modIndex < rawModules.length) {
  processedModules.push(rawModules[modIndex]);
  modIndex++;
}

const goToModule = (path) => {
  router.push(path);
};
</script>

<style scoped>
/* 亮色全局控制 */
.dashboard-container {
  padding: 30px 40px;
  background-color: #f8fafc;
  min-height: 100vh;
  color: #334155;
  font-family: 'Inter', sans-serif;
}

/* 头部样式 */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.header-left h1 {
  font-size: 2rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 8px 0;
}

.header-left p {
  font-size: 0.95rem;
  color: #64748b;
  margin: 0;
}

.status-online {
  color: #10b981;
  font-weight: 600;
}

.header-right {
  display: flex;
  gap: 20px;
}

.stat-badge {
  background: #ffffff;
  padding: 12px 24px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 500;
}

.stat-badge span {
  display: block;
  font-size: 1.5rem;
  font-weight: 800;
  color: #0ea5e9;
  margin-top: 4px;
}

.stat-badge.alert span {
  color: #ef4444;
}

/* 靶场区块 */
.demo-section {
  background: #ffffff;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
  margin-bottom: 40px;
}

.section-title h2 {
  font-size: 1.5rem;
  color: #0f172a;
  margin: 0 0 5px 0;
}

.section-title p {
  color: #64748b;
  margin: 0 0 25px 0;
}

.demo-workspace {
  display: flex;
  gap: 30px;
  height: 400px;
}

/* 上传区 */
.upload-area {
  flex: 1;
  position: relative;
  border: 2px dashed #cbd5e1;
  border-radius: 16px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition: all 0.3s ease;
}

.upload-area:hover {
  border-color: #0ea5e9;
  background: #e0f2fe;
}

.upload-area.has-file {
  border: none;
  background: #000;
}

.file-input {
  position: absolute;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 10;
}

.upload-placeholder {
  text-align: center;
  pointer-events: none;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.upload-placeholder h3 {
  color: #334155;
  margin: 0 0 5px 0;
}

.video-preview {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  flex-direction: column;
}

.preview-player {
  width: 100%;
  height: calc(100% - 60px);
  object-fit: contain;
}

.start-btn {
  height: 60px;
  border-radius: 0 0 16px 16px;
  font-size: 1.1rem;
  z-index: 11;
}

/* 日志面板全面亮色化 */
.analysis-panel {
  flex: 1;
  background: #ffffff; /* 改为纯白背景 */
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.panel-header {
  background: #f8fafc; /* 浅灰表头 */
  color: #334155;
  padding: 12px 20px;
  font-size: 0.95rem;
  font-weight: 700;
  border-bottom: 1px solid #e2e8f0;
}

.log-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 0.9rem;
  background: #fdfdfd;
}

.empty-log {
  color: #94a3b8;
  text-align: center;
  margin-top: 50px;
}

.log-item.info .text { color: #64748b; }
.log-item.process .text { color: #0ea5e9; font-weight: 500;}
.log-item.warn .text { color: #ea580c; font-weight: bold; }
.log-item.success .text { color: #10b981; font-weight: bold; }

.result-summary {
  background: #f0fdf4; /* 成功状态的浅绿底色 */
  padding: 20px;
  border-top: 1px dashed #cbd5e1;
}

.result-summary h4 {
  color: #0f172a;
  margin: 0 0 10px 0;
}

.result-summary .danger {
  color: #ef4444;
}

.result-tags {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.tag {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
}
.tag-sarcasm { background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid #ef4444; }
.tag-behavior { background: rgba(245, 158, 11, 0.2); color: #fcd34d; border: 1px solid #f59e0b; }
.tag-slang { background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid #10b981; }

/* 模块网格区 */
.modules-section {
  margin-top: 20px;
}

.sub-title {
  font-size: 1.3rem;
  color: #0f172a;
  margin-bottom: 20px;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.module-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 20px -8px rgba(14, 165, 233, 0.3);
  border-color: #bae6fd;
}

.card-icon {
  font-size: 2rem;
  background: #f0f9ff;
  padding: 12px;
  border-radius: 12px;
}

.card-content h3 {
  font-size: 1.1rem;
  color: #0f172a;
  margin: 0 0 6px 0;
}

.card-content p {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}

.card-arrow {
  margin-left: auto;
  color: #94a3b8;
  font-size: 1.2rem;
  transition: transform 0.2s;
}

.module-card:hover .card-arrow {
  color: #0ea5e9;
  transform: translateX(4px);
}

/* 公共按钮 */
.btn-primary {
  background: #0ea5e9;
  color: #fff;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}
.btn-primary:hover:not(:disabled) {
  background: #0284c7;
}
.btn-primary:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}
.btn-text {
  background: transparent;
  border: none;
  color: #38bdf8;
  cursor: pointer;
  padding: 0;
  font-size: 0.9rem;
}
.btn-text:hover {
  text-decoration: underline;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>