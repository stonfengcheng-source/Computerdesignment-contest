<template>
  <div class="trace-container">
    <header class="page-header">
      <div>
        <h1 class="page-title">风险溯源拓扑</h1>
        <p class="page-subtitle">通过对局 ID 深度分析网络污染源头，构建全链路风险影响拓扑图谱。</p>
      </div>
      <button class="btn-export">
        <span class="icon">📄</span> 导出溯源报告
      </button>
    </header>

    <section class="search-section card">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" v-model="matchIdInput" placeholder="输入待溯源的对局ID (例如: MATCH_888)" />
      </div>
      <button class="btn-primary" @click="generateTopology" :disabled="isAnalyzing">
        <span class="icon">🕸️</span> {{ isAnalyzing ? '引擎分析中...' : '生成对局拓扑' }}
      </button>
    </section>

    <section class="stats-grid">
      <div class="stat-card card">
        <div class="stat-header">
          <span class="icon-bg blue">🛡️</span>
          <span>检测覆盖率</span>
        </div>
        <div class="stat-body">
          <h2>99.4%</h2>
          <span class="trend success">+0.2% 与昨天相比</span>
        </div>
      </div>

      <div class="stat-card card">
        <div class="stat-header">
          <span class="icon-bg red">🚫</span>
          <span>高危污染源</span>
        </div>
        <div class="stat-body">
          <h2>12</h2>
          <span class="desc">当前活跃节点</span>
        </div>
      </div>

      <div class="stat-card card">
        <div class="stat-header">
          <span class="icon-bg purple">🕸️</span>
          <span>跨服关联度</span>
        </div>
        <div class="stat-body">
          <h2>极高</h2>
          <span class="desc">影响范围: 32个子域</span>
        </div>
      </div>
    </section>

    <section class="table-section card">
      <div class="table-header">
        <h3>历史对局溯源记录</h3>
        <div class="table-actions">
          <button class="btn-icon">🔻</button>
          <button class="btn-icon">🔄</button>
        </div>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>对局 ID</th>
              <th>检测时间</th>
              <th>核心污染源预估</th>
              <th>全链路影响人数</th>
              <th>整体风险评级</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in historyRecords" :key="record.id">
              <td class="text-primary">{{ record.match_id }}</td>
              <td>{{ record.created_at || '刚刚' }}</td>
              <td>
                <div class="user-info">
                  <div class="avatar bg-dark"></div>
                  <span>{{ record.source_player }}</span>
                </div>
              </td>
              <td class="font-bold">{{ record.affected_count }}</td>
              <td>
                <span class="badge" :class="record.risk_class === 'negative' ? 'badge-critical' : 'badge-moderate'">
                  <span class="dot"></span> {{ record.risk_level }}
                </span>
              </td>
              <td><a href="javascript:void(0)" class="link" @click="viewGraph(record)">查看图谱 ></a></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination">
        <span class="page-info">显示 1 到 10 条，共 1,248 条记录</span>
        <div class="page-controls">
          <button class="page-btn">‹</button>
          <button class="page-btn active">1</button>
          <button class="page-btn">2</button>
          <button class="page-btn">3</button>
          <button class="page-btn">›</button>
        </div>
      </div>
    </section>

    <section class="bottom-grid">
      <div class="viz-card card">
        <div class="viz-header">
          <span class="icon text-primary">🕸️</span>
          <h3>实时风险链路传播预估</h3>
        </div>
        <div class="empty-state">
          <div class="empty-icon">📈</div>
          <p>点击历史记录中的"查看图谱"以此处生成交互式传播路径模型</p>
        </div>
      </div>

      <div class="viz-card card">
        <div class="viz-header">
          <span class="icon text-primary">📊</span>
          <h3>污染分布热力图</h3>
        </div>
        <div class="heatmap-container">
          <div ref="heatmapRef" class="heatmap-chart"></div>
          <div class="heatmap-legend">
            <span>活跃热度分布</span>
            <div class="color-bar"></div>
            <div class="legend-labels">
              <span>低</span>
              <span>高</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
