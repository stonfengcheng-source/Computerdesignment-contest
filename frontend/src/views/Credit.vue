<template>
  <div class="credit">
    <el-card shadow="hover" class="search-card">
      <el-form :inline="true" class="search-form" @submit.prevent>
        <el-form-item label="玩家游戏ID">
          <el-input
            v-model="playerId"
            placeholder="例如: admin_test_001"
            class="search-input"
            @keyup.enter="search"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            @click="search"
            :loading="searching"
          >
            全网深度检索
          </el-button>
        </el-form-item>

        <el-form-item v-if="creditData">
          <el-button
            type="success"
            @click="downloadLatestReport"
          >
            📥 下载最新信用报告
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <div v-if="creditData" class="results">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card shadow="hover" class="score-card">
            <template #header>
              <div class="card-header">跨平台综合信用画像</div>
            </template>
            <div class="score-display">
              <el-progress
                type="dashboard"
                :percentage="creditData.totalScore"
                :stroke-width="12"
                :color="getScoreColor(creditData.totalScore)"
                class="score-progress"
              >
                <template #default="{ percentage }">
                  <div class="score-text" :style="{ color: getScoreColor(percentage) }">
                    <div class="current-score">{{ percentage }}</div>
                    <div class="credit-level">{{ creditData.level }}</div>
                  </div>
                </template>
              </el-progress>
              <p class="score-desc">满分: 100分 (基于多平台违规率折算)</p>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">核心信用维度分析</div>
            </template>
            <div ref="radarChartRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">跨平台违规风险画像</div>
            </template>
            <div ref="platformChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div v-else class="empty-state">
      <el-empty description="输入跨平台通行证/游戏ID，获取全网信用评级" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const route = useRoute()

// 响应式数据
const playerId = ref('')
const creditData = ref(null)
const searching = ref(false)

// 图表引用
const radarChartRef = ref(null)
const platformChartRef = ref(null)

let radarChart = null
let platformChart = null

// ====== 💡 新增：监听路由自动搜索 ======
onMounted(() => {
  window.addEventListener('resize', handleResize)

  // Check for ID in query parameters on mount
  if (route.query.id) {
    // If the ID looks like the descriptive text from Behavior.vue (e.g., "最新检测: video.mp4"),
    // you might want to extract just a clean ID or handle it gracefully.
    // For now, let's assume it's a clean ID like 'admin_test_001'
    playerId.value = route.query.id
    search()
  }
})

watch(
  () => route.query.id,
  (newId) => {
    if (newId && newId !== playerId.value) {
      playerId.value = newId;
      search();
    }
  }
)

// ====== 真实调用后端接口 ======
const search = async () => {
  if (!playerId.value.trim()) {
    ElMessage.warning('请输入玩家ID')
    return
  }

  searching.value = true

  try {
    const response = await fetch(`http://127.0.0.1:8000/api/v1/credit/${playerId.value}`)
    const json = await response.json()

    if (response.ok && json.status === 'success') {
      const data = json.data

      creditData.value = {
        totalScore: data.cross_platform_credit_score,
        level: data.credit_level,
        radar: data.radar_chart,
        platforms: data.platform_details
      }

      ElMessage.success('信用数据聚合完毕！')

      await nextTick()
      initCharts()
    } else {
      ElMessage.error(`查询失败: ${json.message || '未知错误'}`)
    }
  } catch (error) {
    console.error(error)
    ElMessage.error(`网络或服务器异常: ${error.message}`)
  } finally {
    searching.value = false
  }
}

// ====== 💡 下载逻辑修复 ======
const downloadLatestReport = () => {
  if (!playerId.value) return;
  // 使用 a 标签隐藏下载避免浏览器拦截新窗口
  const link = document.createElement('a');
  link.href = `http://127.0.0.1:8000/api/v1/report/download_latest/${playerId.value}`;
  link.setAttribute('download', '');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// ====== 分数颜色动态计算 ======
const getScoreColor = (score) => {
  if (score >= 85) return '#67C23A'
  if (score >= 70) return '#E6A23C'
  return '#F56C6C'
}

// ====== 初始化信用维度柱状图 ======
const initRadarChart = () => {
  if (!radarChartRef.value || !creditData.value) return

  if (radarChart) radarChart.dispose()
  radarChart = echarts.init(radarChartRef.value)

  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', max: 100 },
    yAxis: {
      type: 'category',
      data: ['游戏态度', '社交友好', '团队协作'],
      axisLabel: { fontWeight: 'bold' }
    },
    series: [
      {
        name: '维度得分',
        type: 'bar',
        barWidth: '50%',
        data: [
          { value: creditData.value.radar.game_attitude, itemStyle: { color: '#409EFF' } },
          { value: creditData.value.radar.social_friendly, itemStyle: { color: '#67C23A' } },
          { value: creditData.value.radar.team_coop, itemStyle: { color: '#E6A23C' } }
        ],
        label: { show: true, position: 'right' }
      }
    ]
  }
  radarChart.setOption(option)
}

// ====== 初始化多平台违规对比图 ======
const initPlatformChart = () => {
  if (!platformChartRef.value || !creditData.value) return

  if (platformChart) platformChart.dispose()
  platformChart = echarts.init(platformChartRef.value)

  const platforms = creditData.value.platforms.map(p => p.platform)
  const afkData = creditData.value.platforms.map(p => (p.afk_rate * 100).toFixed(1))
  const reportData = creditData.value.platforms.map(p => (p.report_rate * 100).toFixed(1))
  const toxicData = creditData.value.platforms.map(p => (p.toxic_words_freq * 100).toFixed(1))

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      valueFormatter: (value) => value + '%'
    },
    legend: { data: ['挂机率', '被举报率', '言语违规率'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: platforms,
      axisLabel: { fontWeight: 'bold' }
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: '{value} %' }
    },
    series: [
      { name: '挂机率', type: 'bar', data: afkData, itemStyle: { color: '#909399' } },
      { name: '被举报率', type: 'bar', data: reportData, itemStyle: { color: '#F56C6C' } },
      { name: '言语违规率', type: 'bar', data: toxicData, itemStyle: { color: '#E6A23C' } }
    ]
  }
  platformChart.setOption(option)
}

const initCharts = () => {
  initRadarChart()
  initPlatformChart()
}

const handleResize = () => {
  if (radarChart) radarChart.resize()
  if (platformChart) platformChart.resize()
}

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (radarChart) radarChart.dispose()
  if (platformChart) platformChart.dispose()
})
</script>

<style scoped>
/* 保持所有样式不变... */
.credit { padding: 20px; background-color: #f8fafc; min-height: 100vh; }
.search-card { background-color: #ffffff; border: 1px solid #e2e8f0; margin-bottom: 20px; border-radius: 12px; }
.search-form { display: flex; justify-content: center; align-items: flex-end; }
.search-input { width: 350px; }
.results { margin-top: 20px; }
.score-card { background-color: #ffffff; border: 1px solid #e2e8f0; text-align: center; height: 100%; }
.card-header { color: #334155; font-weight: 700; font-size: 1.1rem; }
.score-display { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; }
.score-text { display: flex; flex-direction: column; align-items: center; }
.current-score { font-size: 40px; font-weight: 800; line-height: 1; }
.credit-level { font-size: 16px; font-weight: bold; margin-top: 8px; padding: 2px 12px; border-radius: 12px; background-color: rgba(0,0,0,0.05); }
.score-desc { color: #94a3b8; font-size: 0.9rem; margin-top: -10px; }
.chart-container { width: 100%; height: 300px; }
.empty-state { margin-top: 100px; }
</style>