<template>
  <div class="detect-container">
    <header class="page-header">
      <div class="header-info">
        <h1 class="page-title">文本安全深度检测报告</h1>
        <p class="page-subtitle">分析维度：多模态毒性语义解析</p>
      </div>
      <div class="header-actions">
        <button class="btn-export">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          导出报告
        </button>
        <button class="btn-refresh" @click="resetAnalysis">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
          重新扫描
        </button>
      </div>
    </header>

    <section class="input-section card">
      <div class="section-title">
        <div class="title-bar"></div>
        <h3>待分析内容输入</h3>
      </div>
      <div class="input-wrapper">
        <textarea
          v-model="inputText"
          placeholder="请在此处粘贴需要进行安全性分析的文本内容..."
          rows="6"
        ></textarea>
        <div class="button-row">
          <button class="btn-submit" :disabled="isAnalyzing" @click="startAnalysis">
            {{ isAnalyzing ? '解析中...' : '启动深度解析' }}
          </button>
        </div>
      </div>
    </section>

    <section class="result-section card">
      <div class="section-header">
        <div class="header-left">
          <svg class="icon text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          <h3>毒性检测 (Toxicity Detection)</h3>
        </div>
      </div>

      <div class="result-grid">
        <div class="result-left">
          <div class="info-group">
            <span class="label">判定结果</span>
            <div class="value">{{ resultData.judgment }}</div>
          </div>
          <div class="info-group mt-4">
            <span class="label">风险等级</span>
            <div class="risk-badge" :class="resultData.riskLevelClass">
              <span class="dot"></span> {{ resultData.riskLevelText }}
            </div>
          </div>
        </div>
        <div class="result-right">
          <span class="label">证据与分析</span>
          <div class="analysis-box">
            {{ resultData.evidence }}
          </div>
        </div>
      </div>
    </section>

    <section class="bottom-stats">
      <div class="stat-card card">
        <div class="stat-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg></div>
        <h2>{{ resultData.purificationIndex }}</h2>
        <p>综合净化指数</p>
      </div>
      <div class="stat-card card">
        <div class="stat-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-gray"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></div>
        <h2 :class="{'text-active': resultData.isAnalyzed}">{{ resultData.semanticScore }}</h2>
        <p>语义健康度评分</p>
      </div>
      <div class="stat-card card">
        <div class="stat-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-danger"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div>
        <h2 :class="{'text-danger': resultData.hasLethalThreat}">{{ resultData.lethalThreat }}</h2>
        <p>致命性威胁预警</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'

const inputText = ref('')
const isAnalyzing = ref(false)

const defaultData = {
  isAnalyzed: false,
  judgment: '等待调度解析引擎...',
  riskLevelText: '-',
  riskLevelClass: 'badge-default',
  evidence: '请在上方输入框粘贴待检测文本。系统将调用多维语义大模型，识别潜在的攻击性、偏见或不当言论。',
  purificationIndex: '0.00',
  semanticScore: '未激活',
  lethalThreat: '暂无风险',
  hasLethalThreat: false
}

const resultData = reactive({ ...defaultData })

const startAnalysis = async () => {
  if (!inputText.value.trim()) return

  isAnalyzing.value = true

  try {
    // 【关键】后端使用了 Form(...) 接收参数，前端必须用 FormData 格式提交
    const formData = new FormData()
    formData.append('chat_text', inputText.value)

    // 调用你刚写的真实后端接口
    const response = await axios.post('http://localhost:8000/analyze_text', formData)
    const data = response.data

    resultData.isAnalyzed = true

    // 获取算分结果 (假设 toxicity_score 是 0 到 100 的数值)
    const score = data.toxicity_score || 0

    // 动态渲染评级
    if (score > 60) {
      resultData.judgment = '检测到高危违规内容'
      resultData.riskLevelText = '高危风险'
      resultData.riskLevelClass = 'badge-danger'
      resultData.hasLethalThreat = score > 85
      resultData.lethalThreat = score > 85 ? '触发熔断拦截' : '需人工复核'
    } else {
      resultData.judgment = '内容安全合规'
      resultData.riskLevelText = '安全'
      resultData.riskLevelClass = 'badge-success'
      resultData.hasLethalThreat = false
      resultData.lethalThreat = '无风险'
    }

    // 将你后端的 5 维数据格式化成专业报告的样式展示在"证据与分析"框里
    resultData.evidence = `【引擎解析完成】\n` +
                          `• 毒性分值: ${score.toFixed(2)} / 100\n` +
                          `• 违规类型: ${data.toxic_type || '无'}\n` +
                          `• 表达特征: ${data.expression || '正常'}\n` +
                          `• 针对目标: ${(data.target_groups && data.target_groups.length) ? data.target_groups.join(', ') : '无明确目标'}\n` +
                          `• 黑话/术语识别: ${data.is_jargon ? '已检出 (关联游戏内特有黑话字典)' : '未检出'}`

    // 动态计算底部大卡片的数字
    resultData.purificationIndex = Math.max(0, 100 - score).toFixed(2)
    resultData.semanticScore = `${score.toFixed(1)}/100`

  } catch (error) {
    console.error("API请求失败:", error)
    alert("引擎调度失败，请检查深蓝卫士后端节点 (FastAPI) 是否正常运行。")
    resetAnalysis()
  } finally {
    isAnalyzing.value = false
  }
}

