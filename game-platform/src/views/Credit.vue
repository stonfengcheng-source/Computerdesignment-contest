<template>
  <div class="credit">
    <!-- 搜索区域 -->
    <el-card shadow="hover" class="search-card">
      <el-form :inline="true" class="search-form">
        <el-form-item label="玩家ID">
          <el-input
            v-model="playerId"
            placeholder="请输入玩家ID"
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
            搜索
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 结果展示区域 -->
    <div v-if="creditData" class="results">
      <el-row :gutter="20">
        <!-- 信用总分 -->
        <el-col :span="8">
          <el-card shadow="hover" class="score-card">
            <template #header>
              <div class="card-header">信用总分</div>
            </template>
            <div class="score-display">
              <el-progress
                type="circle"
                :percentage="(creditData.totalScore / creditData.maxScore) * 100"
                :stroke-width="12"
                :color="getScoreColor(creditData.totalScore)"
                class="score-progress"
              />
              <div class="score-text">
                <div class="current-score">{{ creditData.totalScore }}</div>
                <div class="max-score">/ {{ creditData.maxScore }}</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 分项得分柱状图 -->
        <el-col :span="8">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">分项得分</div>
            </template>
            <div ref="barChartRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <!-- 信用变化折线图 -->
        <el-col :span="8">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">近30天信用变化</div>
            </template>
            <div ref="lineChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <el-empty description="请输入玩家ID进行搜索" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

// 响应式数据
const playerId = ref('')
const creditData = ref(null)
const searching = ref(false)

// 图表引用
const barChartRef = ref(null)
const lineChartRef = ref(null)

let barChart = null
let lineChart = null

// 搜索函数
const search = () => {
  if (!playerId.value.trim()) {
    ElMessage.warning('请输入玩家ID')
    return
  }

  searching.value = true

  // 模拟搜索过程
  setTimeout(() => {
    // Mock 数据
    creditData.value = {
      totalScore: 687,
      maxScore: 1000,
      categories: {
        text: 250,
        behavior: 300,
        social: 137
      },
      trendData: {
        dates: Array.from({length: 30}, (_, i) => {
          const day = i + 1
          return `02-${day.toString().padStart(2, '0')}`
        }),
        scores: Array.from({length: 30}, (_, i) => {
          // 生成模拟的信用分数变化数据
          const baseScore = 650
          const variation = Math.sin(i * 0.2) * 50 + Math.random() * 30 - 15
          return Math.max(400, Math.min(900, Math.floor(baseScore + variation)))
        })
      }
    }

    // 初始化图表
    initCharts()

    searching.value = false
  }, 1000)
}

// 获取分数颜色
const getScoreColor = (score) => {
  const percentage = score / 1000
  if (percentage >= 0.8) return '#67C23A' // 绿色
  if (percentage >= 0.6) return '#E6A23C' // 橙色
  if (percentage >= 0.4) return '#FFC107' // 黄色
  return '#F56C6C' // 红色
}

// 初始化柱状图
const initBarChart = () => {
  if (!barChartRef.value || !creditData.value) return

  barChart = echarts.init(barChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['文本得分', '行为得分', '社交得分'],
      textStyle: {
        color: '#B0B3C1'
      }
    },
    xAxis: {
      type: 'category',
      data: ['信用分项'],
      axisLabel: {
        color: '#B0B3C1'
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#B0B3C1'
      }
    },
    series: [
      {
        name: '文本得分',
        type: 'bar',
        stack: 'total',
        data: [creditData.value.categories.text],
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '行为得分',
        type: 'bar',
        stack: 'total',
        data: [creditData.value.categories.behavior],
        itemStyle: {
          color: '#67C23A'
        }
      },
      {
        name: '社交得分',
        type: 'bar',
        stack: 'total',
        data: [creditData.value.categories.social],
        itemStyle: {
          color: '#E6A23C'
        }
      }
    ]
  }
  barChart.setOption(option)
}

// 初始化折线图
const initLineChart = () => {
  if (!lineChartRef.value || !creditData.value) return

  lineChart = echarts.init(lineChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: creditData.value.trendData.dates,
      axisLabel: {
        color: '#B0B3C1',
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#B0B3C1'
      }
    },
    series: [{
      data: creditData.value.trendData.scores,
      type: 'line',
      smooth: true,
      itemStyle: {
        color: '#409EFF'
      },
      areaStyle: {
        color: 'rgba(64, 158, 255, 0.1)'
      }
    }]
  }
  lineChart.setOption(option)
}

// 初始化所有图表
const initCharts = () => {
  initBarChart()
  initLineChart()
}

// 窗口大小改变时重新调整图表大小
const handleResize = () => {
  if (barChart) barChart.resize()
  if (lineChart) lineChart.resize()
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (barChart) barChart.dispose()
  if (lineChart) lineChart.dispose()
})
</script>

<style scoped>
.credit {
  padding: 20px;
  background-color: #0A0F1F;
  min-height: 100vh;
}

.search-card {
  background-color: #1A1D2A;
  border: 1px solid #2A2F3A;
  margin-bottom: 20px;
}

.search-form {
  display: flex;
  justify-content: center;
}

.search-input {
  width: 300px;
}

.search-input :deep(.el-input__inner) {
  background-color: #2A2F3A;
  border: 1px solid #3A3F4A;
  color: #B0B3C1;
}

.search-input :deep(.el-input__inner::placeholder) {
  color: #7A7F8A;
}

.results {
  margin-top: 20px;
}

.score-card {
  background-color: #1A1D2A;
  border: 1px solid #2A2F3A;
  text-align: center;
}

.card-header {
  color: #B0B3C1;
  font-weight: 500;
}

.score-display {
  position: relative;
  display: inline-block;
}

.score-progress {
  margin-bottom: 20px;
}

.score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #409EFF;
}

.current-score {
  font-size: 24px;
  font-weight: bold;
}

.max-score {
  font-size: 12px;
  color: #7A7F8A;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.empty-state {
  margin-top: 100px;
}

:deep(.el-empty__description p) {
  color: #7A7F8A;
}
</style>