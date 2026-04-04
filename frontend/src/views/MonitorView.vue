<template>
  <div class="monitor-container">
    <header class="page-header">
      <div class="header-left-text">
        <h1 class="page-title">实时监测</h1>
        <p class="page-subtitle">实时追踪网络环境中的多维风险状态</p>
      </div>
      <div class="live-indicator">
        <span class="pulsing-dot"></span>
        <span class="live-text">实时监控中</span>
      </div>
    </header>

    <section class="top-section">
      <div class="video-card card">
        <div class="card-header">
          <div class="header-left">
            <svg class="icon text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"/><line x1="7" y1="2" x2="7" y2="22"/><line x1="17" y1="2" x2="17" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="2" y1="7" x2="7" y2="7"/><line x1="2" y1="17" x2="7" y2="17"/><line x1="17" y1="17" x2="22" y2="17"/><line x1="17" y1="7" x2="22" y2="7"/></svg>
            <h3>视频风险实时监控</h3>
          </div>
          <div class="header-actions">
            <input type="file" ref="fileInput" accept="video/mp4,video/x-m4v,video/*" style="display: none" @change="handleFileUpload" />
            <button class="btn-text text-danger" @click="clearVideo" v-if="videoSrc">清除视频</button>
            <button class="btn-outline" @click="triggerUpload">上传本地视频</button>
            <button class="btn-primary" :disabled="!videoSrc || isAnalyzing" @click="startAnalysis">
              {{ isAnalyzing ? '引擎检测中...' : '开始分析' }}
            </button>
          </div>
        </div>

        <div class="video-player">
          <video v-if="videoSrc" :src="videoSrc" controls autoplay loop class="real-video-element"></video>
          <div v-else class="video-overlay empty-video">
            <div class="center-focus">
              <div class="focus-box"></div>
              <div class="focus-text">等待视频流接入...</div>
            </div>
          </div>
        </div>
      </div>

      <div class="feed-card card">
        <div class="card-header">
          <h3>文本与毒性(%)标签</h3>
        </div>
        <div class="feed-list">
          <div v-for="(log, index) in displayLogs" :key="index" class="feed-item danger">
            <div class="item-top">
              <span class="tag-type">言</span>
              <span class="score">文本捕获</span>
            </div>
            <p class="item-desc">{{ log }}</p>
            <span class="time">最新抓取</span>
          </div>
          <div v-if="displayLogs.length === 0" style="padding: 20px; text-align: center; color: #94a3b8; font-size: 13px;">
            视频流分析尚未产生违规文本...
          </div>
        </div>
      </div>
    </section>

    <section class="topology-entry card">
      <div class="card-header">
        <div class="header-left">
          <svg class="icon text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
          <h3>风险溯源拓扑</h3>
        </div>
        <button class="btn-outline" @click="$router.push('/trace')">导出拓扑图</button>
      </div>
      <div class="topology-placeholder" @click="$router.push('/trace')">
        <div class="node left-node">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <div class="line"></div>
        <div class="center-node pulse">
          <div class="loading-text">交互式网络结构加载中...</div>
        </div>
        <div class="line"></div>
        <div class="node right-node text-danger">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        </div>
      </div>
    </section>

    <section class="charts-section">
      <div class="chart-card card">
        <div class="card-header">
          <div class="header-left">
            <h3>风险时间线</h3>
          </div>
        </div>
        <div class="chart-box" ref="timelineChartRef"></div>
      </div>

      <div class="chart-card card">
        <div class="card-header">
          <div class="header-left">
            <h3>风险类型占比</h3>
          </div>
        </div>
        <div class="chart-box" ref="pieChartRef"></div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

// 1. 变量声明
const fileInput = ref(null)
const videoSrc = ref(null)
const selectedFileObj = ref(null)
const isAnalyzing = ref(false)

const seenLogsSet = new Set()
const displayLogs = ref([])
let logPollingTimer = null

// 2. 视频与文件操作
const triggerUpload = () => { fileInput.value.click() }

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file && file.type.startsWith('video/')) {
    selectedFileObj.value = file
    if (videoSrc.value) URL.revokeObjectURL(videoSrc.value)
    videoSrc.value = URL.createObjectURL(file)
  } else {
    alert("请上传有效的视频文件 (MP4, WebM 等)")
  }
}

