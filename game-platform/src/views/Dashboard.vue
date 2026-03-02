<template>
  <div class="dashboard">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" class="card-row">
      <el-col :span="6" v-for="(card, index) in cardList" :key="index">
        <el-card class="stat-card" shadow="hover">
          <div class="card-content">
            <div class="card-icon">
              <el-icon :size="32" :color="card.color">
                <component :is="card.icon" />
              </el-icon>
            </div>
            <div class="card-info">
              <div class="card-title">{{ card.title }}</div>
              <div class="card-value">{{ card.value }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行：折线图和饼图 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">近7日风险言论趋势</div>
          </template>
          <div ref="lineChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">风险等级分布</div>
          </template>
          <div ref="pieChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第三行：雷达图 -->
    <el-row class="chart-row">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">平台健康度</div>
          </template>
          <div ref="radarChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { Warning, User, Star, Loading } from '@element-plus/icons-vue'
import dashboardMock from '@/mock/dashboard.js'

// 卡片数据
const cardList = ref([
  {
    title: '今日风险言论数',
    value: dashboardMock.cardData.riskStatements,
    icon: Warning,
    color: '#F56C6C'
  },
  {
    title: '高危用户数',
    value: dashboardMock.cardData.highRiskUsers,
    icon: User,
    color: '#E6A23C'
  },
  {
    title: '平均信用分',
    value: dashboardMock.cardData.avgCreditScore,
    icon: Star,
    color: '#FFC107'
  },
  {
    title: '实时处理量',
    value: dashboardMock.cardData.realTimeProcessing,
    icon: Loading,
    color: '#67C23A'
  }
])

// 图表引用
const lineChartRef = ref(null)
const pieChartRef = ref(null)
const radarChartRef = ref(null)

let lineChart = null
let pieChart = null
let radarChart = null

// 初始化折线图
const initLineChart = () => {
  if (!lineChartRef.value) return
  lineChart = echarts.init(lineChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: dashboardMock.trendData.dates
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: dashboardMock.trendData.values,
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

// 初始化饼图
const initPieChart = () => {
  if (!pieChartRef.value) return
  pieChart = echarts.init(pieChartRef.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c}% ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      name: '风险等级',
      type: 'pie',
      radius: '50%',
      data: [
        { value: dashboardMock.riskDistribution.high, name: '高危', itemStyle: { color: '#F56C6C' } },
        { value: dashboardMock.riskDistribution.medium, name: '中危', itemStyle: { color: '#E6A23C' } },
        { value: dashboardMock.riskDistribution.low, name: '低危', itemStyle: { color: '#67C23A' } }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
  pieChart.setOption(option)
}

// 初始化雷达图
const initRadarChart = () => {
  if (!radarChartRef.value) return
  radarChart = echarts.init(radarChartRef.value)
  const option = {
    radar: {
      indicator: [
        { name: '文本毒性', max: 100 },
        { name: '行为异常', max: 100 },
        { name: '社交污染', max: 100 },
        { name: '响应速度', max: 100 },
        { name: '覆盖广度', max: 100 }
      ]
    },
    series: [{
      name: '平台健康度',
      type: 'radar',
      data: [{
        value: [
          dashboardMock.healthIndicators.textToxicity,
          dashboardMock.healthIndicators.abnormalBehavior,
          dashboardMock.healthIndicators.socialPollution,
          dashboardMock.healthIndicators.responseSpeed,
          dashboardMock.healthIndicators.coverage
        ],
        name: '健康度'
      }],
      itemStyle: {
        color: '#409EFF'
      },
      areaStyle: {
        color: 'rgba(64, 158, 255, 0.3)'
      }
    }]
  }
  radarChart.setOption(option)
}

// 窗口大小改变时重新调整图表大小
const handleResize = () => {
  if (lineChart) lineChart.resize()
  if (pieChart) pieChart.resize()
  if (radarChart) radarChart.resize()
}

onMounted(() => {
  initLineChart()
  initPieChart()
  initRadarChart()
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (lineChart) lineChart.dispose()
  if (pieChart) pieChart.dispose()
  if (radarChart) radarChart.dispose()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
  background-color: #0A0F1F;
}

.card-row {
  margin-bottom: 20px;
}

.stat-card {
  background-color: #1A1D2A;
  border: 1px solid #2A2F3A;
  color: #B0B3C1;
}

.card-content {
  display: flex;
  align-items: center;
}

.card-icon {
  margin-right: 15px;
}

.card-info {
  flex: 1;
}

.card-title {
  font-size: 14px;
  color: #B0B3C1;
  margin-bottom: 5px;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.chart-row {
  margin-bottom: 20px;
}

.card-header {
  color: #B0B3C1;
  font-weight: 500;
}

.chart-container {
  width: 100%;
  height: 350px;
}
</style>