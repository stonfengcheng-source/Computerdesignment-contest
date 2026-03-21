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
        <h2>多模态分析靶场 (真实全链路测试)</h2>
        <p>上传游戏对局录像，调用后端 OpenCV 视觉引擎与 BERT NLP 模型，结果存入 SQLite。</p>
      </div>

      <div class="demo-workspace">
        <div class="upload-area" :class="{ 'has-file': videoUrl }">
          <input type="file" accept="video/*" @change="handleFileUpload" class="file-input" :disabled="isAnalyzing" />

          <div v-if="!videoUrl" class="upload-placeholder">
            <div class="upload-icon">📁</div>
            <h3>点击或拖拽游戏录像至此处</h3>
            <p>支持 MP4, WebM 格式</p>
          </div>

          <div v-else class="video-preview">
            <video :src="videoUrl" controls style="background: #000; z-index: 5;" class="preview-player"></video>

            <div v-if="isAnalyzing" class="progress-overlay">
              <div class="progress-text">多模态引擎超载运算中... {{ progress }}%</div>
              <div class="progress-track">
                <div class="progress-fill" :style="{ width: progress + '%' }"></div>
              </div>
            </div>

            <button v-else class="btn-primary start-btn" @click="startAnalysis">
              发送至后端并启动分析
            </button>
          </div>
        </div>

        <div class="analysis-panel">
          <div class="panel-header">分析链路日志 & 数据库响应</div>
          <div class="log-container" ref="logContainer">
            <div v-if="processLogs.length === 0" class="empty-log">等待输入多模态数据...</div>
            <div v-for="(log, index) in processLogs" :key="index" class="log-item" :class="log.type">
              <span class="time">[{{ log.time }}]</span>
              <span class="text">{{ log.msg }}</span>
            </div>
          </div>

          <div v-if="analysisResult" class="result-summary">
            <h4>综合评定结果：
              <span :class="analysisResult.is_inconsistent ? 'danger' : 'success'">
                {{ analysisResult.is_inconsistent ? '检测到言行不一 / 违规风险' : '未见明显异常' }}
                (风险等级: {{ analysisResult.risk_level }})
              </span>
            </h4>
            <div class="result-tags">
              <span class="tag tag-sarcasm">文本异常分: {{ formatScore(analysisResult.details.text_sentiment_prob) }}</span>
              <span class="tag tag-behavior">行为异常分: {{ formatScore(analysisResult.details.behavior_anomaly_score) }}</span>
              <span class="tag tag-slang">综合毒性值: {{ formatScore(analysisResult.details.final_toxicity_score) }}</span>
            </div>

            <div v-if="latestReportId" style="margin-top: 15px;">
              <button class="btn-primary" style="padding: 10px 20px; border-radius: 8px; width: 100%;" @click="downloadReport">
                📥 下载官方信用诊断判决书 (.txt)
              </button>
            </div>

            <div style="margin-top: 15px; display: flex; gap: 15px; justify-content: space-between;">
              <button class="btn-text" @click="goToModule('/behavior')">查看行为检测报告 &rarr;</button>
              <button class="btn-text" @click="jumpToCredit">查看跨平台信用档案 &rarr;</button>
            </div>

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

// --- 真实状态管理 ---
const selectedFile = ref(null);
const videoUrl = ref('');
const isAnalyzing = ref(false);
const processLogs = ref([]);
const analysisResult = ref(null);
const logContainer = ref(null);

// 💡 新增：保存刚刚生成的报告 ID
const latestReportId = ref(null);
const currentPlayerId = 'admin_test_001'; // 靶场默认测试ID

// 进度条管理
const progress = ref(0);
let progressTimer = null;

const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
    videoUrl.value = URL.createObjectURL(file);
    processLogs.value = [];
    analysisResult.value = null;
    latestReportId.value = null;
    progress.value = 0;
  }
};

const addLog = (msg, type = "info") => {
  const now = new Date();
  const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
  processLogs.value.push({ time: timeStr, msg, type });
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight;
    }
  });
};

const simulateProgress = () => {
  progress.value = 0;
  progressTimer = setInterval(() => {
    if (progress.value < 85) {
      progress.value += Math.floor(Math.random() * 5) + 2;
    } else if (progress.value < 98) {
      progress.value += 1;
    }
  }, 600);
};