const clearVideo = () => {
  if (videoSrc.value) {
    URL.revokeObjectURL(videoSrc.value)
    videoSrc.value = null
  }
  selectedFileObj.value = null
  if (fileInput.value) fileInput.value.value = ''

  // 清理轮询与数据
  if (logPollingTimer) clearInterval(logPollingTimer)
  displayLogs.value = []
  seenLogsSet.clear()
}

// 3. 核心：调用引擎并实时拉取文本
const startAnalysis = async () => {
  if (!selectedFileObj.value) return alert("请先上传视频文件！")

  isAnalyzing.value = true

  const formData = new FormData()
  formData.append('video_file', selectedFileObj.value)
  formData.append('player_id', 'Monitor_Live_001')

  // 开启轮询拉取日志
  logPollingTimer = setInterval(async () => {
    try {
      const res = await axios.get('/api/v1/monitor/logs')
      const incomingLogs = res.data.logs || []

      incomingLogs.forEach(line => {
        if (!seenLogsSet.has(line)) {
          seenLogsSet.add(line)
          displayLogs.value.unshift(line) // 最新弹幕排在最前
        }
      })
    } catch (error) {
      console.error("拉取日志失败:", error)
    }
  }, 1500)

  // 提交视频分析
  try {
    await axios.post('/api/v1/analyze/video', formData)
    console.log("视频全流程分析完毕")
  } catch (error) {
    console.error("AI 引擎调用异常:", error)
  } finally {
    isAnalyzing.value = false
    if (logPollingTimer) clearInterval(logPollingTimer)
  }
}

// 4. Echarts 图表渲染
const timelineChartRef = ref(null)
const pieChartRef = ref(null)
let charts = []

const initCharts = () => {
  if (!timelineChartRef.value || !pieChartRef.value) return;

  const timelineChart = echarts.init(timelineChartRef.value)
  timelineChart.setOption({
    grid: { top: 20, right: 10, bottom: 20, left: 30 },
    xAxis: { type: 'category', data: ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'], axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#64748B', fontSize: 10 } },
    yAxis: { type: 'value', show: false },
    series: [{
      data: [40, 50, 90, 45, 30, 60, 95], type: 'bar', barWidth: '60%',
      itemStyle: { borderRadius: [4, 4, 0, 0], color: function(params) { if (params.dataIndex === 2) return '#3B82F6'; if (params.dataIndex === 6) return '#EF4444'; return '#E2E8F0'; } }
    }]
  })
  charts.push(timelineChart)

  const pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    color: ['#1D4ED8', '#3B82F6', '#93C5FD'],
    series: [{ type: 'pie', radius: ['0%', '70%'], label: { color: '#64748B', formatter: '{b} {c}%' }, labelLine: { lineStyle: { color: '#CBD5E1' } }, itemStyle: { borderColor: '#fff', borderWidth: 2 }, data: [{ value: 43, name: '黑话' }, { value: 37, name: '嘲讽' }, { value: 20, name: '阴阳怪气' }] }]
  })
  charts.push(pieChart)
}

onMounted(() => {
  nextTick(() => { setTimeout(initCharts, 100) })
  window.addEventListener('resize', () => charts.forEach(c => c.resize()))
})

onUnmounted(() => {
  charts.forEach(c => c.dispose())
  if (logPollingTimer) clearInterval(logPollingTimer)
})
</script>

