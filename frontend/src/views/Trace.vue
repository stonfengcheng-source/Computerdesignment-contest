<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">风险溯源拓扑图</h1>
      <p class="page-desc">基于 GAT 图神经网络，动态分析玩家间的社交传播链，揪出污染源头并定级污染程度。</p>
    </div>

    <div class="chart-card">
      <div class="graph-container" ref="graphContainer"></div>
    </div>

    <el-drawer
      v-model="drawerVisible"
      title="节点深度溯源详情"
      size="400px"
      :close-on-click-modal="false"
      class="custom-light-drawer"
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
import { ref, onMounted, onUnmounted } from 'vue'
import { Graph } from '@antv/g6'
// 移除原有的 mock 数据导入！

const graphContainer = ref(null)
const drawerVisible = ref(false)
const selectedNode = ref(null)
let graph = null

// 用于缓存所有的边和节点，以便进行深度遍历计算影响力
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

// 核心优化：深度优先遍历 (DFS) 计算全链路真实影响力
const calculateInfluence = (startNodeId) => {
  let influenceCount = 0;
  const visited = new Set();
  const stack = [startNodeId];

  while (stack.length > 0) {
    const currentId = stack.pop();

    if (!visited.has(currentId)) {
      visited.add(currentId);
      if (currentId !== startNodeId) {
        influenceCount++;
      }

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

const handleResize = () => {
  const container = graphContainer.value
  if (!graph || !container) return
  const width = container.offsetWidth
  const height = container.offsetHeight || 600

  if (typeof graph.changeSize === 'function') {
    graph.changeSize(width, height)
  } else if (typeof graph.setSize === 'function') {
    graph.setSize([width, height])
  }
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
  if (targetId && baseNodeMap.has(targetId)) {
    openNodeDrawer(baseNodeMap.get(targetId))
  }
}

// ================= 新增：动态请求后端图谱数据 =================
const fetchAndInitGraph = async () => {
  const container = graphContainer.value
  if (!container) return

  try {
    // 调用后端接口获取 GAT 生成的 GEXF 拓扑数据
    const res = await fetch('http://127.0.0.1:8000/api/slang/graph')
    const rawData = await res.json()

    // 格式化后端 Echarts 数据到 AntV G6 格式
    globalNodes = rawData.nodes || []
    // Echarts中边通常用 links，兼容处理
    globalEdges = rawData.links || rawData.edges || []

    const formattedNodes = globalNodes.map(node => {
      // 存储到 Map
      baseNodeMap.set(String(node.id), { ...node, color: node.itemStyle?.color });

      return {
        id: String(node.id),
        label: node.name || String(node.id),
        size: node.symbolSize || 30,
        style: {
          fill: node.itemStyle?.color || '#67C23A',
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

    const width = container.offsetWidth
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
        manyBody: { strength: -300 }, // 排斥力
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
          endArrow: {
            path: 'M 0,0 L 8,4 L 8,-4 Z',
            fill: '#cbd5e1',
          }
        },
      },
    })

    graph.render()
    graph.on('node:click', handleNodeClick)
    window.addEventListener('resize', handleResize)

  } catch (error) {
    console.error("加载图谱数据失败，请确保后端 8000 端口及模型已启动:", error)
  }
}

onMounted(() => {
  // 修改这里：从原来的 initGraph() 改为异步获取渲染
  fetchAndInitGraph()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (graph) {
    graph.destroy()
    graph = null
  }
})
</script>

<style scoped>
/* 融入主框架的容器样式 */
.page-container {
  padding: 30px 40px;
  min-height: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.page-header {
  margin-bottom: 25px;
}

.page-title {
  font-size: 1.8rem;
  color: #0f172a;
  font-weight: 800;
  margin: 0 0 10px 0;
}

.page-desc {
  color: #64748b;
  font-size: 1rem;
  margin: 0;
}

/* 图谱白色卡片容器 */
.chart-card {
  flex: 1;
  background: #ffffff;
  border-radius: 16px;
  padding: 10px;
  box-shadow: 0 4px 20px -5px rgba(14, 165, 233, 0.1);
  border: 1px solid #e2e8f0;
  min-height: 600px;
  position: relative;
  overflow: hidden;
}

.graph-container {
  width: 100%;
  height: 100%;
  border-radius: 12px;
  background-image: radial-gradient(#f1f5f9 1px, transparent 1px);
  background-size: 20px 20px;
  background-color: #f8fafc; /* 替换原有的暗黑背景，采用工程打点背景 */
}

.node-details {
  padding: 10px;
}

.highlight-text {
  color: #0ea5e9;
  font-weight: bold;
  font-family: monospace;
}

.danger-text {
  color: #ef4444;
  font-weight: 900;
  font-size: 1.1rem;
}

/* 强制重写 Element Plus 描述列表的亮色主题 */
:deep(.light-descriptions .el-descriptions__label) {
  background-color: #f8fafc !important;
  color: #475569 !important;
  font-weight: 600;
  width: 130px;
}

:deep(.light-descriptions .el-descriptions__content) {
  background-color: #ffffff !important;
  color: #0f172a !important;
}
</style>