const startAnalysis = async () => {
  if (isAnalyzing.value || !selectedFile.value) return;

  isAnalyzing.value = true;
  processLogs.value = [];
  analysisResult.value = null;
  latestReportId.value = null;

  simulateProgress();

  addLog(">>> [系统中枢] 收到指令，开始封包多模态数据...", "info");

  const formData = new FormData();
  formData.append('video_file', selectedFile.value);
  formData.append('player_id', currentPlayerId);

  try {
    addLog(">>> [模块1] 启动 CV+NLP 引擎：向后端发送视频，提取特征流...", "process");
    addLog(">>> [模块2] 唤醒 GAT 图神经网络：触发全网黑话溯源与拓扑更新...", "process");

    const videoAnalysisPromise = fetch('http://127.0.0.1:8000/api/v1/analyze/video', {
      method: 'POST',
      body: formData,
    });

    const graphAnalysisPromise = fetch('http://127.0.0.1:8000/api/slang/analyze', {
      method: 'POST',
    });

    const [videoResponse, graphResponse] = await Promise.all([
      videoAnalysisPromise,
      graphAnalysisPromise
    ]);

    if (!videoResponse.ok || !graphResponse.ok) {
      throw new Error(`后端引擎崩溃！Video:${videoResponse.status}, Graph:${graphResponse.status}`);
    }

    const videoData = await videoResponse.json();
    const graphData = await graphResponse.json();

    if (videoData.status === "success") {
      addLog(">>> [模块1] OpenCV 帧运算与 BERT 推理完成！数据已入库 SQLite。", "success");
      analysisResult.value = videoData.result;
    } else {
      addLog(`[模块1] 异常：${videoData.message}`, "warn");
    }

    if (graphData.status === "success") {
      addLog(">>> [模块2] GAT 溯源图谱已由后端重新计算并覆写！", "success");
    } else {
      addLog(`[模块2] 图谱训练异常：${graphData.message}`, "warn");
    }

    addLog(">>> [模块3] 启动信用评估模型：正在融合多模态特征生成综合信用报告...", "process");

    const textScore = videoData.result?.details?.text_sentiment_prob || 0.1;
    const behaviorScore = videoData.result?.details?.behavior_anomaly_score || 0.1;

    const reportResponse = await fetch('http://127.0.0.1:8000/api/v1/report/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        player_id: currentPlayerId,
        text_toxicity: textScore,
        audio_toxicity: 0.05,
        behavior_anomaly: behaviorScore,
        graph_risk: 0.82
      })
    });

    const reportData = await reportResponse.json();
    if (reportData.status === "success") {
      addLog(">>> [模块3] 玩家专属信用评级报告已生成！", "success");
      // 💡 保存生成的报告ID，让下载按钮亮起
      latestReportId.value = reportData.record_id;
    } else {
      addLog(`[模块3] 报告生成异常：${reportData.message}`, "warn");
    }

    clearInterval(progressTimer);
    progress.value = 100;

  } catch (error) {
    console.error(error);
    clearInterval(progressTimer);
    addLog(`前端总线异常：${error.message}`, "warn");
  } finally {
    setTimeout(() => {
      isAnalyzing.value = false;
      progress.value = 0;
    }, 800);
  }
};

