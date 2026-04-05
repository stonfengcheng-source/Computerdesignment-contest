<template>
  <div class="trace-container">
    <header class="page-header">
      <div>
        <h1 class="page-title">风险溯源拓扑</h1>
        <p class="page-subtitle">通过对局 ID 深度分析网络污染源头，构建全链路风险影响拓扑图谱。</p>
      </div>
      <button class="btn-export">
        导出溯源报告
      </button>
    </header>

    <section class="stats-grid">
      <div class="stat-card card">
        <div class="stat-header">
          <span class="icon-bg blue"></span>
          <span>检测覆盖率</span>
        </div>
        <div class="stat-body">
          <h2>99.4%</h2>
          <span class="trend success">+0.2% 与昨天相比</span>
        </div>
      </div>

      <div class="stat-card card">
        <div class="stat-header">
          <span class="icon-bg red"></span>
          <span>高危污染源</span>
        </div>
        <div class="stat-body">
          <h2>{{ historyRecords.length || 12 }}</h2>
          <span class="desc">当前活跃节点</span>
        </div>
      </div>

      <div class="stat-card card">
        <div class="stat-header">
          <span class="icon-bg purple"></span>
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
          <button class="btn-icon" @click="fetchRecords">刷新数据</button>
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
        <span class="page-info">显示 1 到 10 条记录</span>
        <div class="page-controls">
          <button class="page-btn">‹</button>
          <button class="page-btn active">1</button>
          <button class="page-btn">›</button>
        </div>
      </div>
    </section>

    <section class="bottom-grid">
      <div class="viz-card card" style="min-height: 400px; display: flex; flex-direction: column;">
        <div class="viz-header">
          <h3>实时风险链路传播预估</h3>
        </div>

        <div v-show="!showGraph" class="empty-state" style="flex: 1;">
          <p>点击历史记录中的"查看图谱"以此处生成交互式传播路径模型</p>
        </div>

        <div v-show="showGraph" ref="traceGraphRef" style="flex: 1; width: 100%; min-height: 350px;"></div>
      </div>

      <div class="viz-card card" style="min-height: 400px; display: flex; flex-direction: column;">
        <div class="viz-header">
          <h3>污染分布热力图</h3>
        </div>

        <div v-show="!showGraph" class="empty-state" style="flex: 1;">
          <p>等待对局数据注入...</p>
        </div>

        <div v-show="showGraph" class="heatmap-container" style="flex: 1; width: 100%; min-height: 350px;">
          <div ref="heatmapRef" class="heatmap-chart"></div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

const matchIdInput = ref('')
const isAnalyzing = ref(false)
const historyRecords = ref([])

// 1. 拉取记录
const fetchRecords = async () => {
  try {
    const res = await axios.get('/api/v1/trace/records')
    historyRecords.value = res.data.data
  } catch (error) {
    console.error('拉取历史记录失败', error)
  }
}

// 2. 生成拓扑
const generateTopology = async () => {
  if (!matchIdInput.value.trim()) return alert('请输入对局 ID！')
  isAnalyzing.value = true
  try {
    await axios.post('/api/v1/trace/analyze', { match_id: matchIdInput.value })
    alert('溯源分析完毕！')
    matchIdInput.value = ''
    await fetchRecords()
  } catch (error) {
    alert('引擎调用失败，请检查后端运行状态。')
  } finally {
    isAnalyzing.value = false
  }
}

const showGraph = ref(false)
const traceGraphRef = ref(null)
let graphChartInstance = null

const heatmapRef = ref(null)
let heatmapChartInstance = null

