<template>
  <div class="labeling-container">
    <header class="toolbar card">
      <div class="toolbar-left">
        <svg class="icon text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
        <span class="toolbar-title">当前语料池: <span class="text-primary cursor-pointer">ToxiCN_1.0 数据集</span></span>
      </div>
      <div class="toolbar-center">
        <div class="search-box">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input type="text" placeholder="搜索语料 ID 或 关键词..." />
        </div>
        <div class="filter-box">
          <span>全部文本</span>
          <span class="icon-down">˅</span>
        </div>
      </div>
      <div class="toolbar-right">
        <button class="btn-primary" @click="fetchCorpusData">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
          刷新语料
        </button>
      </div>
    </header>

    <section class="workspace">
      <div class="corpus-list-panel card">
        <div class="panel-header">
          <div class="header-left">
            <h3>待标注语料 ({{ corpusList.length }})</h3>
          </div>
          <div class="header-actions text-secondary" v-if="isLoading">
            加载中...
          </div>
        </div>

        <div class="list-content">
          <div
            v-for="item in paginatedList"
            :key="item.id"
            class="list-item"
            :class="{ active: currentCorpus && currentCorpus.id === item.id }"
            @click="selectCorpus(item)"
          >
            <div class="item-header">
              <span class="item-id">ID: {{ item.id }}</span>
              <span :class="item.status === '待标注' ? 'tag-pending' : 'tag-completed'">{{ item.status }}</span>
            </div>
            <p class="item-text">{{ item.text }}</p>
            <div class="item-footer">
              <span class="tag-source">{{ item.source }}</span>
            </div>
          </div>
        </div>

        <div class="pagination-mini">
          <span>第 {{ currentPage }} / {{ totalPages }} 页 (共 {{ corpusList.length }} 条)</span>
          <div class="page-btns">
            <button class="btn-page" @click="prevPage" :disabled="currentPage === 1">‹</button>
            <button class="btn-page" @click="nextPage" :disabled="currentPage === totalPages">›</button>
          </div>
        </div>
      </div>

      <div class="detail-workspace-panel card">
        <div class="workspace-header">
          <span class="workspace-title"><span class="dot-gray"></span> 详情工作区</span>
        </div>

        <div v-if="!currentCorpus" class="workspace-empty-state">
          <div class="empty-icon-box">
            <svg class="icon-big" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="3" x2="9" y2="21"/></svg>
          </div>
          <h3>准备开始标注</h3>
          <p>请从左侧语料池中选择一条数据开始深度标注。<br/>系统将自动加载多模态特征分析模型。</p>
        </div>

        <div v-else class="workspace-active-state">
          <div class="active-content-box">
            <span class="content-label">原文内容 [ID: {{ currentCorpus.id }}]</span>
            <p class="content-text">{{ currentCorpus.text }}</p>
          </div>

          <div class="label-actions">
            <span class="content-label">毒性分类标注</span>
            <div class="action-buttons">
              <button class="btn-tag danger" @click="submitLabel('严重违规')">严重违规 (仇恨/歧视)</button>
              <button class="btn-tag warning" @click="submitLabel('轻度违规')">轻度违规 (阴阳怪气/嘲讽)</button>
              <button class="btn-tag success" @click="submitLabel('安全合规')">安全合规</button>
            </div>
          </div>
        </div>

        <div class="statusbar">
          <div class="status-left">
            <span class="status-item"><span class="dot-green"></span> IDE核心: 活跃</span>
            <span class="status-item text-secondary" style="color: #64748B;">数据源集群: 已连接 (ToxiCN_1.0)</span>
          </div>
          <div class="status-right text-secondary">
            网络延迟: 24ms | 节点: 主节点-01
          </div>
        </div>
      </div>
    </section>

    <section class="performance-banner">
      <div class="banner-content">
        <div class="banner-header">
          <svg class="icon text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:8px;"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
          <span>标注规范</span>
        </div>
        <ul class="rule-list">
          <li>参考 ToxiCN 数据集标准，识别文本中的显性与隐性攻击。</li>
          <li>遇到边缘语境（如游戏黑话、反讽），需结合具体业务场景进行研判。</li>
        </ul>
      </div>

      <div class="banner-stats-box">
        <div class="stats-text-area">
          <h2>实时标注效能</h2>
          <p>过去 24 小时内，深蓝卫士共协助处理 42,901 条对抗性语料，净化成功率提升至 98.4%。</p>
          <div class="stats-numbers">
            <div class="num-item">
              <h3>3.2k</h3>
              <span>今日个人已标</span>
            </div>
            <div class="num-item">
              <h3>12.5m</h3>
              <span>全网监测总量</span>
            </div>
            <div class="num-item">
              <h3>0.08s</h3>
              <span>模型响应均值</span>
            </div>
          </div>
        </div>
        <svg class="banner-shield-bg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const corpusList = ref([])