// 💡 新增：触发下载逻辑
const downloadReport = () => {
  if (latestReportId.value) {
    // 创建一个隐藏的 a 标签触发下载，避免被浏览器当作恶意弹窗拦截
    const link = document.createElement('a');
    link.href = `http://127.0.0.1:8000/api/v1/report/download/${latestReportId.value}`;
    link.setAttribute('download', ''); // 提示浏览器这是下载请求
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};

// 💡 新增：携带参数跳转信用页，实现“有意义的跳转”
const jumpToCredit = () => {
  router.push({ path: '/credit', query: { id: currentPlayerId } });
};

const formatScore = (val) => {
  return typeof val === 'number' ? val.toFixed(4) : val;
};

const rawModules = [
  { icon: '🕸️', title: '风险溯源拓扑', desc: '利用GAT图神经网络找出污染源与传播路径', route: '/trace' },
  { icon: '🛡️', title: '跨平台信用评级', desc: '异构数据打分，生成用户综合游戏信用画像', route: '/credit' },
  { icon: '🎭', title: '阴阳怪气分析', desc: '调用 NLP 引擎深度识别隐藏嘲讽', route: '/detect' },
  { icon: '🎮', title: '言行不一检测', desc: '比对行为流与文本流，定位异常消极行为', route: '/behavior' }
];

const processedModules = reactive([...rawModules]);
const goToModule = (path) => { router.push(path); };
</script>

<style scoped>
/* 保持所有样式不变... */
.dashboard-container { padding: 30px 40px; background-color: #f8fafc; min-height: 100vh; color: #334155; font-family: 'Inter', sans-serif;}
.dashboard-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; }
.header-left h1 { font-size: 2rem; font-weight: 800; color: #0f172a; margin: 0 0 8px 0; }
.header-left p { font-size: 0.95rem; color: #64748b; margin: 0; }
.status-online { color: #10b981; font-weight: 600; }
.header-right { display: flex; gap: 20px; }
.stat-badge { background: #ffffff; padding: 12px 24px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); font-size: 0.9rem; color: #64748b; font-weight: 500; }
.stat-badge span { display: block; font-size: 1.5rem; font-weight: 800; color: #0ea5e9; margin-top: 4px; }
.stat-badge.alert span { color: #ef4444; }
.demo-section { background: #ffffff; border-radius: 20px; padding: 30px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 40px; }
.section-title h2 { font-size: 1.5rem; color: #0f172a; margin: 0 0 5px 0; }
.section-title p { color: #64748b; margin: 0 0 25px 0; }
.demo-workspace { display: flex; gap: 30px; height: 400px; }
.upload-area { flex: 1; position: relative; border: 2px dashed #cbd5e1; border-radius: 16px; background: #f1f5f9; display: flex; align-items: center; justify-content: center; overflow: hidden; transition: all 0.3s ease; }
.upload-area:hover { border-color: #0ea5e9; background: #e0f2fe; }
.upload-area.has-file { border: none; background: #e2e8f0; }
.file-input { position: absolute; width: 100%; height: 100%; opacity: 0; cursor: pointer; z-index: 10; }
.upload-placeholder { text-align: center; pointer-events: none; }
.upload-icon { font-size: 3rem; margin-bottom: 15px; }
.upload-placeholder h3 { color: #334155; margin: 0 0 5px 0; }
.video-preview { width: 100%; height: 100%; position: relative; display: flex; flex-direction: column; }
.preview-player { width: 100%; height: calc(100% - 60px); object-fit: contain; }
.start-btn { height: 60px; border-radius: 0 0 16px 16px; font-size: 1.1rem; z-index: 11; }
.analysis-panel { flex: 1; background: #ffffff; border-radius: 16px; display: flex; flex-direction: column; overflow: hidden; border: 1px solid #e2e8f0; }
.panel-header { background: #f8fafc; color: #334155; padding: 12px 20px; font-size: 0.95rem; font-weight: 700; border-bottom: 1px solid #e2e8f0; }
.log-container { flex: 1; padding: 20px; overflow-y: auto; font-family: 'Consolas', 'Courier New', monospace; font-size: 0.9rem; background: #fdfdfd; }
.empty-log { color: #94a3b8; text-align: center; margin-top: 50px; }
.log-item.info .text { color: #64748b; }
.log-item.process .text { color: #0ea5e9; font-weight: 500;}
.log-item.warn .text { color: #ea580c; font-weight: bold; }
.log-item.success .text { color: #10b981; font-weight: bold; }
.result-summary { padding: 20px; border-top: 1px dashed #cbd5e1; }
.result-summary h4 { margin: 0 0 10px 0; font-size: 1.05rem; }
.result-summary .danger { color: #ef4444; }
.result-summary .success { color: #10b981; }
.result-tags { display: flex; gap: 10px; margin-bottom: 15px; }
.tag { padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; }
.tag-sarcasm { background: rgba(14, 165, 233, 0.1); color: #0284c7; border: 1px solid #38bdf8; }
.tag-behavior { background: rgba(245, 158, 11, 0.2); color: #d97706; border: 1px solid #f59e0b; }
.tag-slang { background: rgba(16, 185, 129, 0.2); color: #059669; border: 1px solid #10b981; }
.modules-section { margin-top: 20px; }
.sub-title { font-size: 1.3rem; color: #0f172a; margin-bottom: 20px; }
.modules-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
.module-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 24px; display: flex; align-items: flex-start; gap: 16px; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
.module-card:hover { transform: translateY(-4px); box-shadow: 0 12px 20px -8px rgba(14, 165, 233, 0.3); border-color: #bae6fd; }
.card-icon { font-size: 2rem; background: #f0f9ff; padding: 12px; border-radius: 12px; }
.card-content h3 { font-size: 1.1rem; color: #0f172a; margin: 0 0 6px 0; }
.card-content p { font-size: 0.85rem; color: #64748b; margin: 0; line-height: 1.4; }
.card-arrow { margin-left: auto; color: #94a3b8; font-size: 1.2rem; transition: transform 0.2s; }
.module-card:hover .card-arrow { color: #0ea5e9; transform: translateX(4px); }
.btn-primary { background: #0ea5e9; color: #fff; border: none; cursor: pointer; font-weight: 600; transition: background 0.2s; }
.btn-primary:hover:not(:disabled) { background: #0284c7; }
.btn-primary:disabled { background: #94a3b8; cursor: not-allowed; }
.btn-text { background: transparent; border: none; color: #38bdf8; cursor: pointer; padding: 0; font-size: 0.9rem; }
.btn-text:hover { text-decoration: underline; }

.progress-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 60px;
  background: rgba(15, 23, 42, 0.9);
  border-radius: 0 0 16px 16px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0 20px;
  z-index: 12;
  backdrop-filter: blur(4px);
}
.progress-text { color: #38bdf8; font-size: 0.9rem; font-weight: 600; margin-bottom: 8px; letter-spacing: 0.5px; }
.progress-track { width: 100%; height: 6px; background: rgba(255, 255, 255, 0.2); border-radius: 4px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #0ea5e9, #38bdf8); border-radius: 4px; transition: width 0.3s ease-out; box-shadow: 0 0 10px rgba(56, 189, 248, 0.6); }
</style>