<style scoped>
.monitor-container { display: flex; flex-direction: column; gap: 24px; font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif; color: #1E293B;}
.card { background: #FFFFFF; border-radius: 12px; box-shadow: 0 4px 24px rgba(0, 0, 0, 0.03); border: none; padding: 24px; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-left { display: flex; align-items: center; gap: 10px; }
.header-left h3 { margin: 0; font-size: 16px; font-weight: 600; color: #1E293B; }
.icon { width: 20px; height: 20px; }
.text-primary { color: #2563EB; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.header-left-text { display: flex; flex-direction: column; gap: 4px; }
.page-title { font-size: 24px; font-weight: 600; margin: 0; }
.page-subtitle { color: #64748B; font-size: 14px; margin: 0; }
.live-indicator { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: #2563EB; background: #EFF6FF; padding: 6px 16px; border-radius: 20px;}
.pulsing-dot { width: 8px; height: 8px; background-color: #2563EB; border-radius: 50%; animation: pulse 1.5s infinite; }
@keyframes pulse { 0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.4); } 70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(37, 99, 235, 0); } 100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); } }
.top-section { display: grid; grid-template-columns: 2fr 1fr; gap: 24px; }
.video-card { display: flex; flex-direction: column; }
.header-actions { display: flex; gap: 12px; }
.btn-text { background: transparent; border: none; cursor: pointer; font-size: 13px; font-weight: 500;}
.text-danger { color: #DC2626; }
.btn-outline { background: #fff; border: 1px solid #E2E8F0; color: #475569; padding: 6px 16px; border-radius: 6px; font-size: 13px; cursor: pointer; font-weight: 500;}
.btn-primary { background: #2563EB; color: white; border: none; padding: 6px 16px; border-radius: 6px; font-size: 13px; cursor: pointer; font-weight: 500;}
.btn-primary:disabled { background: #94A3B8; cursor: not-allowed;}
.video-player { flex: 1; background: #0F172A; border-radius: 8px; min-height: 380px; position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center; border: 1px solid #E2E8F0;}
.real-video-element { width: 100%; height: 100%; object-fit: contain; background: #000; border-radius: 8px; }
.empty-video { background: #F8FAFC; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;}
.center-focus { display: flex; flex-direction: column; align-items: center; gap: 16px; }
.focus-box { width: 80px; height: 80px; border: 2px dashed #CBD5E1; border-radius: 12px; }
.focus-text { color: #64748B; font-size: 14px; letter-spacing: 1px; }
.feed-card { display: flex; flex-direction: column; }
.feed-list { display: flex; flex-direction: column; gap: 12px; overflow-y: auto; max-height: 380px; padding-right: 4px;}
.feed-list::-webkit-scrollbar { width: 4px; }
.feed-list::-webkit-scrollbar-thumb { background: #E2E8F0; border-radius: 4px; }
.feed-item { padding: 16px; border-radius: 8px; border: 1px solid #E2E8F0; background: #F8FAFC; }
.feed-item.danger { background: #FEF2F2; border-color: #FECACA; }
.item-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.tag-type { background: #FEE2E2; color: #DC2626; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.score { font-weight: 700; font-size: 15px; color: #DC2626; }
.item-desc { font-size: 13px; color: #334155; margin: 0 0 12px 0; line-height: 1.6; }
.time { font-size: 12px; color: #94A3B8; }
.topology-entry { cursor: pointer; transition: border-color 0.3s; }
.topology-entry:hover { border-color: #93C5FD; }
.topology-placeholder { background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 8px; height: 160px; display: flex; align-items: center; justify-content: center; position: relative; margin-top: 10px; }
.node { width: 48px; height: 48px; background: white; border: 1px solid #E2E8F0; border-radius: 12px; display: flex; align-items: center; justify-content: center; z-index: 2; box-shadow: 0 2px 8px rgba(0,0,0,0.05); color: #64748B;}
.center-node { width: 180px; height: 48px; background: white; border: 1px solid #93C5FD; border-radius: 24px; display: flex; align-items: center; justify-content: center; z-index: 2; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1); }
.loading-text { font-size: 13px; color: #2563EB; font-weight: 500;}
.line { width: 120px; height: 2px; background: linear-gradient(90deg, #E2E8F0, #93C5FD); margin: 0 -10px; z-index: 1; }
.pulse { animation: soft-pulse 2s infinite; }
@keyframes soft-pulse { 0% { box-shadow: 0 0 0 0 rgba(37,99,235,0.15); } 50% { box-shadow: 0 0 0 10px rgba(37,99,235,0); } 100% { box-shadow: 0 0 0 0 rgba(37,99,235,0); } }
.charts-section { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.chart-box { height: 240px; width: 100%; }
</style>