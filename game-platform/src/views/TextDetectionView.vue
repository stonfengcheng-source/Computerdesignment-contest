<template>
  <div style="padding: 30px;">
    <h1 style="color: #B0B3C1;">💬 文本分析模块</h1>
    <p style="color: #B0B3C1;">调用微调后的 BERT 模型，深度检测游戏黑话与阴阳怪气。</p>
    
    <div style="margin-top: 20px;">
      <el-input 
        v-model="inputText" 
        placeholder="例如：就你这操作，真是下饭" 
        style="width: 400px; margin-right: 10px;"
      />
      <el-button type="primary" @click="handleDetect" :loading="loading">
        开始 AI 分析
      </el-button>
    </div>

    <div v-if="result" style="margin-top: 30px; padding: 20px; background: #2b2b40; border-radius: 8px;">
      <h3 style="color: #fff;">分析结果：</h3>
      <p style="color: #B0B3C1;">输入文本：{{ result.chat_text }}</p>
      <p style="color: #B0B3C1;">
        毒性概率：
        <span :style="{ color: result.toxicity_score > 0.5 ? '#F56C6C' : '#67C23A', fontSize: '20px', fontWeight: 'bold' }">
          {{ result.toxicity_score }}
        </span>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const inputText = ref('')
const loading = ref(false)
const result = ref(null)

const handleDetect = async () => {
  if (!inputText.value) return ElMessage.warning("请输入内容")
  
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('chat_text', inputText.value)

    // 发送请求到后端的 8000 端口
    const res = await axios.post('http://127.0.0.1:8000/api/v1/text/analyze_text', formData)
    
    result.value = res.data
    ElMessage.success("AI 判定完成！")
  } catch (err) {
    console.error(err)
    ElMessage.error("后端连接失败，请确认黑框框没报错")
  } finally {
    loading.value = false
  }
}
</script>