const matchIdInput = ref('')
const isAnalyzing = ref(false)
const historyRecords = ref([])

// 1. 页面加载时：自动从数据库拉取真实历史记录
const fetchRecords = async () => {
  try {
    const res = await axios.get('/api/v1/trace/records')
    historyRecords.value = res.data.data
  } catch (error) {
    console.error('拉取历史记录失败', error)
  }
}

// 2. 点击按钮时：调用后端核心引擎进行真实推演
const generateTopology = async () => {
  if (!matchIdInput.value.trim()) return alert('请输入对局 ID！')
  isAnalyzing.value = true
  try {
    await axios.post('/api/v1/trace/analyze', { match_id: matchIdInput.value })
    alert('溯源分析完毕！')
    matchIdInput.value = '' // 清空输入
    await fetchRecords() // 重新拉取最新表格数据
  } catch (error) {
    alert('引擎调用失败，请检查后端运行状态。')
  } finally {
    isAnalyzing.value = false
  }
}

// 3. 点击查看图谱
const viewGraph = (record) => {
  console.log('准备渲染图谱，参数:', record.match_id)
  // 这里可以触发你原有的 Echarts 渲染逻辑或打开弹窗
}

onMounted(() => {
  fetchRecords()
})
const heatmapRef = ref(null)
let chartInstance = null

const initHeatmap = () => {
  chartInstance = echarts.init(heatmapRef.value)

  // 生成模拟的波浪状散点数据，模拟设计图中的网状粒子感
  const data = []
  for (let i = 0; i < 50; i++) {
    for (let j = 0; j < 20; j++) {
      const val = Math.sin(i / 5) * Math.cos(j / 3) * 50 + 50 + Math.random() * 20
      data.push([i, j, val])
    }
  }

  chartInstance.setOption({
    backgroundColor: '#0F172A', // 深度暗蓝背景
    grid: { top: 0, right: 0, bottom: 0, left: 0 },
    xAxis: { type: 'value', show: false, min: 0, max: 49 },
    yAxis: { type: 'value', show: false, min: 0, max: 19 },
    visualMap: {
      show: false,
      min: 0,
      max: 120,
      inRange: {
        color: ['#1E3A8A', '#3B82F6', '#93C5FD', '#F472B6'] // 蓝到粉红的渐变
      }
    },
    series: [{
      type: 'scatter',
      symbolSize: function (val) { return val[2] / 15 },
      data: data,
      itemStyle: { opacity: 0.8 }
    }]
  })
}

onMounted(() => {
  initHeatmap()
  window.addEventListener('resize', () => chartInstance?.resize())
})

onUnmounted(() => {
  chartInstance?.dispose()
})
</script>

<style scoped>
.trace-container { display: flex; flex-direction: column; gap: 20px; }

/* 基础卡片 */
.card { background: var(--surface-color); border-radius: var(--radius-lg); box-shadow: var(--card-shadow); border: 1px solid var(--border-color); padding: 24px; }

