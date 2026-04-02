<template>
  <div class="dashboard-container">
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">2026 深蓝卫士 - 数据总览台</h1>
        <p class="page-subtitle">基于多模态博弈大数据的网络游戏生态健康度监测与信用评级平台。引擎全时段主动防御中。</p>
      </div>
      <div class="header-right text-secondary">
        <span class="update-time">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          最后更新: {{ formattedUpdateTime }}
        </span>
      </div>
    </header>

    <section class="kpi-grid">
      <div class="kpi-card">
        <div class="card-header">
          <span class="card-title">今日游戏场均数量</span>
          <svg class="icon blue-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4m-2-2v4m10-2h.01M16 10h.01"/></svg>
        </div>
        <div class="card-body">
          <h2 class="kpi-number">12,450</h2>
          <span class="trend up">↗ 5.2%</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="card-header">
          <span class="card-title">高危违规账号封禁</span>
          <svg class="icon red-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="17" y1="8" x2="23" y2="14"/><line x1="23" y1="8" x2="17" y2="14"/></svg>
        </div>
        <div class="card-body">
          <h2 class="kpi-number">458</h2>
          <span class="trend up-danger">↗ 12.5%</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="card-header">
          <span class="card-title">风险言论总数</span>
          <svg class="icon blue-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <div class="card-body">
          <h2 class="kpi-number">3,120</h2>
          <span class="trend down">↘ 8.1%</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="card-header">
          <span class="card-title">系统日历</span>
          <svg class="icon blue-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        </div>
        <div class="card-body">
          <div class="date-group">
            <span class="year-month">{{ currentYearMonth }}</span>
            <div class="day-row">
              <h2 class="kpi-number">{{ currentDayInfo }}</h2>
              <span class="arrow-down">˅</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="charts-grid">
      <div class="chart-card">
        <div class="chart-header">
          <h3>近七日风险言论趋势</h3>
          <span class="legend-dot blue">风险指数</span>
        </div>
        <div class="chart-content" ref="barChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3>近七日高危违规趋势</h3>
          <span class="legend-dot dark">异动检测</span>
        </div>
        <div class="chart-content" ref="lineChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3>游戏中风险言论分布</h3>
          <span class="legend-text">比例</span>
        </div>
        <div class="chart-content" ref="distributionChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3>复杂语境下违规类型占比</h3>
        </div>
        <div class="chart-content" ref="pieChartRef"></div>
      </div>
    </section>

    <section class="bottom-grid">
      <div class="monitor-card card">
        <h3>专项监控数据</h3>
        <div class="progress-list">
          <div class="progress-item">
            <div class="progress-info">
              <div class="icon-box alert-box"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>
              <span class="progress-label">溯源高危预警</span>
              <span class="value text-danger">18</span>
            </div>
            <div class="progress-bar"><div class="fill danger" style="width: 18%"></div></div>
          </div>
          <div class="progress-item">
            <div class="progress-info">
              <div class="icon-box warning-box"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div>
              <span class="progress-label">行为异常波动</span>
              <span class="value text-primary">42</span>
            </div>
            <div class="progress-bar"><div class="fill primary" style="width: 42%"></div></div>
          </div>
          <div class="progress-item">
            <div class="progress-info">
              <div class="icon-box safe-box"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg></div>
              <span class="progress-label">生态健康指数</span>
              <span class="value text-success">94%</span>
            </div>
            <div class="progress-bar"><div class="fill success" style="width: 94%"></div></div>
          </div>
        </div>
        <div class="system-notice">
          "系统正在深度识别垂直游戏领域的黑话体系与阴阳怪气语境，当前复杂异构数据集已更新至最新版本。"
        </div>
      </div>

      <div class="engine-section">
        <div class="mini-cards">
          <div class="mini-card card">
            <div class="mini-header"><span>新型黑话</span> <span class="tag active">ACTIVE</span></div>
            <h2 class="mini-number">1,402</h2>
            <p class="sub">今日毫秒级拦截</p>
            <div class="mini-chart" ref="miniChart1"></div>
          </div>
          <div class="mini-card card">
            <div class="mini-header"><span>关系流违规</span> <span class="tag danger">OIGO</span></div>
            <h2 class="mini-number">892</h2>
            <p class="sub">社交链路阻断</p>
            <div class="mini-chart" ref="miniChart2"></div>
          </div>
          <div class="mini-card card">
            <div class="mini-header"><span>阴阳怪气</span> <span class="tag normal">NORMAL</span></div>
            <h2 class="mini-number">544</h2>
            <p class="sub">多模态语义捕获</p>
            <div class="mini-chart" ref="miniChart3"></div>
          </div>
        </div>

        <div class="engine-banner">
          <div class="banner-content">
            <h2>多模态语义与行为分析引擎</h2>
            <p>首创“关系流+文本流”双轨机制。深度融合 BERT 语义理解、GAT 社交图谱与 XGBoost 决策体系。不仅精准识别阴阳怪气，更独家生成“风险溯源拓扑图”，直击污染源头，建立用户信用评级体系。</p>
            <div class="banner-actions">
              <button class="btn-white">查看溯源拓扑图</button>
              <button class="btn-outline">引擎设置</button>
            </div>
          </div>
          <div class="banner-ring">
            <div class="ring-circle">
              <span class="ring-score">99</span>
              <span class="ring-label">ACCURACY</span>
            </div>
          </div>
          <div class="status-badge"><span class="dot-green"></span> 毫秒级主动防御就绪</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import * as echarts from 'echarts'

