<template>
  <div class="dashboard-container">
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">数据总览台</h1>
        <p class="page-subtitle">欢迎回来。系统正在实时净化游戏网络环境，当前运行状态良好。</p>
      </div>
      <div class="header-right text-secondary">
        <span class="update-time">🕒 最后更新: 2024-05-24 14:30:22</span>
      </div>
    </header>

    <section class="kpi-grid">
      <div class="kpi-card">
        <div class="card-header">
          <span class="card-title">今日游戏场均数量</span>
          <span class="icon blue-icon">🎮</span>
        </div>
        <div class="card-body">
          <h2 class="kpi-number">12,842</h2>
          <span class="trend up">↗ 4.2%</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="card-header">
          <span class="card-title">言行不一致数</span>
          <span class="icon gray-icon">🎭</span>
        </div>
        <div class="card-body">
          <h2 class="kpi-number">458</h2>
          <span class="trend up-danger">↗ 12.5%</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="card-header">
          <span class="card-title">风险言论总数</span>
          <span class="icon red-icon">🛡️</span>
        </div>
        <div class="card-body">
          <h2 class="kpi-number">3,120</h2>
          <span class="trend down">↘ 8.1%</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="card-header">
          <span class="card-title">日历</span>
          <span class="icon blue-icon">📅</span>
        </div>
        <div class="card-body">
          <div class="date-group">
            <span class="year-month">2024年5月</span>
            <div class="day-row">
              <h2 class="kpi-number">24日 星期五</h2>
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
          <h3>近七日言行不一致趋势</h3>
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
          <h3>游戏中各类风险言论占比</h3>
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
              <div class="icon-box alert-box" style="background: #FEE2E2; color: #DC2626;">🚨</div>
              <span class="progress-label">高危预警 (严重破坏生态)</span>
              <span class="value text-danger">18</span>
            </div>
            <div class="progress-bar"><div class="fill danger" style="width: 18%; background: #EF4444;"></div></div>
          </div>
          <div class="progress-item">
            <div class="progress-info">
              <div class="icon-box warning-box" style="background: #DCFCE7; color: #10B981;">⚠️</div>
              <span class="progress-label">中低危 (轻微阴阳怪气)</span>
              <span class="value text-success" style="color: #10B981;">42</span>
            </div>
            <div class="progress-bar"><div class="fill success" style="width: 42%; background: #10B981;"></div></div>
          </div>
          <div class="progress-item">
            <div class="progress-info">
              <div class="icon-box safe-box" style="background: #D1FAE5; color: #059669;">🛡️</div>
              <span class="progress-label">风气健康</span>
              <span class="value text-success" style="color: #059669;">94%</span>
            </div>
            <div class="progress-bar"><div class="fill success" style="width: 94%; background: #059669;"></div></div>
          </div>
        </div>
        <div class="system-notice">
          "系统正在深度识别垂直游戏领域的黑话体系"
        </div>
      </div>

      <div class="engine-section">
        <div class="mini-cards">
          <div class="mini-card card">
            <div class="mini-header"><span>黑话</span> <span class="tag active">ACTIVE</span></div>
            <h2 class="mini-number">1,402</h2>
            <p class="sub">今日检出数</p>
            <div class="mini-chart" ref="miniChart1"></div>
          </div>
          <div class="mini-card card">
            <div class="mini-header"><span>嘲讽</span> <span class="tag danger">OIGO</span></div>
            <h2 class="mini-number">892</h2>
            <p class="sub">今日检出数</p>
            <div class="mini-chart" ref="miniChart2"></div>
          </div>
          <div class="mini-card card">
            <div class="mini-header"><span>阴阳怪气</span> <span class="tag normal">NORMAL</span></div>
            <h2 class="mini-number">544</h2>
            <p class="sub">今日检出数</p>
            <div class="mini-chart" ref="miniChart3"></div>
          </div>
        </div>

        <div class="engine-banner">
          <div class="banner-content">
            <h2>多模态语义分析引擎</h2>
            <p>基于自研的深蓝语义大模型，我们能够精准识别隐藏在谐音、缩写以及游戏特定场景下的恶意言论。目前模型准确率已达 99.2%。</p>
            <div class="banner-actions">
              <button class="btn-white">查看详细报告</button>
              <button class="btn-outline">引擎设置</button>
            </div>
          </div>
          <div class="banner-ring">
            <div class="ring-circle">
              <span class="ring-score">90</span>
              <span class="ring-label">SANITY</span>
            </div>
          </div>
          <div class="status-badge"><span class="dot-green"></span> 实时检测已就绪</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const barChartRef = ref(null)