// 🌟 终极修复：右侧图例 + 高对比分段色块
// 🌟 完美融合版：保留高级边框与布局，严格修复 Echarts 数据类型以重现渐变色差！
const updateHeatmapWithRealData = (timeline) => {
  if (!heatmapChartInstance) {
    heatmapChartInstance = echarts.init(heatmapRef.value)
  }
  if (!timeline || timeline.length === 0) return

  const players = [...new Set(timeline.map(t => t.user))]
  // 恢复极简数字编号，去掉“第X句”，防止拥挤和倾斜
  const xAxisData = timeline.map((_, i) => i + 1)

  // 🌟 致命修复：强制使用 Number()！绝不把 text 塞进图表数据里，保证渐变色带绝对生效！
  const heatmapData = timeline.map((t, index) => {
    return [index, players.indexOf(t.user), Number((t.toxicity * 100).toFixed(0))]
  })

  heatmapChartInstance.setOption({
    backgroundColor: '#ffffff',
    tooltip: {
      enterable: true,
      position: 'top',
      backgroundColor: '#ffffff',
      borderColor: '#E2E8F0',
      textStyle: { color: '#1E293B', fontSize: 13 },
      formatter: function (params) {
        // 🌟 从外部 timeline 读取原话，保持界面绝美
        const originalData = timeline[params.dataIndex];
        return `
          <div style="padding: 4px;">
            <div style="color: #64748B; margin-bottom: 4px;">发言顺位: 第 ${params.data[0] + 1} 句</div>
            <div style="font-weight: 600; color: #1E293B; margin-bottom: 6px;">${originalData.user}</div>
            <div style="color: #334155; margin-bottom: 8px; font-style: italic; background: #F8FAFC; padding: 4px; border-radius: 4px;">"${originalData.text}"</div>
            <div style="color: ${params.data[2] > 60 ? '#DC2626' : '#10B981'}; font-weight: bold;">
              毒性判定: ${params.data[2]}%
            </div>
          </div>
        `
      }
    },
    // 右侧留出 80px 放色带，底部留 40px 放时间线，完美互不干扰
    grid: { top: 30, right: 80, bottom: 40, left: 130 },
    xAxis: {
      type: 'category',
      data: xAxisData,
      name: '发言顺序',
      nameTextStyle: { color: '#94A3B8' },
      splitArea: { show: true },
      // 自动计算间隔，取消丑陋的倾斜
      axisLabel: { color: '#64748B', interval: 'auto' },
      axisLine: { lineStyle: { color: '#E2E8F0' } }
    },
    yAxis: {
      type: 'category',
      data: players,
      axisLabel: { width: 110, overflow: 'truncate', color: '#334155', fontWeight: 500 },
      splitArea: { show: true },
      axisLine: { lineStyle: { color: '#E2E8F0' } }
    },
    // 🌟 完美保留你设定的竖向渐变色带
    visualMap: {
      type: 'continuous',
      orient: 'vertical',
      right: 0,
      top: 'center',
      min: 0,
      max: 100,
      calculable: true,
      itemWidth: 15,
      itemHeight: 120,
      textStyle: { color: '#64748B', fontSize: 12 },
      inRange: {
        // 极浅灰白 -> 浅红 -> 鲜红 -> 深红
        color: ['#F8FAFC', '#FCA5A5', '#EF4444', '#991B1B']
      }
    },
    series: [{
      type: 'heatmap',
      data: heatmapData,
      label: {
        show: true,
        color: '#1E293B',
        fontSize: 12,
        formatter: (p) => p.data[2] > 0 ? p.data[2] : ''
      },
      // 完美保留你设定的高级纯白边框
      itemStyle: { borderColor: '#ffffff', borderWidth: 2 }
    }]
  }, true)

  setTimeout(() => { heatmapChartInstance.resize() }, 100)
}

// 🌟 知识图谱：带鼠标悬浮窗滚动 + 点击聚光灯高亮
const viewGraph = async (record) => {
  try {
    const res = await axios.get(`/api/v1/trace/graph/${record.match_id}`)
    const { nodes, edges, timeline } = res.data.data

    if (!nodes || nodes.length === 0) {
      alert("该对局没有图谱数据！")
      return
    }

    showGraph.value = true
    await nextTick()

    if (!graphChartInstance) {
      graphChartInstance = echarts.init(traceGraphRef.value)
    }

    graphChartInstance.setOption({
      backgroundColor: '#ffffff',
      tooltip: {
        enterable: true, // 允许鼠标进入滚动
        trigger: 'item',
        backgroundColor: '#ffffff',
        borderColor: '#E2E8F0',
        textStyle: { color: '#1E293B' },
        extraCssText: 'box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-radius: 8px;',
        formatter: function (params) {
          if (params.dataType === 'node' && params.data.history) {
            let historyHtml = params.data.history.map((h, i) => `
              <div style="margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px dashed #E2E8F0; font-size: 13px;">
                <span style="color: ${h.score > 0.6 ? '#DC2626' : '#2563EB'}; font-weight: bold; display: inline-block; width: 45px;">[${(h.score*100).toFixed(0)}%]</span>
                <span style="color: #475569; white-space: normal; word-break: break-all;">${h.text}</span>
              </div>
            `).join('');

            return `
              <div style="max-height: 280px; overflow-y: auto; padding: 6px; min-width: 280px; pointer-events: auto;">
                <div style="font-size: 15px; font-weight: bold; margin-bottom: 14px; color: ${params.data.color}; border-bottom: 2px solid ${params.data.color}; padding-bottom: 6px;">
                  🎯 节点主体：${params.data.name}
                </div>
                ${historyHtml}
              </div>
            `;
          }
        }
      },
      series: [{
        type: 'graph',
        layout: 'force',
        data: nodes.map(n => ({
          id: n.id,
          name: n.label,
          symbolSize: n.size,
          itemStyle: { color: n.color },
          history: n.history
        })),
        edges: edges.map(e => ({
          source: e.source,
          target: e.target,
          lineStyle: { width: 1.5, color: '#CBD5E1' }
        })),
        roam: true,
        label: { show: true, position: 'bottom', color: '#1E293B', fontWeight: 500 },
        // 🌟 聚光灯：鼠标放上去，周边节点高亮，其他变暗！
        emphasis: {
          focus: 'adjacency',
          lineStyle: { width: 4 },
          label: { show: true, fontSize: 14, fontWeight: 'bold' }
        },
        force: {
          repulsion: 500,
          edgeLength: 120
        }
      }]
    }, true)

    updateHeatmapWithRealData(timeline)

  } catch (error) {
    console.error('获取图谱失败', error)
    alert('获取图谱失败，请检查后端 API')
  }
}