const barChartRef = ref(null)
const lineChartRef = ref(null)
const distributionChartRef = ref(null)
const pieChartRef = ref(null)
const miniChart1 = ref(null)
const miniChart2 = ref(null)
const miniChart3 = ref(null)

let charts = []

// 【核心修复】：全局响应式时间变量必须放在函数外
const now = ref(new Date())
let timer = null

// 动态格式化最后更新时间
const formattedUpdateTime = computed(() => {
  const y = now.value.getFullYear()
  const m = String(now.value.getMonth() + 1).padStart(2, '0')
  const d = String(now.value.getDate()).padStart(2, '0')
  const hh = String(now.value.getHours()).padStart(2, '0')
  const mm = String(now.value.getMinutes()).padStart(2, '0')
  const ss = String(now.value.getSeconds()).padStart(2, '0')
  return `${y}-${m}-${d} ${hh}:${mm}:${ss}`
})

// 动态日历：年月
const currentYearMonth = computed(() => {
  return `${now.value.getFullYear()}年${now.value.getMonth() + 1}月`
})

// 动态日历：日期与星期
const currentDayInfo = computed(() => {
  const days = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return `${now.value.getDate()}日 ${days[now.value.getDay()]}`
})

// 生成近七天的日期数组 (格式: MM/DD)
const getLast7Days = () => {
  const days = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i) // 依次推算前6天到今天
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    days.push(`${month}/${day}`)
  }
  return days
}

