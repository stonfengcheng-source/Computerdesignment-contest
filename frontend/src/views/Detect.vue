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
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 响应式数据
const text = ref('')
const result = ref(null)
const detecting = ref(false)

// ✅ 真实检测函数：调用后端 API
const detect = async () => {
  if (!text.value.trim()) {
    ElMessage.warning('请输入要检测的文本内容')
    return
  }

  detecting.value = true

  try {
    // 用 FormData 发送，和后端 Form(...) 对应
    const formData = new FormData()
    formData.append('chat_text', text.value)

    const res = await axios.post('http://127.0.0.1:8000/api/v1/text/analyze_text', formData)

    // 后端返回：{ status, chat_text, toxicity_score }
    // toxicity_score 是 0~1 的小数，乘以 100 转成百分比整数给进度条用
    const scorePercent = Math.round(res.data.toxicity_score * 100)

    result.value = {
      toxicity: scorePercent,
      highlightedText: highlightSlang(res.data.chat_text),
      sentiment: scorePercent >= 50 ? '阴阳怪气' : '正常'
    }

    ElMessage.success('AI 判定完成！')
  } catch (err) {
    console.error(err)
    ElMessage.error('后端连接失败，请确认后端服务已启动（端口 8000）')
  } finally {
    detecting.value = false
  }
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
  background-color: #f8fafc;
  min-height: 100vh;
}

.input-card,
.result-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  color: #334155;
}

.card-header {
  color: #334155;
  font-weight: 500;
}

.text-input {
  background-color: #e2e8f0;
  border: 1px solid #cbd5e1;
  color: #334155;
}

.text-input :deep(.el-textarea__inner) {
  background-color: #e2e8f0;
  border: none;
  color: #334155;
}

.text-input :deep(.el-textarea__inner::placeholder) {
  color: #94a3b8;
}

.detect-btn {
  width: 100%;
}

.result-section {
  margin-bottom: 30px;
}

.result-section h4 {
  color: #334155;
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
  background-color: #e2e8f0;
  padding: 15px;
  border-radius: 8px;
  line-height: 1.6;
  color: #334155;
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
  stroke: #e2e8f0;
}

:deep(.el-progress-circle__path) {
  stroke-linecap: round;
}

:deep(.el-empty__description p) {
  color: #94a3b8;
}
</style>