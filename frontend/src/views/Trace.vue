<template>
  <div class="page-container behavior-container">
    <header class="page-header">
      <div>
        <h1 class="page-title">风险溯源拓扑图</h1>
        <p class="page-desc">基于 GAT 图神经网络，记录每局社交传播链，揪出污染源头并定级污染程度。</p>
      </div>
      <button class="export-btn">导出溯源报告</button>
    </header>

    <div class="upload-box" style="margin-bottom: 24px; padding: 20px; background: #fff; border-radius: 16px; border: 1px dashed #0ea5e9; display: flex; align-items: center; justify-content: center;">
      <div style="display: flex; align-items: center; gap: 15px;">
        <span style="font-weight: 600; color: #64748b;">输入待溯源的对局ID：</span>
        <input type="text" v-model="newMatchId" placeholder="例如: MATCH_9527" class="match-input" />
        <button
          @click="startTrace"
          :disabled="isLoading"
          style="padding: 10px 28px; background: #0ea5e9; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 700; transition: opacity 0.3s;"
          :style="{ opacity: isLoading ? 0.6 : 1 }"
        >
          {{ isLoading ? '🕸️ GAT 拓扑生成中...' : '生成对局拓扑' }}
        </button>
      </div>
    </div>

    <div class="main-content">
      <section class="alert-section">
        <div class="section-header">
          <h3>历史对局溯源记录</h3>
        </div>
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>对局 ID</th>
                <th>检测时间</th>
                <th>核心污染源预估</th>
                <th>全链路影响人数</th>
                <th>整体风险评级</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in historyList" :key="item.id">
                <td class="player-col"><strong>{{ item.matchId }}</strong></td>
                <td style="color: #64748b;">{{ item.time }}</td>
                <td><span class="danger-text">{{ item.sourcePlayer }}</span></td>
                <td>{{ item.affectedNodes }} 人</td>
                <td>
                  <span class="tag" :class="item.riskClass">{{ item.riskLevel }}</span>
                </td>
                <td>
                  <button class="action-btn" @click="viewGraph(item)">查看图谱</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>

    <el-dialog
      v-model="graphDialogVisible"
      :title="`对局 [${currentMatch?.matchId}] 传播链路拓扑`"
      width="85%"
      top="5vh"
      @opened="fetchAndInitGraph"
      @closed="destroyGraph"
      destroy-on-close
    >
      <div class="chart-card">
        <div class="graph-container" ref="graphContainer"></div>
      </div>
    </el-dialog>

    <el-drawer
      v-model="drawerVisible"
      title="节点深度溯源详情"
      size="400px"
      :close-on-click-modal="false"
      class="custom-light-drawer"
      append-to-body
    >
      <div v-if="selectedNode" class="node-details">
        <el-descriptions :column="1" border class="light-descriptions">
          <el-descriptions-item label="溯源追踪ID">
            <span class="highlight-text">{{ selectedNode.id }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="用户标签画像">
            {{ selectedNode.label }}
          </el-descriptions-item>
          <el-descriptions-item label="系统判定等级">
            <el-tag :color="selectedNode.style.fill" effect="dark" style="border: none;">
              {{ getRiskLevel(selectedNode.style.fill) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="全链路影响人数">
            <span class="danger-text">{{ selectedNode.influenceCount }} 人</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Graph } from '@antv/g6'
import axios from 'axios'

const graphContainer = ref(null)
const drawerVisible = ref(false)
const selectedNode = ref(null)
let graph = null

// --- 列表状态 ---
const newMatchId = ref('')
const isLoading = ref(false)
const historyList = ref([])
const graphDialogVisible = ref(false)
const currentMatch = ref(null)

// 缓存边和节点，以便DFS计算
let globalNodes = []
let globalEdges = []
const baseNodeMap = new Map()

// 风险等级映射
const getRiskLevel = (color) => {
  const levelMap = {
    '#F56C6C': '高危污染源',
    '#E6A23C': '中高危传播者',
    '#FFC107': '中危易感人群',
    '#67C23A': '低危健康玩家'
  }
  return levelMap[color] || '未知状态'
}

// ================= 1. 真实接入：从数据库读取历史记录 =================
const fetchHistory = async () => {
  try {
    // 【注意】这里请替换为你后端实际的拉取历史记录接口
    const response = await axios.get('api/v1/trace/records')

    // 将后端返回的记录映射为前端需要的格式
    const history = response.data.data.map(item => ({
      id: item.id,
      matchId: item.match_id,
      time: item.created_at || new Date().toLocaleString(),
      sourcePlayer: item.source_player || '系统推演中',
      affectedNodes: item.affected_count || 0,
      riskLevel: item.risk_level || (item.affected_count > 5 ? '高危扩散' : '低危正常'),
      riskClass: item.affected_count > 5 ? 'negative' : 'positive'
    }))

    // 倒序排列展示最新记录
    historyList.value = history.reverse()
  } catch (error) {
    console.error("加载溯源历史记录失败:", error)
    // 接口没通时的容错提示
    // alert("无法连接到后端数据库，请检查 8000 端口服务")
  }
}

// ================= 2. 真实接入：发送对局ID给后端生成拓扑 =================
const startTrace = async () => {
  if (!newMatchId.value) {
    alert("请输入待溯源的对局 ID")
    return
  }

  isLoading.value = true

  try {
    // 【注意】这里请替换为你后端实际触发分析的接口
    const response = await axios.post('/api/v1/trace/analyze', {
      match_id: newMatchId.value
    })

    const serverResult = response.data.result || response.data.data || {}

    // 将后端生成的新记录追加到表格头部
    const newRecord = {
      id: serverResult.id || Date.now(),
      matchId: serverResult.match_id || newMatchId.value,
      time: serverResult.created_at || new Date().toLocaleString(),
      sourcePlayer: serverResult.source_player || '分析完成',
      affectedNodes: serverResult.affected_count || 0,
      riskLevel: serverResult.risk_level || '中危扩散',
      riskClass: serverResult.risk_class || 'neutral'
    }

    historyList.value.unshift(newRecord)
    alert(`对局 [${newMatchId.value}] 拓扑溯源分析完成，已入库。`)
    newMatchId.value = '' // 清空输入框

  } catch (error) {
    console.error("后端引擎分析失败:", error)
    alert("GAT 引擎调用失败，请确保后端服务和模型已启动")
  } finally {
    isLoading.value = false
  }
}

// ================= 3. 动态请求对应对局的图谱 JSON 数据 =================
const fetchAndInitGraph = async () => {
  const container = graphContainer.value
  if (!container || !currentMatch.value) return

  // 确保每次打开弹窗前，彻底清空上一次残留的空画布
  container.innerHTML = ''

  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/slang/graph?match_id=${currentMatch.value.matchId}`)
    const rawData = res.data

    globalNodes = rawData.nodes || []
    globalEdges = rawData.links || rawData.edges || []

    // 💡 核心修复：如果后台还没生成完，弹窗提示并阻止 G6 报错
    if (globalNodes.length === 0) {
      alert(`对局 [${currentMatch.value.matchId}] 的图谱正在后台 AI 生成中，请耐心等待 5-10 秒后再查看！`)
      return
    }

    baseNodeMap.clear()

    const formattedNodes = globalNodes.map(node => {
      // 💡 增强解析：兼容 Echarts 和 NetworkX GEXF 的各种属性命名
      const nodeColor = node.color || node.attributes?.color || node.itemStyle?.color || '#67C23A'
      const nodeName = node.label || node.name || node.attributes?.name || String(node.id)
      const nodeSize = node.symbolSize || node.attributes?.symbolSize || 40

      baseNodeMap.set(String(node.id), { ...node, color: nodeColor })

      return {
        id: String(node.id),
        label: nodeName,  // 这里将会显示中文英雄名！
        size: parseInt(nodeSize),
        style: {
          fill: nodeColor,
          stroke: '#ffffff',
          lineWidth: 3,
          shadowColor: 'rgba(0,0,0,0.1)',
          shadowBlur: 10
        }
      }
    })

    const formattedEdges = globalEdges.map(edge => ({
      source: String(edge.source),
      target: String(edge.target),
    }))

    const width = container.offsetWidth || 800 // 给一个默认宽度防 fallback
    const height = container.offsetHeight || 600

    graph = new Graph({
      container,
      width,
      height,
      data: { nodes: formattedNodes, edges: formattedEdges },
      layout: {
        type: 'd3-force',
        preventOverlap: true,
        link: { distance: 150 },
        manyBody: { strength: -300 },
        collide: { radius: (d) => (d.size || 24) / 2 + 10 },
      },
      behaviors: ['drag-canvas', 'zoom-canvas', 'drag-element'],
      node: {
        style: {
          size: (d) => d.size || 30,
          labelText: (d) => d.label,
          labelFill: '#334155',
          labelFontSize: 12,
          labelFontWeight: 'bold',
          stroke: '#fff',
          lineWidth: 2,
          fill: (d) => d.style?.fill || '#67C23A',
        },
      },
      edge: {
        style: {
          stroke: '#cbd5e1',
          lineWidth: 1.5,
          endArrow: { path: 'M 0,0 L 8,4 L 8,-4 Z', fill: '#cbd5e1' }
        },
      },
    })

    graph.render()
    graph.on('node:click', handleNodeClick)

  } catch (error) {
    console.error(`拉取对局 ${currentMatch.value.matchId} 的图谱数据失败:`, error)
  }
}

// 打开图谱弹窗
const viewGraph = (match) => {
  currentMatch.value = match
  graphDialogVisible.value = true
  // 弹窗出现后，el-dialog 的 @opened 会自动执行 fetchAndInitGraph
}

// DFS 计算影响力 (本地图遍历算法，无需请求后端)
const calculateInfluence = (startNodeId) => {
  let influenceCount = 0;
  const visited = new Set();
  const stack = [startNodeId];

  while (stack.length > 0) {
    const currentId = stack.pop();
    if (!visited.has(currentId)) {
      visited.add(currentId);
      if (currentId !== startNodeId) influenceCount++;

      let i = 0;
      while (i < globalEdges.length) {
        if (globalEdges[i].source === currentId && !visited.has(globalEdges[i].target)) {
          stack.push(globalEdges[i].target);
        }
        i++;
      }
    }
  }
  return influenceCount;
}

const openNodeDrawer = (nodeModel) => {
  if (!nodeModel?.id) return
  const baseNode = baseNodeMap.get(nodeModel.id)
  const color = nodeModel?.style?.fill || baseNode?.color || '#67C23A'

  selectedNode.value = {
    id: nodeModel.id,
    label: nodeModel.label || baseNode?.label || nodeModel.id,
    style: { fill: color },
    influenceCount: calculateInfluence(nodeModel.id),
  }
  drawerVisible.value = true
}

const handleNodeClick = (evt) => {
  if (!evt) return
  if (evt.item?.getModel) {
    openNodeDrawer(evt.item.getModel())
    return
  }
  const targetId = evt.target?.id || evt.itemId || evt.id
  if (targetId && baseNodeMap.has(targetId)) openNodeDrawer(baseNodeMap.get(targetId))
}

const destroyGraph = () => {
  if (graph) {
    graph.destroy()
    graph = null
  }
  if (graphContainer.value) {
    graphContainer.value.innerHTML = '' // 连同 DOM 一起清空
  }
}

const handleResize = () => {
  if (graph && graphContainer.value) {
    graph.changeSize(graphContainer.value.offsetWidth, graphContainer.value.offsetHeight)
  }
}

onMounted(() => {
  fetchHistory() // 页面挂载时自动请求后端历史数据
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  destroyGraph()
})
</script>

<style scoped>
/* 融合主框架样式 */
.behavior-container {
  padding: 32px;
  background-color: #f8fafc;
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 8px 0;
}

.page-desc {
  color: #64748b;
  font-size: 1rem;
  margin: 0;
}

.export-btn {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  padding: 10px 20px;
  border-radius: 8px;
  color: #334155;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.export-btn:hover { background: #f1f5f9; border-color: #94a3b8; }

.match-input {
  padding: 8px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  outline: none;
  color: #334155;
  width: 200px;
}

/* 核心表格区 - 复用 Behavior.vue 风格 */
.alert-section {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 { margin: 0; font-size: 1.2rem; font-weight: 700; color: #0f172a; }

.data-table { width: 100%; border-collapse: collapse; }
.data-table th { text-align: left; padding: 16px; background: #f8fafc; color: #64748b; font-weight: 600; font-size: 0.9rem; border-bottom: 2px solid #e2e8f0; }
.data-table td { padding: 16px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }

.player-col { color: #334155; }
.danger-text { color: #ef4444; font-weight: 900; }

.tag {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
}
.tag.positive { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
.tag.neutral { background: #fffbeb; color: #d97706; border: 1px solid #fde68a; }
.tag.negative { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }

.action-btn {
  background: transparent;
  color: #0ea5e9;
  border: 1px solid #0ea5e9;
  padding: 6px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}
.action-btn:hover { background: #0ea5e9; color: #fff; }

/* 弹窗图谱容器 */
.chart-card {
  width: 100%;
  height: 65vh; /* 确保弹窗内图谱有足够高度 */
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.graph-container {
  width: 100%;
  height: 100%;
  background-image: radial-gradient(#f1f5f9 1px, transparent 1px);
  background-size: 20px 20px;
  background-color: #f8fafc;
}

.highlight-text { color: #0ea5e9; font-weight: bold; font-family: monospace; }
</style>