const initCharts = () => {
  if (!barChartRef.value) return; // 防止DOM未加载完毕导致报错白屏

  const barChart = echarts.init(barChartRef.value)
  barChart.setOption({
    color: ['#8BA3E8'], grid: { top: 20, right: 0, bottom: 0, left: 0 },
    xAxis: { type: 'category', show: false, data: ['1','2','3','4','5','6','7'] },
    yAxis: { type: 'value', show: false },
    series: [{
      data: [40, 60, 45, 80, 55, 70, 95], type: 'bar', barWidth: '85%',
      itemStyle: { borderRadius: [4, 4, 0, 0], color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#6B8DF2' }, { offset: 1, color: '#C6D6FF' }]) }
    }]
  }); charts.push(barChart)

  const lineChart = echarts.init(lineChartRef.value)
  lineChart.setOption({
    grid: { top: 20, right: 10, bottom: 20, left: 10 },
    xAxis: {
      type: 'category',
      // 👇 这里替换为动态获取的日期数组
      data: getLast7Days(),
      axisLine: {show: false},
      axisTick: {show: false},
      axisLabel: {color: '#64748B', fontSize: 12}
    },
    yAxis: { type: 'value', show: false },
    series: [{ data: [10, 20, 15, 60, 10, 80, 30], type: 'line', smooth: true, symbol: 'none', lineStyle: { color: '#64748B', width: 2 } }]
  }); charts.push(lineChart)

  const distChart = echarts.init(distributionChartRef.value)
  distChart.setOption({
    grid: { top: 20, right: 10, bottom: 20, left: 10 },
    xAxis: { type: 'category', data: ['0','1','2','3','4','5','6','7','8'], axisLine: {lineStyle: {color: '#E2E8F0'}}, axisTick: {show: true, lineStyle: {color: '#E2E8F0'}}, axisLabel: {color: '#64748B', fontSize: 12} },
    yAxis: { type: 'value', show: false },
    series: [{ data: [50, 20, 40, 38, 90, 30, 20, 18, 5], type: 'line', symbol: 'none', lineStyle: { color: '#22C55E', width: 1.5 } }]
  }); charts.push(distChart)

  const pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    color: ['#8BA3E8'],
    series: [{ type: 'pie', radius: ['0%', '70%'], label: { color: '#64748B', fontSize: 12, formatter: '{b}\n{c}' }, labelLine: { lineStyle: { color: '#CBD5E1' } }, itemStyle: { borderColor: '#fff', borderWidth: 2 }, data: [{ value: 404, name: '阴阳怪气' }, { value: 201, name: '嘲讽攻击' }, { value: 195, name: '新型黑话' }] }]
  }); charts.push(pieChart)

  const miniOptions = (color) => ({ grid: { top: 5, right: 0, bottom: 0, left: 0 }, xAxis: { type: 'category', show: false, data: ['1','2','3','4','5'] }, yAxis: { type: 'value', show: false }, series: [{ type: 'bar', data: [3, 4, 3, 5, 2], itemStyle: { color: color }, barWidth: '80%' }] })

  if(miniChart1.value) { const m1 = echarts.init(miniChart1.value); m1.setOption(miniOptions('#C6D6FF')); charts.push(m1); }
  if(miniChart2.value) { const m2 = echarts.init(miniChart2.value); m2.setOption(miniOptions('#FECACA')); charts.push(m2); }
  if(miniChart3.value) { const m3 = echarts.init(miniChart3.value); m3.setOption(miniOptions('#E2E8F0')); charts.push(m3); }
}

