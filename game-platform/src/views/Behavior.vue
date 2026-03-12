<template>
  <div class="behavior-container">
    <header class="page-header">
      <div>
        <h1 class="page-title">言行不一检测</h1>
        <p class="page-subtitle">融合文本情感与对局行为轨迹，精准识别“伪装型消极比赛”、“高端演员”等复杂违规行为。</p>
      </div>
      <button class="export-btn">导出监控报告</button>
    </header>

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
                  <div class="kda-info">KDA: {{ item.kda }} | 参团率: {{ item.kp }}%</div>
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
import { ref } from 'vue';

// 顶部统计数据
const statsConfig = ref([
  { label: '今日扫描对局', value: '12,450', icon: '🎮', trend: '+12%', trendType: 'up' },
  { label: '言语伪装拦截', value: '843', icon: '🎭', trend: '+5%', trendType: 'up' },
  { label: '高危言行背离', value: '156', icon: '⚠️', trend: '-2%', trendType: 'down' },
  { label: '判定准确率', value: '98.2%', icon: '🎯', trend: '+0.4%', trendType: 'up' }
]);

// 模拟“言行不一”的典型案例数据
const mockAlerts = ref([
  {
    id: 1,
    playerId: 'ID: 774892_Yasuo',
    textSentiment: 'positive',
    textSummary: '积极互动',
    chatExcerpt: '我的我的，兄弟们稳住能赢，等我发育。',
    behaviorType: 'negative',
    behaviorSummary: '恶意送人头 / 塔下挂机',
    kda: '0/12/1',
    kp: 5,
    confidence: 96,
    verdict: '伪装型演员',
    verdictClass: 'critical'
  },
  {
    id: 2,
    playerId: 'ID: 992100_LeeSin',
    textSentiment: 'neutral',
    textSummary: '中立防卫',
    chatExcerpt: '哎呀卡了一下，不好意思。',
    behaviorType: 'negative',
    behaviorSummary: '野区打转 / 规避团战',
    kda: '1/3/0',
    kp: 12,
    confidence: 88,
    verdict: '隐蔽消极比赛',
    verdictClass: 'warning'
  },
  {
    id: 3,
    playerId: 'ID: 110293_Vayne',
    textSentiment: 'negative',
    textSummary: '言语暴躁',
    chatExcerpt: '辅助怎么这么菜？会不会玩？',
    behaviorType: 'positive',
    behaviorSummary: '高频输出 / 积极推进',
    kda: '15/2/8',
    kp: 85,
    confidence: 92,
    verdict: '暴躁老哥(无消极行为)',
    verdictClass: 'safe'
  },
  {
    id: 4,
    playerId: 'ID: 556721_Teemo',
    textSentiment: 'positive',
    textSummary: '友好伪装',
    chatExcerpt: '大家辛苦了，这把我的锅。',
    behaviorType: 'negative',
    behaviorSummary: '无效伤害 / 基地挂机',
    kda: '0/0/0',
    kp: 0,
    confidence: 99,
    verdict: '挂机脚本',
    verdictClass: 'critical'
  }
]);

const getConfidenceColor = (val) => {
  if (val >= 95) return '#ef4444'; // 红
  if (val >= 85) return '#f59e0b'; // 橙
  return '#10b981'; // 绿
};
</script>

<style scoped>
.behavior-container {
  padding: 32px;
  background-color: #f8fafc;
  min-height: 100%;
}

/* 头部样式 */
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

/* 统计卡片区 */
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

/* 核心表格区 */
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