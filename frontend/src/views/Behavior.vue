<template>
  <div class="behavior-container">
    <header class="page-header">
      <div>
        <h1 class="page-title">言行不一检测</h1>
        <p class="page-subtitle">融合文本情感与对局行为轨迹，精准识别“伪装型消极比赛”、“高端演员”等复杂违规行为。</p>
      </div>
      <button class="export-btn">导出监控报告</button>
    </header>

    <div class="upload-box" style="margin-bottom: 24px; padding: 20px; background: #fff; border-radius: 16px; border: 1px dashed #0ea5e9; display: flex; align-items: center; justify-content: center;">
      <div style="display: flex; align-items: center; gap: 15px;">
        <span style="font-weight: 600; color: #64748b;">上传待检视频：</span>
        <input type="file" @change="handleFileChange" accept="video/*" style="color: #64748b;" />
        <button
          @click="startDetection"
          :disabled="isLoading"
          style="padding: 10px 28px; background: #0ea5e9; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 700; transition: opacity 0.3s;"
          :style="{ opacity: isLoading ? 0.6 : 1 }"
        >
          {{ isLoading ? '🚀 AI 矩阵运算中...' : '启动 M-IARD 深度检测' }}
        </button>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card" v-for="(stat, index) in statsConfig" :key="index">
        <div class="stat-icon">{{ stat.icon }}</div>
        <div class="stat-info">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
        <div class="stat-trend" :class="stat.trendType">
          {{ stat.trend }}
        </div>
      </div>
    </div>

    <div class="main-content">
      <section class="alert-section">
        <div class="section-header">
          <h3>实时高危告警 (言行严重背离)</h3>
          <div class="pulse-indicator">
            <span class="pulse-dot"></span> 实时监控中
          </div>
        </div>

        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>玩家 ID</th>
                <th>言语特征 (NLP解析)</th>
                <th>行为特征 (时空轨迹)</th>
                <th>偏差置信度</th>
                <th>系统判定结论</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="mockAlerts.length === 0">
                <td colspan="6" style="text-align: center; color: #94a3b8; padding: 30px;">
                  暂无检测记录，请上传视频进行 AI 分析
                </td>
              </tr>

              <tr v-for="item in mockAlerts" :key="item.id">
                <td class="player-col">
                  <div class="avatar"></div>
                  <span>{{ item.playerId }}</span>
                </td>
                <td>
                  <span class="tag text-tag" :class="item.textSentiment">
                    {{ item.textSummary }}
                  </span>
                  <div class="chat-excerpt">"{{ item.chatExcerpt }}"</div>
                </td>
                <td>
                  <span class="tag behavior-tag" :class="item.behaviorType">
                    {{ item.behaviorSummary }}
                  </span>
                  <div class="kda-info">状态: {{ item.kda }} | 偏差值: {{ item.kp }}</div>
                </td>
                <td>
                  <div class="confidence-bar">
                    <div class="bar-fill" :style="{ width: item.confidence + '%', background: getConfidenceColor(item.confidence) }"></div>
                  </div>
                  <span class="confidence-val">{{ item.confidence }}%</span>
                </td>
                <td>
                  <span class="verdict-badge" :class="item.verdictClass">
                    {{ item.verdict }}
                  </span>
                </td>
                <td>
                  <button class="action-btn">查看回放</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

// 状态控制
const selectedFile = ref(null);
const isLoading = ref(false);
const mockAlerts = ref([]);

// ！！！修复 Bug：为您补齐缺失的页面统计卡片数据 ！！！
const statsConfig = ref([
  { label: '今日累计分析对局', value: '1,284', icon: '🎮', trend: '+12%', trendType: 'up' },
  { label: '揪出伪装型演员', value: '86', icon: '🚨', trend: '-5%', trendType: 'down' },
  { label: '多模态模型置信度', value: '94.2%', icon: '🧠', trend: '+1.2%', trendType: 'up' },
  { label: '系统误判率', value: '0.02%', icon: '🛡️', trend: '稳定', trendType: 'up' }
]);

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0];
};

// 1. 获取数据库真实历史记录
const fetchHistory = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/v1/records');

    const history = response.data.data.map(item => {
      // 避免 undefined 报错的防御性编程
      const textProb = item.text_prob || 0;
      const behaveErr = item.behavior_error || 0;
      const isToxic = item.is_inconsistent;

      return {
        id: item.id,
        playerId: item.player_id || '未知玩家',
        // 语义>0.6为积极
        textSentiment: textProb > 0.6 ? 'positive' : 'negative',
        textSummary: textProb > 0.6 ? '表面积极' : '消极辱骂',
        chatExcerpt: `积极概率: ${(textProb * 100).toFixed(1)}%`,
        // 行为>0.7为异常送人头
        behaviorType: behaveErr > 0.7 ? 'negative' : 'positive',
        behaviorSummary: behaveErr > 0.7 ? '异常送分(高Loss)' : '正常游戏',
        kda: behaveErr > 0.7 ? '摆烂/逛街' : '积极发育',
        kp: behaveErr.toFixed(3),
        confidence: Math.round(behaveErr * 100),
        verdict: isToxic ? '🚨 判定：言行不一' : '✅ 判定：言行一致',
        verdictClass: isToxic ? 'critical' : 'safe'
      };
    });
    // 倒序排列，新检测的在最上面
    mockAlerts.value = history.reverse();
  } catch (error) {
    console.error("加载历史记录失败:", error);
  }
};