const lineChartRef = ref(null)
const distributionChartRef = ref(null)
const pieChartRef = ref(null)
const miniChart1 = ref(null)
const miniChart2 = ref(null)
const miniChart3 = ref(null)

let charts = []

const initCharts = () => {
  // 1. 柱状图 (去掉坐标轴线，纯粹展示数据块)
  const barChart = echarts.init(barChartRef.value)
  barChart.setOption({
    color: ['#8BA3E8'],
    grid: { top: 20, right: 0, bottom: 0, left: 0 },
    xAxis: { type: 'category', show: false, data: ['1','2','3','4','5','6','7'] },
    yAxis: { type: 'value', show: false },
    series: [{
      data: [40, 60, 45, 80, 55, 70, 95],
      type: 'bar',
      barWidth: '85%',
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#6B8DF2' }, // 顶部稍深的蓝
          { offset: 1, color: '#C6D6FF' }  // 底部极浅的蓝
        ])
      }
    }]
  })
  charts.push(barChart)

  // 2. 极简平滑折线图
  const lineChart = echarts.init(lineChartRef.value)
  lineChart.setOption({
    grid: { top: 20, right: 10, bottom: 20, left: 10 },
    xAxis: {
      type: 'category',
      data: ['05/18', '05/19', '05/20', '05/21', '05/22', '05/23', '05/24'],
      axisLine: {show: false},
      axisTick: {show: false},
      axisLabel: {color: '#64748B', fontSize: 12}
    },
    yAxis: { type: 'value', show: false },
    series: [{
      data: [10, 20, 15, 60, 10, 80, 30],
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: { color: '#64748B', width: 2 }
    }]
  })
  charts.push(lineChart)

  // 3. 绿色细线分布图
  const distChart = echarts.init(distributionChartRef.value)
  distChart.setOption({
    grid: { top: 20, right: 10, bottom: 20, left: 10 },
    xAxis: {
      type: 'category',
      data: ['0','1','2','3','4','5','6','7','8'],
      axisLine: {lineStyle: {color: '#E2E8F0'}},
      axisTick: {show: true, lineStyle: {color: '#E2E8F0'}},
      axisLabel: {color: '#64748B', fontSize: 12}
    },
    yAxis: { type: 'value', show: false },
    series: [{
      data: [50, 20, 40, 38, 90, 30, 20, 18, 5],
      type: 'line',
      symbol: 'none',
      lineStyle: { color: '#22C55E', width: 1.5 }
    }]
  })
  charts.push(distChart)

  // 4. 清爽饼图
  const pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    color: ['#8BA3E8'],
    series: [{
      type: 'pie',
      radius: ['0%', '70%'],
      label: { color: '#64748B', fontSize: 12, formatter: '{b}\n{c}' },
      labelLine: { lineStyle: { color: '#CBD5E1' } },
      itemStyle: { borderColor: '#fff', borderWidth: 2 },
      data: [
        { value: 404, name: '阴阳怪气' },
        { value: 201, name: '嘲讽' },
        { value: 195, name: '黑话' }
      ]
    }]
  })
  charts.push(pieChart)

  // 5. 底部微型图 (去掉多余元素，只留色块)
