// src/mock/trace.js
export const nodes = [
  { id: 'A', label: '污染源A', size: 56, color: '#F56C6C' },
  { id: 'B', label: '扩散B', size: 42, color: '#E6A23C' },
  { id: 'C', label: '扩散C', size: 48, color: '#FFC107' },
  { id: 'D', label: '受影响D', size: 34, color: '#67C23A' },
  { id: 'E', label: '受影响E', size: 30, color: '#67C23A' },
  { id: 'F', label: '受影响F', size: 28, color: '#67C23A' },
  { id: 'G', label: '外围G', size: 36, color: '#E6A23C' },
  { id: 'H', label: '外围H', size: 26, color: '#67C23A' },
]

export const edges = [
  { source: 'A', target: 'B' },
  { source: 'A', target: 'C' },
  { source: 'C', target: 'D' },
  { source: 'C', target: 'E' },
  { source: 'C', target: 'F' },
  { source: 'G', target: 'H' },
]

export default {
  nodes,
  edges,
}