const currentCorpus = ref(null)
const isLoading = ref(false)

// --- 分页核心逻辑 ---
const currentPage = ref(1)
const pageSize = ref(10) // 每页显示 10 条

const paginatedList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return corpusList.value.slice(start, end)
})

const totalPages = computed(() => {
  const total = Math.ceil(corpusList.value.length / pageSize.value)
  return total === 0 ? 1 : total
})

const prevPage = () => { if (currentPage.value > 1) currentPage.value-- }
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
// ------------------------


const fetchCorpusData = async () => {
  isLoading.value = true
  try {
    const response = await axios.get('/api/datasets/toxicn')
    if (response.data && !response.data.error) {
      corpusList.value = response.data // 完全相信后端传来的真实数据
    } else {
      corpusList.value = [] // 如果后端没数据，就是空数组，不再造假
    }
  } catch (error) {
    console.error("无法连接后端读取真实数据集", error)
    corpusList.value = [] // 报错时也置空
  } finally {
    isLoading.value = false
  }
}

const selectCorpus = (item) => { currentCorpus.value = item }

const submitLabel = (label) => {
  if (!currentCorpus.value) return
  const itemIndex = corpusList.value.findIndex(i => i.id === currentCorpus.value.id)
  if (itemIndex > -1) {
    corpusList.value[itemIndex].status = '已完成'
  }
  currentCorpus.value = null
}

onMounted(() => { fetchCorpusData() })
</script>