// 5. 底部微型图 (高危红色，中低危绿色)
  const miniOptions = (color) => ({
    grid: { top: 5, right: 0, bottom: 0, left: 0 },
    xAxis: { type: 'category', show: false, data: ['1','2','3','4','5'] },
    yAxis: { type: 'value', show: false },
    series: [{ type: 'bar', data: [3, 4, 3, 5, 2], itemStyle: { color: color }, barWidth: '80%' }]
  })

  // 黑话 (假设为中低危) -> 绿色
  const m1 = echarts.init(miniChart1.value); m1.setOption(miniOptions('#34D399')); charts.push(m1);
  // 嘲讽 (高危) -> 红色
  const m2 = echarts.init(miniChart2.value); m2.setOption(miniOptions('#EF4444')); charts.push(m2);
  // 阴阳怪气 (中低危) -> 浅绿色
  const m3 = echarts.init(miniChart3.value); m3.setOption(miniOptions('#6EE7B7')); charts.push(m3);

onMounted(() => {
  initCharts()
  window.addEventListener('resize', () => charts.forEach(c => c.resize()))
})

onUnmounted(() => {
  charts.forEach(c => c.dispose())
})
</script>

<style scoped>
/* 全局字体与容器优化 */
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
  color: #1E293B;
  background-color: #F8FAFC; /* SVG图背景是极淡的灰白 */
}

/* 取消所有硬边框，使用极柔和的超大弥散阴影，这能极大提升精致感 */
.card, .kpi-card, .chart-card {
  background: #FFFFFF;
  border-radius: 12px; /* 圆角统一调大 */
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.03); /* 关键：非常柔和的阴影 */
  border: none;
}