/* 头部 */
.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-title { font-size: 24px; font-weight: 600; margin: 0 0 8px 0; }
.page-subtitle { color: var(--text-secondary); font-size: 14px; margin: 0; }
.btn-export { background: transparent; color: #2563EB; border: 1px solid #BFDBFE; padding: 8px 16px; border-radius: 6px; font-weight: 500; cursor: pointer; display: flex; align-items: center; gap: 8px; }
.btn-export:hover { background: #EFF6FF; }

/* 搜索区 */
.search-section { display: flex; gap: 16px; padding: 16px 24px; }
.search-box { flex: 1; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; display: flex; align-items: center; padding: 0 16px; }
.search-box input { border: none; background: transparent; width: 100%; height: 40px; outline: none; margin-left: 8px; font-size: 14px; }
.btn-primary { background: #2563EB; color: white; border: none; padding: 0 24px; border-radius: 6px; font-weight: 500; cursor: pointer; display: flex; align-items: center; gap: 8px; }

/* 指标卡片 */
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.stat-card { padding: 20px; }
.stat-header { display: flex; align-items: center; gap: 12px; font-size: 14px; color: var(--text-regular); margin-bottom: 16px; }
.icon-bg { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 16px; }
.icon-bg.blue { background: #DBEAFE; color: #2563EB; }
.icon-bg.red { background: #FEE2E2; color: #DC2626; }
.icon-bg.purple { background: #F3E8FF; color: #9333EA; }
.stat-body h2 { font-size: 32px; margin: 0 0 8px 0; color: #1E293B; }
.trend.success { color: #10B981; font-size: 13px; font-weight: 500; }
.desc { color: var(--text-secondary); font-size: 13px; }

/* 表格区 */
.table-section { padding: 0; overflow: hidden; }
.table-header { padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; }
.table-header h3 { margin: 0; font-size: 16px; color: #1E293B; }
.table-actions { display: flex; gap: 12px; }
.btn-icon { background: transparent; border: none; font-size: 16px; cursor: pointer; color: #64748B; }

.table-container { width: 100%; overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }
.data-table th { padding: 16px 24px; color: #64748B; font-weight: 500; background: #F8FAFC; border-bottom: 1px solid #E2E8F0; }
.data-table td { padding: 16px 24px; border-bottom: 1px solid #F1F5F9; color: #1E293B; vertical-align: middle; }
.text-primary { color: #2563EB; }
.font-bold { font-weight: 600; }

.user-info { display: flex; align-items: center; gap: 12px; }
.avatar { width: 32px; height: 32px; border-radius: 4px; }
.bg-dark { background: #1E293B; }
.bg-gray { background: #475569; }
.bg-light { background: #94A3B8; }

/* 状态徽章 */
.badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.dot { width: 6px; height: 6px; border-radius: 50%; }
.badge-critical { background: #FEF2F2; color: #DC2626; }
.badge-critical .dot { background: #DC2626; }
.badge-high { background: #FFF7ED; color: #EA580C; }
.badge-high .dot { background: #EA580C; }
.badge-moderate { background: #EFF6FF; color: #2563EB; }
.badge-moderate .dot { background: #2563EB; }

.link { color: #2563EB; text-decoration: none; font-size: 13px; }
.link:hover { text-decoration: underline; }

/* 分页 */
.pagination { padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; color: #64748B; font-size: 13px; }
.page-controls { display: flex; gap: 8px; }
.page-btn { background: white; border: 1px solid #E2E8F0; border-radius: 4px; min-width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #475569; }
.page-btn.active { background: #2563EB; color: white; border-color: #2563EB; }

/* 底部图表区 */
.bottom-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.viz-card { display: flex; flex-direction: column; }
.viz-header { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.viz-header h3 { margin: 0; font-size: 15px; color: #1E293B; }

.empty-state { flex: 1; background: #F8FAFC; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px; text-align: center; color: #94A3B8; }
.empty-icon { font-size: 48px; opacity: 0.5; margin-bottom: 16px; color: #CBD5E1; }

.heatmap-container { flex: 1; border-radius: 8px; overflow: hidden; position: relative; min-height: 240px; }
.heatmap-chart { width: 100%; height: 100%; position: absolute; top: 0; left: 0; }
.heatmap-legend { position: absolute; bottom: 16px; left: 16px; background: rgba(255,255,255,0.9); padding: 12px; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); width: 160px; }
.heatmap-legend > span { font-size: 12px; color: #1E293B; font-weight: 600; display: block; margin-bottom: 8px; }
.color-bar { height: 8px; background: linear-gradient(90deg, #93C5FD, #F472B6); border-radius: 4px; margin-bottom: 4px; }
.legend-labels { display: flex; justify-content: space-between; font-size: 10px; color: #64748B; }
</style>