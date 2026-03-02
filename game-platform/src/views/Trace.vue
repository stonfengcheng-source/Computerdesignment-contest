<template>
  <div class="trace">
    <div class="graph-container" ref="graphContainer"></div>

    <el-drawer
      v-model="drawerVisible"
      title="节点详情"
      size="400px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedNode" class="node-details">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="节点ID">
            {{ selectedNode.id }}
          </el-descriptions-item>
          <el-descriptions-item label="用户标签">
            {{ selectedNode.label }}
          </el-descriptions-item>
          <el-descriptions-item label="污染等级">
            <el-tag :color="selectedNode.style.fill">
              {{ getRiskLevel(selectedNode.style.fill) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="影响人数">
            {{ selectedNode.influenceCount }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Graph } from '@antv/g6'
import { nodes, edges } from '@/mock/trace.js'

const graphContainer = ref(null)
const drawerVisible = ref(false)
const selectedNode = ref(null)
let graph = null
const baseNodeMap = new Map(nodes.map((node) => [node.id, node]))

// 获取污染等级标签
const getRiskLevel = (color) => {
  const levelMap = {
    '#F56C6C': '高危',
    '#E6A23C': '中高危',
    '#FFC107': '中危',
    '#67C23A': '低危'
  }
  return levelMap[color] || '未知'
}

// 计算影响人数（直接连接的节点数）
const calculateInfluence = (nodeId) => {
  return edges.filter((edge) => edge.source === nodeId).length
}

const handleResize = () => {
  const container = graphContainer.value
  if (!graph || !container) return

  if (typeof graph.changeSize === 'function') {
    graph.changeSize(container.offsetWidth, 600)
    return
  }

  if (typeof graph.setSize === 'function') {
    graph.setSize([container.offsetWidth, 600])
  }
}

const openNodeDrawer = (nodeModel) => {
  if (!nodeModel?.id) return

  const baseNode = baseNodeMap.get(nodeModel.id)
  const color =
    nodeModel?.style?.fill ||
    baseNode?.color ||
    '#67C23A'

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

  const directData = evt.data?.id ? evt.data : evt.data?.data
  if (directData?.id) {
    openNodeDrawer(directData)
    return
  }

  const targetId = evt.target?.id || evt.itemId || evt.id
  if (targetId && baseNodeMap.has(targetId)) {
    openNodeDrawer(baseNodeMap.get(targetId))
  }
}

// 初始化图表
const initGraph = () => {
  const container = graphContainer.value
  if (!container) return

  const width = container.offsetWidth
  const height = 600

  const graphData = {
    nodes: nodes.map((node) => ({
      id: node.id,
      label: node.label,
      size: node.size,
      style: {
        fill: node.color,
        stroke: '#fff',
        lineWidth: 2,
      },
    })),
    edges: edges.map((edge) => ({
      source: edge.source,
      target: edge.target,
    })),
  }

  graph = new Graph({
    container,
    width,
    height,
    data: graphData,
    layout: {
      type: 'd3-force',
      preventOverlap: true,
      link: { distance: 120 },
      manyBody: { strength: -260 },
      collide: { radius: (d) => (d.size || 24) / 2 + 8 },
    },
    behaviors: ['drag-canvas', 'zoom-canvas', 'drag-element'],
    node: {
      style: {
        size: (d) => d.size || 30,
        labelText: (d) => d.label,
        labelFill: '#fff',
        labelFontSize: 12,
        stroke: '#fff',
        lineWidth: 2,
        fill: (d) => d.style?.fill || '#67C23A',
      },
    },
    edge: {
      style: {
        stroke: '#B0B3C1',
        lineWidth: 1,
      },
    },
  })

  graph.render()

  // 绑定节点点击事件
  graph.on('node:click', handleNodeClick)

  window.addEventListener('resize', handleResize)
}

// 组件挂载时初始化
onMounted(() => {
  initGraph()
})

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)

  if (graph) {
    graph.destroy()
    graph = null
  }
})
</script>

<style scoped>
.trace {
  padding: 20px;
  background-color: #0A0F1F;
  height: 100vh;
}

.graph-container {
  width: 100%;
  height: 600px;
  border: 1px solid #2A2F3A;
  background-color: #1A1D2A;
  border-radius: 8px;
}

.node-details {
  padding: 20px;
}

:deep(.el-drawer__body) {
  background-color: #1A1D2A;
  color: #B0B3C1;
}

:deep(.el-descriptions__title) {
  color: #B0B3C1;
}

:deep(.el-descriptions__label) {
  color: #B0B3C1;
  background-color: #2A2F3A;
}

:deep(.el-descriptions__content) {
  color: #B0B3C1;
  background-color: #1A1D2A;
}
</style>