/* 头部 */
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;}
.page-title { font-size: 24px; font-weight: 600; margin: 0 0 6px 0; letter-spacing: 0.5px;}
.page-subtitle { color: #64748B; font-size: 14px; margin: 0; }
.update-time { background: #F1F5F9; color: #475569; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 500;}

/* --- 核心指标卡片 (精细调整字号和留白) --- */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.kpi-card { padding: 24px; display: flex; flex-direction: column; gap: 16px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-size: 14px; color: #64748B; font-weight: 500;}
.icon { font-size: 18px; }
.blue-icon { color: #3B82F6; }
.gray-icon { color: #64748B; }
.red-icon { color: #EF4444; }

.card-body { display: flex; align-items: baseline; gap: 12px; }
.kpi-number { font-size: 36px; font-weight: 700; margin: 0; line-height: 1; letter-spacing: -0.5px;} /* 放大数字并加粗 */
.trend { font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 2px;}
.trend.up { color: #3B82F6; }
.trend.up-danger { color: #EF4444; }
.trend.down { color: #3B82F6; }

/* 日历卡片特殊处理 */
.date-group { display: flex; flex-direction: column; gap: 4px; }
.year-month { font-size: 13px; color: #64748B; }
.day-row { display: flex; align-items: center; justify-content: space-between; width: 100%;}
.day-row .kpi-number { font-size: 24px; }
.arrow-down { color: #3B82F6; font-weight: bold; }

/* --- 图表区 --- */
.charts-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }
.chart-card { padding: 24px; height: 320px; display: flex; flex-direction: column; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.chart-header h3 { font-size: 16px; font-weight: 600; margin: 0; color: #1E293B;}
.legend-dot { font-size: 12px; color: #64748B; display: flex; align-items: center; gap: 6px;}
.legend-dot::before { content: ''; width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.legend-dot.blue::before { background-color: #3B82F6; }
.legend-dot.dark::before { background-color: #475569; }
.legend-text { font-size: 12px; color: #64748B; }
.chart-content { flex: 1; width: 100%; }

/* --- 底部区域 --- */
.bottom-grid { display: grid; grid-template-columns: 1fr 2.5fr; gap: 24px; }

/* 专项监控数据卡片 */
.monitor-card { padding: 24px; display: flex; flex-direction: column; }
.monitor-card h3 { font-size: 16px; font-weight: 600; margin: 0 0 24px 0; }
.progress-list { display: flex; flex-direction: column; gap: 24px; flex: 1; }
.progress-item { display: flex; flex-direction: column; gap: 10px; }
.progress-info { display: flex; align-items: center; font-size: 14px; font-weight: 500;}
.icon-box { width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; margin-right: 12px; font-size: 14px;}
.alert-box { background: #FEE2E2; }
.warning-box { background: #EFF6FF; }
.safe-box { background: #DCFCE7; }
.progress-label { color: #475569; }
.progress-info .value { margin-left: auto; font-weight: 700; font-size: 16px;}
.text-danger { color: #EF4444; }
.text-primary { color: #3B82F6; }
.text-success { color: #22C55E; }
.progress-bar { height: 6px; background: #F1F5F9; border-radius: 3px; }
.progress-bar .fill { height: 100%; border-radius: 3px; }
.fill.danger { background: #EF4444; }
.fill.primary { background: #3B82F6; }
.fill.success { background: #22C55E; }
.system-notice { margin-top: 24px; font-size: 13px; color: #94A3B8; background: #F8FAFC; padding: 16px; border-radius: 8px; line-height: 1.5; }

/* 右侧引擎区域 */
.engine-section { display: flex; flex-direction: column; gap: 24px; }
.mini-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.mini-card { padding: 20px; display: flex; flex-direction: column;}
.mini-header { display: flex; justify-content: space-between; align-items: center; font-size: 14px; margin-bottom: 16px; font-weight: 500; color: #1E293B;}
.tag { font-size: 10px; padding: 4px 8px; border-radius: 12px; font-weight: 700; letter-spacing: 0.5px;}
.tag.active { background: #EFF6FF; color: #2563EB; }
.tag.danger { background: #FEF2F2; color: #DC2626; }
.tag.normal { background: #F1F5F9; color: #64748B; }
.mini-number { font-size: 28px; font-weight: 700; margin: 0; }
.mini-card .sub { font-size: 12px; color: #94A3B8; margin: 4px 0 16px 0; }
.mini-chart { height: 40px; width: 100%; margin-top: auto;}

/* 炫酷的多模态引擎蓝色大横幅 */
.engine-banner {
  background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%); /* 非常纯正的深蓝到亮蓝渐变 */
  color: #fff;
  border-radius: 16px;
  padding: 32px 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  box-shadow: 0 10px 30px rgba(37, 99, 235, 0.2); /* 蓝色发光阴影 */
}
.banner-content { max-width: 55%; z-index: 2; }
.banner-content h2 { font-size: 22px; margin: 0 0 12px 0; font-weight: 600;}
.banner-content p { font-size: 14px; color: #DBEAFE; line-height: 1.6; margin: 0 0 24px 0; font-weight: 300;}
.banner-actions { display: flex; gap: 16px; }
.btn-white { background: #ffffff; color: #1D4ED8; border: none; padding: 10px 24px; border-radius: 6px; font-size: 14px; cursor: pointer; font-weight: 600; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}
.btn-outline { background: rgba(255,255,255,0.1); color: #fff; border: 1px solid rgba(255,255,255,0.3); padding: 10px 24px; border-radius: 6px; font-size: 14px; cursor: pointer; }

.banner-ring { z-index: 2; margin-right: 60px; }
.ring-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 8px solid rgba(255,255,255,0.2);
  border-top-color: #ffffff; /* 模拟90%进度的白色缺口环 */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.ring-score { font-size: 36px; font-weight: 700; line-height: 1;}
.ring-label { font-size: 12px; color: #DBEAFE; margin-top: 4px; letter-spacing: 1px;}

.status-badge {
  position: absolute;
  bottom: -16px;
  right: 40px;
  background: #ffffff;
  color: #1E293B;
  font-size: 13px;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.dot-green { width: 8px; height: 8px; background: #22C55E; border-radius: 50%; }
</style>