const resetAnalysis = () => {
  inputText.value = ''
  Object.assign(resultData, defaultData)
}
</script>

<style scoped>
.detect-container { display: flex; flex-direction: column; gap: 24px; max-width: 1200px; margin: 0 auto; color: #1E293B; }
.card { background: #FFFFFF; border-radius: 12px; box-shadow: 0 4px 24px rgba(0, 0, 0, 0.03); border: none; padding: 32px; }

.page-header { display: flex; justify-content: space-between; align-items: flex-end; }
.page-title { font-size: 24px; font-weight: 600; margin: 0 0 8px 0; color: #1E293B; }
.page-subtitle { color: #64748B; font-size: 14px; margin: 0; }
.header-actions { display: flex; gap: 12px; }
.btn-export { background: #2563EB; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; font-size: 14px; cursor: pointer; display: flex; align-items: center; gap: 8px; font-weight: 500;}
.btn-refresh { background: #F1F5F9; color: #475569; border: 1px solid #E2E8F0; padding: 8px 16px; border-radius: 6px; font-size: 14px; cursor: pointer; display: flex; align-items: center; gap: 8px;}
.icon-sm { width: 16px; height: 16px; }
.icon { width: 20px; height: 20px; }

.input-section { padding: 24px 32px; }
.section-title { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.title-bar { width: 4px; height: 18px; background: #2563EB; border-radius: 2px; }
.section-title h3 { margin: 0; font-size: 16px; color: #1E293B; font-weight: 600;}

.input-wrapper { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; display: flex; flex-direction: column; gap: 16px; }
textarea { width: 100%; border: none; background: transparent; resize: none; outline: none; font-size: 14px; color: #1E293B; font-family: inherit; line-height: 1.6; }
textarea::placeholder { color: #94A3B8; }
.button-row { display: flex; justify-content: flex-end; }
.btn-submit { background: #2563EB; color: white; border: none; padding: 10px 24px; border-radius: 6px; font-weight: 500; cursor: pointer; transition: background 0.2s; }
.btn-submit:disabled { background: #94A3B8; cursor: not-allowed; }

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; border-bottom: 1px solid #F1F5F9; padding-bottom: 16px; }
.header-left { display: flex; align-items: center; gap: 12px; }
.header-left h3 { margin: 0; font-size: 18px; color: #1E293B; }

.result-grid { display: grid; grid-template-columns: 1fr 2fr; gap: 40px; }
.label { font-size: 13px; color: #64748B; display: block; margin-bottom: 8px; }
.value { font-size: 18px; color: #1E293B; font-weight: 600; }
.mt-4 { margin-top: 24px; }

.risk-badge { display: inline-flex; align-items: center; gap: 8px; padding: 6px 16px; border-radius: 20px; font-size: 14px; font-weight: 500; }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.badge-default { background: #F1F5F9; color: #64748B; } .badge-default .dot { background: #94A3B8; }
.badge-danger { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA;} .badge-danger .dot { background: #DC2626; }
.badge-success { background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0;} .badge-success .dot { background: #059669; }

.analysis-box { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 20px; font-size: 14px; color: #475569; line-height: 1.6; min-height: 100px; }

.bottom-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; text-align: center; }
.stat-card { padding: 32px 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.stat-icon { width: 32px; height: 32px; margin-bottom: 16px; }
.stat-card h2 { font-size: 36px; margin: 0 0 8px 0; color: #1E293B; font-weight: 700;}
.stat-card p { margin: 0; font-size: 14px; color: #64748B; }
.text-primary { color: #2563EB; }
.text-gray { color: #94A3B8; }
.text-danger { color: #DC2626 !important; }
.text-active { color: #2563EB !important; }
</style>