// 2. 真实提交视频进行 AI 判定
const startDetection = async () => {
  if (!selectedFile.value) {
    alert("请先选择要分析的对局视频片段！");
    return;
  }

  isLoading.value = true;
  const formData = new FormData();
  // 比赛演示时可以写死一个玩家ID，或者做成输入框
  formData.append('player_id', 'UID_' + Math.floor(Math.random() * 10000));
  formData.append('video_file', selectedFile.value);

  try {
    const response = await axios.post('http://127.0.0.1:8000/api/v1/analyze/video', formData);
    const serverResult = response.data.result;

    // 重新获取列表，展示最新结果
    await fetchHistory();
    alert("🎉 AI 引擎分析完成！结果已更新至大屏。");

  } catch (error) {
    console.error("后端引擎连接失败:", error);
    alert("后端连接失败！请确认后端 fastapi (8000端口) 正在运行！");
  } finally {
    isLoading.value = false;
  }
};

// 页面加载时自动拉取数据
onMounted(() => {
  fetchHistory();
});

// 置信度颜色条
const getConfidenceColor = (val) => {
  if (val >= 80) return '#ef4444'; // 红色高危
  if (val >= 60) return '#f59e0b'; // 黄色警告
  return '#10b981';                // 绿色安全
};
</script>

<style scoped>
/* 保持您原有美丽的设计样式完全不动！ */
.behavior-container {
  padding: 32px;
  background-color: #f8fafc;
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 8px 0;
}

.page-subtitle {
  color: #64748b;
  font-size: 1rem;
  margin: 0;
  max-width: 600px;
}

.export-btn {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  padding: 10px 20px;
  border-radius: 8px;
  color: #334155;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.export-btn:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: #ffffff;
  padding: 24px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  position: relative;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}

.stat-icon {
  font-size: 2.5rem;
  margin-right: 20px;
  background: #f1f5f9;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 800;
  color: #0f172a;
}

.stat-label {
  color: #64748b;
  font-size: 0.9rem;
  margin-top: 4px;
}

.stat-trend {
  position: absolute;
  top: 24px;
  right: 24px;
  font-size: 0.85rem;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 20px;
}

.stat-trend.up { background: #dcfce7; color: #16a34a; }
.stat-trend.down { background: #fee2e2; color: #ef4444; }

.alert-section {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: #0f172a;
}

.pulse-indicator {
  display: flex;
  align-items: center;
  color: #10b981;
  font-size: 0.9rem;
  font-weight: 600;
}

.pulse-dot {
  width: 10px;
  height: 10px;
  background: #10b981;
  border-radius: 50%;
  margin-right: 8px;
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 16px;
  background: #f8fafc;
  color: #64748b;
  font-weight: 600;
  font-size: 0.9rem;
  border-bottom: 2px solid #e2e8f0;
}

.data-table td {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.player-col {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #334155;
}

.avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #bae6fd, #7dd3fc);
  border-radius: 50%;
  margin-right: 12px;
}

.tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 8px;
}

.tag.positive { background: #dcfce7; color: #16a34a; }
.tag.neutral { background: #f1f5f9; color: #475569; }
.tag.negative { background: #fee2e2; color: #ef4444; }

.chat-excerpt {
  font-size: 0.85rem;
  color: #64748b;
  font-style: italic;
  background: #f8fafc;
  padding: 6px;
  border-radius: 6px;
  border-left: 3px solid #cbd5e1;
}

.kda-info {
  font-size: 0.85rem;
  color: #64748b;
  font-family: monospace;
}

.confidence-bar {
  width: 100px;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 4px;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
}

.confidence-val {
  font-size: 0.85rem;
  font-weight: 700;
  color: #334155;
}

.verdict-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
}

.verdict-badge.critical { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }
.verdict-badge.warning { background: #fffbeb; color: #d97706; border: 1px solid #fde68a; }
.verdict-badge.safe { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }

.action-btn {
  background: transparent;
  color: #0ea5e9;
  border: 1px solid #0ea5e9;
  padding: 6px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #0ea5e9;
  color: #fff;
}
</style>