onMounted(() => {
  nextTick(() => { setTimeout(initCharts, 100) }) // 确保渲染后再加载图表
  window.addEventListener('resize', () => charts.forEach(c => c.resize()))

  // 启动时间定时器
  timer = setInterval(() => {
    now.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  charts.forEach(c => c.dispose())
  // 清除定时器，防止内存泄漏
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.dashboard-container { display: flex; flex-direction: column; gap: 24px; font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif; color: #1E293B; background-color: #F8FAFC; }
.card, .kpi-card, .chart-card { background: #FFFFFF; border-radius: 12px; box-shadow: 0 4px 24px rgba(0, 0, 0, 0.03); border: none; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;}
.page-title { font-size: 24px; font-weight: 600; margin: 0 0 6px 0; letter-spacing: 0.5px;}
.page-subtitle { color: #64748B; font-size: 14px; margin: 0; }
.update-time { display: flex; align-items: center; gap: 6px; background: #F1F5F9; color: #475569; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 500;}

.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.kpi-card { padding: 24px; display: flex; flex-direction: column; gap: 16px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-size: 14px; color: #64748B; font-weight: 500;}
.icon { width: 22px; height: 22px; }
.icon-sm { width: 14px; height: 14px; }
.blue-icon { color: #3B82F6; } .gray-icon { color: #64748B; } .red-icon { color: #EF4444; }

.card-body { display: flex; align-items: baseline; gap: 12px; }
.kpi-number { font-size: 36px; font-weight: 700; margin: 0; line-height: 1; letter-spacing: -0.5px;}
.trend { font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 2px;}
.trend.up, .trend.down { color: #3B82F6; } .trend.up-danger { color: #EF4444; }

.date-group { display: flex; flex-direction: column; gap: 4px; }
.year-month { font-size: 13px; color: #64748B; }
.day-row { display: flex; align-items: center; justify-content: space-between; width: 100%;}
.day-row .kpi-number { font-size: 24px; }
.arrow-down { color: #3B82F6; font-weight: bold; }

.charts-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }
.chart-card { padding: 24px; height: 320px; display: flex; flex-direction: column; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.chart-header h3 { font-size: 16px; font-weight: 600; margin: 0; color: #1E293B;}
.legend-dot { font-size: 12px; color: #64748B; display: flex; align-items: center; gap: 6px;}
.legend-dot::before { content: ''; width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.legend-dot.blue::before { background-color: #3B82F6; } .legend-dot.dark::before { background-color: #475569; }
.legend-text { font-size: 12px; color: #64748B; }
.chart-content { flex: 1; width: 100%; }

.bottom-grid { display: grid; grid-template-columns: 1fr 2.5fr; gap: 24px; }
.monitor-card { padding: 24px; display: flex; flex-direction: column; }
.monitor-card h3 { font-size: 16px; font-weight: 600; margin: 0 0 24px 0; }
.progress-list { display: flex; flex-direction: column; gap: 24px; flex: 1; }
.progress-item { display: flex; flex-direction: column; gap: 10px; }
.progress-info { display: flex; align-items: center; font-size: 14px; font-weight: 500;}
.icon-box { width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; margin-right: 12px; font-size: 14px;}
.icon-box svg { width: 16px; height: 16px; }
.alert-box { background: #FEE2E2; color: #EF4444; } .warning-box { background: #EFF6FF; color: #3B82F6;} .safe-box { background: #DCFCE7; color: #22C55E;}
.progress-label { color: #475569; }
.progress-info .value { margin-left: auto; font-weight: 700; font-size: 16px;}
.text-danger { color: #EF4444; } .text-primary { color: #3B82F6; } .text-success { color: #22C55E; }
.progress-bar { height: 6px; background: #F1F5F9; border-radius: 3px; }
.progress-bar .fill { height: 100%; border-radius: 3px; }
.fill.danger { background: #EF4444; } .fill.primary { background: #3B82F6; } .fill.success { background: #22C55E; }
.system-notice { margin-top: 24px; font-size: 13px; color: #94A3B8; background: #F8FAFC; padding: 16px; border-radius: 8px; line-height: 1.5; }

.engine-section { display: flex; flex-direction: column; gap: 24px; }
.mini-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.mini-card { padding: 20px; display: flex; flex-direction: column;}
.mini-header { display: flex; justify-content: space-between; align-items: center; font-size: 14px; margin-bottom: 16px; font-weight: 500; color: #1E293B;}
.tag { font-size: 10px; padding: 4px 8px; border-radius: 12px; font-weight: 700; letter-spacing: 0.5px;}
.tag.active { background: #EFF6FF; color: #2563EB; } .tag.danger { background: #FEF2F2; color: #DC2626; } .tag.normal { background: #F1F5F9; color: #64748B; }
.mini-number { font-size: 28px; font-weight: 700; margin: 0; }
.mini-card .sub { font-size: 12px; color: #94A3B8; margin: 4px 0 16px 0; }
.mini-chart { height: 40px; width: 100%; margin-top: auto;}

.engine-banner { background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%); color: #fff; border-radius: 16px; padding: 32px 40px; display: flex; align-items: center; justify-content: space-between; position: relative; box-shadow: 0 10px 30px rgba(37, 99, 235, 0.2); }
.banner-content { max-width: 55%; z-index: 2; }
.banner-content h2 { font-size: 22px; margin: 0 0 12px 0; font-weight: 600;}
.banner-content p { font-size: 14px; color: #DBEAFE; line-height: 1.6; margin: 0 0 24px 0; font-weight: 300;}
.banner-actions { display: flex; gap: 16px; }
.btn-white { background: #ffffff; color: #1D4ED8; border: none; padding: 10px 24px; border-radius: 6px; font-size: 14px; cursor: pointer; font-weight: 600; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}
.btn-outline { background: rgba(255,255,255,0.1); color: #fff; border: 1px solid rgba(255,255,255,0.3); padding: 10px 24px; border-radius: 6px; font-size: 14px; cursor: pointer; }
.banner-ring { z-index: 2; margin-right: 60px; }
.ring-circle { width: 120px; height: 120px; border-radius: 50%; border: 8px solid rgba(255,255,255,0.2); border-top-color: #ffffff; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.ring-score { font-size: 36px; font-weight: 700; line-height: 1;}
.ring-label { font-size: 12px; color: #DBEAFE; margin-top: 4px; letter-spacing: 1px;}
.status-badge { position: absolute; bottom: -16px; right: 40px; background: #ffffff; color: #1E293B; font-size: 13px; padding: 8px 16px; border-radius: 20px; font-weight: 600; display: flex; align-items: center; gap: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.dot-green { width: 8px; height: 8px; background: #22C55E; border-radius: 50%; }
</style>