<template>
  <div class="detect">
    <el-row :gutter="20">
      <!-- 左侧输入区域 -->
      <el-col :span="12">
        <el-card shadow="hover" class="input-card">
          <template #header>
            <div class="card-header">文本输入</div>
          </template>
          <el-form>
            <el-form-item>
              <el-input
                v-model="text"
                type="textarea"
                :rows="8"
                placeholder="请输入要检测的文本内容..."
                class="text-input"
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                @click="detect"
                :loading="detecting"
                class="detect-btn"
              >
                检测
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧结果区域 -->
      <el-col :span="12">
        <el-card v-if="result" shadow="hover" class="result-card">
          <template #header>
            <div class="card-header">检测结果</div>
          </template>

          <!-- 毒性概率 -->
          <div class="result-section">
            <h4>毒性概率</h4>
            <el-progress
              type="circle"
              :percentage="result.toxicity"
              :color="getProgressColor(result.toxicity)"
              :stroke-width="8"
              class="toxicity-progress"
            />
            <p class="toxicity-text">{{ result.toxicity }}%</p>
          </div>

          <!-- 黑话词高亮 -->
          <div class="result-section">
            <h4>原文及黑话词</h4>
            <div class="highlighted-text" v-html="result.highlightedText"></div>
          </div>

          <!-- 情感标签 -->
          <div class="result-section">
            <h4>情感标签</h4>
            <el-tag
              :type="result.sentiment === '正常' ? 'success' : 'warning'"
              size="large"
            >
              {{ result.sentiment }}
            </el-tag>
          </div>
        </el-card>

        <el-card v-else shadow="hover" class="result-card">
          <el-empty description="请先输入文本并点击检测" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 响应式数据
const text = ref('')
const result = ref(null)
const detecting = ref(false)

// 模拟检测函数
const detect = () => {
  if (!text.value.trim()) {
    ElMessage.warning('请输入要检测的文本内容')
    return
  }

  detecting.value = true

  // 模拟异步检测过程
  setTimeout(() => {
    result.value = {
      toxicity: 85,
      highlightedText: highlightSlang(text.value),
      sentiment: '阴阳怪气'
    }
    detecting.value = false
  }, 1000)
}

// 高亮黑话词
const highlightSlang = (txt) => {
  const slangWords = ['下饭', '演员', '摆烂']
  let highlighted = txt

  slangWords.forEach(word => {
    const regex = new RegExp(`(${word})`, 'gi')
    highlighted = highlighted.replace(regex, '<span class="highlight">$1</span>')
  })

  return highlighted
}

// 根据毒性概率获取进度条颜色
const getProgressColor = (toxicity) => {
  if (toxicity >= 80) return '#F56C6C' // 红色
  if (toxicity >= 60) return '#E6A23C' // 橙色
  if (toxicity >= 40) return '#FFC107' // 黄色
  return '#67C23A' // 绿色
}
</script>

<style scoped>
.detect {
  padding: 20px;
  background-color: #0A0F1F;
  min-height: 100vh;
}

.input-card,
.result-card {
  background-color: #1A1D2A;
  border: 1px solid #2A2F3A;
  color: #B0B3C1;
}

.card-header {
  color: #B0B3C1;
  font-weight: 500;
}

.text-input {
  background-color: #2A2F3A;
  border: 1px solid #3A3F4A;
  color: #B0B3C1;
}

.text-input :deep(.el-textarea__inner) {
  background-color: #2A2F3A;
  border: none;
  color: #B0B3C1;
}

.text-input :deep(.el-textarea__inner::placeholder) {
  color: #7A7F8A;
}

.detect-btn {
  width: 100%;
}

.result-section {
  margin-bottom: 30px;
}

.result-section h4 {
  color: #B0B3C1;
  margin-bottom: 15px;
  font-size: 16px;
}

.toxicity-progress {
  margin: 0 auto;
  display: block;
}

.toxicity-text {
  text-align: center;
  margin-top: 10px;
  color: #409EFF;
  font-size: 18px;
  font-weight: bold;
}

.highlighted-text {
  background-color: #2A2F3A;
  padding: 15px;
  border-radius: 8px;
  line-height: 1.6;
  color: #B0B3C1;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.highlight {
  background-color: #F56C6C;
  color: #fff;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: bold;
}

:deep(.el-progress-circle__track) {
  stroke: #2A2F3A;
}

:deep(.el-progress-circle__path) {
  stroke-linecap: round;
}

:deep(.el-empty__description p) {
  color: #7A7F8A;
}
</style>