<style scoped>
.labeling-container { display: flex; flex-direction: column; gap: 20px; height: calc(100vh - 100px); color: #1E293B; font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;}
.card { background: #FFFFFF; border-radius: 12px; box-shadow: 0 4px 24px rgba(0, 0, 0, 0.03); border: none; }
.text-primary { color: #2563EB; } .text-secondary { color: #94A3B8; } .cursor-pointer { cursor: pointer; }

/* 顶部工具栏 */
.toolbar { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; }
.toolbar-left { display: flex; align-items: center; gap: 12px; font-weight: 600; font-size: 15px; }
.icon { width: 20px; height: 20px; } .icon-sm { width: 16px; height: 16px; margin-right: 8px;}
.toolbar-center { display: flex; gap: 16px; flex: 1; max-width: 600px; margin: 0 40px; }
.search-box { flex: 1; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; display: flex; align-items: center; padding: 0 16px; color: #94A3B8;}
.search-box input { border: none; background: transparent; width: 100%; height: 36px; outline: none; font-size: 13px; color: #1E293B;}
.filter-box { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; display: flex; align-items: center; justify-content: space-between; padding: 0 16px; min-width: 140px; font-size: 13px; color: #475569; cursor: pointer; }
.btn-primary { background: #2563EB; color: white; border: none; padding: 8px 20px; border-radius: 6px; font-weight: 500; cursor: pointer; display: flex; align-items: center; font-size: 14px; }

/* 核心工作区 */
.workspace { display: flex; gap: 20px; flex: 1; min-height: 0; }

/* 左侧：语料列表面板 */
.corpus-list-panel { width: 400px; display: flex; flex-direction: column; overflow: hidden; }
.panel-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #F1F5F9; }
.header-left h3 { margin: 0; font-size: 15px; font-weight: 600; }
.list-content { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.list-item { padding: 16px; border-radius: 8px; border: 1px solid transparent; cursor: pointer; transition: all 0.2s; border-bottom: 1px solid #F1F5F9; }
.list-item:hover { background: #F8FAFC; }
.list-item.active { background: #F8FAFC; border-color: #BFDBFE; box-shadow: 0 2px 8px rgba(37, 99, 235, 0.05); }

.item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.item-id { font-size: 12px; color: #64748B; font-family: monospace; }
.tag-pending { background: #FEF3C7; color: #D97706; font-size: 11px; padding: 4px 8px; border-radius: 4px; font-weight: 600; }
.tag-completed { background: #DCFCE7; color: #16A34A; font-size: 11px; padding: 4px 8px; border-radius: 4px; font-weight: 600; }
.item-text { font-size: 14px; color: #334155; line-height: 1.6; margin: 0 0 12px 0; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.tag-source { background: #F1F5F9; color: #64748B; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 500;}

/* 分页器 */
.pagination-mini { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; border-top: 1px solid #E2E8F0; font-size: 12px; color: #64748B; }
.page-btns { display: flex; gap: 4px; }
.btn-page { background: white; border: 1px solid #E2E8F0; border-radius: 4px; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #475569; }
.btn-page:disabled { opacity: 0.5; cursor: not-allowed; }

/* 右侧：详情工作区面板 */
.detail-workspace-panel { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }
.workspace-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #F1F5F9; }
.workspace-title { font-size: 13px; color: #64748B; font-weight: 500; display: flex; align-items: center; gap: 8px; }
.dot-gray { width: 6px; height: 6px; background: #CBD5E1; border-radius: 50%; }

/* 占位状态 */
.workspace-empty-state { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; background: #FAFAFA; }
.empty-icon-box { width: 64px; height: 64px; background: #F1F5F9; border-radius: 16px; display: flex; align-items: center; justify-content: center; margin-bottom: 24px; color: #94A3B8;}
.icon-big { width: 32px; height: 32px; }
.workspace-empty-state h3 { font-size: 18px; color: #1E293B; margin: 0 0 12px 0; font-weight: 600;}
.workspace-empty-state p { font-size: 14px; color: #64748B; line-height: 1.6; }

/* 激活工作区状态 */
.workspace-active-state { flex: 1; padding: 32px; display: flex; flex-direction: column; gap: 32px; overflow-y: auto;}
.content-label { font-size: 13px; color: #64748B; font-weight: 600; display: block; margin-bottom: 12px; }
.active-content-box { background: #F8FAFC; border: 1px solid #E2E8F0; padding: 24px; border-radius: 8px; }
.content-text { font-size: 16px; color: #0F172A; line-height: 1.8; margin: 0; }
.action-buttons { display: flex; gap: 16px; flex-wrap: wrap; }
.btn-tag { border: 1px solid transparent; padding: 10px 20px; border-radius: 6px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s; background: #fff;}
.btn-tag.danger { border-color: #FECACA; color: #DC2626; } .btn-tag.danger:hover { background: #FEF2F2; }
.btn-tag.warning { border-color: #FDE68A; color: #D97706; } .btn-tag.warning:hover { background: #FFFBEB; }
.btn-tag.success { border-color: #A7F3D0; color: #059669; } .btn-tag.success:hover { background: #ECFDF5; }

/* 底部状态栏 */
.statusbar { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: #F8FAFC; border-top: 1px solid #F1F5F9; font-size: 12px; }
.status-left { display: flex; gap: 24px; }
.status-item { display: flex; align-items: center; gap: 6px; color: #10B981; font-weight: 500;}
.dot-green { width: 6px; height: 6px; background: #10B981; border-radius: 50%; }

/* 底部效能横幅 */
.performance-banner { display: grid; grid-template-columns: 1fr 2fr; gap: 24px; }
.banner-content { background: white; border-radius: 12px; padding: 24px; border: 1px solid #F1F5F9; }
.banner-header { display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 600; margin-bottom: 16px; }
.rule-list { margin: 0; padding-left: 20px; font-size: 13px; color: #475569; line-height: 1.8; }

.banner-stats-box { background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%); border-radius: 12px; padding: 24px 32px; color: white; display: flex; justify-content: space-between; align-items: center; position: relative; overflow: hidden; box-shadow: 0 10px 30px rgba(37, 99, 235, 0.15);}
.stats-text-area { position: relative; z-index: 2; }
.stats-text-area h2 { font-size: 20px; margin: 0 0 8px 0; font-weight: 600;}
.stats-text-area p { font-size: 13px; color: #DBEAFE; margin: 0 0 24px 0; max-width: 80%; line-height: 1.6; }
.stats-numbers { display: flex; gap: 48px; }
.num-item h3 { font-size: 28px; margin: 0 0 4px 0; font-weight: 700;}
.num-item span { font-size: 12px; color: #DBEAFE; }
.banner-shield-bg { position: absolute; right: 20px; top: 50%; transform: translateY(-50%); width: 140px; height: 140px; opacity: 0.1; color: #fff;}
</style>