onMounted(() => {
  fetchRecords()
  window.addEventListener('resize', () => {
    graphChartInstance?.resize()
    heatmapChartInstance?.resize()
  })
})

onUnmounted(() => {
  graphChartInstance?.dispose()
  heatmapChartInstance?.dispose()
})
</script>

<style scoped>
/* 绝对没有动你的任何原版 UI 和 CSS */
.trace-container { display: flex; flex-direction: column; gap: 20px; }

.card { background: var(--surface-color); border-radius: var(--radius-lg); box-shadow: var(--card-shadow); border: 1px solid var(--border-color); padding: 24px; }

.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-title { font-size: 24px; font-weight: 600; margin: 0 0 8px 0; }
.page-subtitle { color: var(--text-secondary); font-size: 14px; margin: 0; }
.btn-export { background: transparent; color: #2563EB; border: 1px solid #BFDBFE; padding: 8px 16px; border-radius: 6px; font-weight: 500; cursor: pointer; display: flex; align-items: center; gap: 8px; }
.btn-export:hover { background: #EFF6FF; }

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

.table-section { padding: 0; overflow: hidden; }
.table-header { padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; }
.table-header h3 { margin: 0; font-size: 16px; color: #1E293B; }
.table-actions { display: flex; gap: 12px; }
.btn-icon { background: transparent; border: 1px solid #E2E8F0; padding: 4px 12px; border-radius: 4px; font-size: 13px; cursor: pointer; color: #64748B; }

.table-container { width: 100%; overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }
.data-table th { padding: 16px 24px; color: #64748B; font-weight: 500; background: #F8FAFC; border-bottom: 1px solid #E2E8F0; }
.data-table td { padding: 16px 24px; border-bottom: 1px solid #F1F5F9; color: #1E293B; vertical-align: middle; }
.text-primary { color: #2563EB; }
.font-bold { font-weight: 600; }

.user-info { display: flex; align-items: center; gap: 12px; }

.badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.dot { width: 6px; height: 6px; border-radius: 50%; }
.badge-critical { background: #FEF2F2; color: #DC2626; }
.badge-critical .dot { background: #DC2626; }
.badge-moderate { background: #EFF6FF; color: #2563EB; }
.badge-moderate .dot { background: #2563EB; }

.link { color: #2563EB; text-decoration: none; font-size: 13px; }
.link:hover { text-decoration: underline; }

.pagination { padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; color: #64748B; font-size: 13px; }
.page-controls { display: flex; gap: 8px; }
.page-btn { background: white; border: 1px solid #E2E8F0; border-radius: 4px; min-width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #475569; }
.page-btn.active { background: #2563EB; color: white; border-color: #2563EB; }

.bottom-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.viz-card { display: flex; flex-direction: column; }
.viz-header { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.viz-header h3 { margin: 0; font-size: 15px; color: #1E293B; }

.empty-state { flex: 1; background: #F8FAFC; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px; text-align: center; color: #94A3B8; }

.heatmap-container { flex: 1; border-radius: 8px; position: relative; min-height: 400px; }
.heatmap-chart { width: 100%; height: 100%; position: absolute; top: 0; left: 0; }
</style>