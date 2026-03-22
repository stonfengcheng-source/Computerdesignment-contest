<template>
  <div class="credit-report-wrapper">
    <h2 style="text-align: center; color: #60a5fa;">历史对局检测记录</h2>

    <div class="record-list">
      <div class="record-item" v-for="match in historyRecords" :key="match.matchId">
        <div>
          <h3 style="margin: 0 0 5px 0;">对局 ID: {{ match.matchId }}</h3>
          <span style="font-size: 12px; color: #94a3b8;">{{ match.timestamp }}</span>
        </div>
        <button class="btn-view" @click="openReport(match)">查看报告</button>
      </div>
    </div>

    <div v-if="isModalOpen" class="modal-overlay" @click.self="closeReport">
      <div class="modal-content">
        <div class="modal-header">
          <h3 style="margin: 0; color: #60a5fa;">对局分析报告 - {{ currentMatch.matchId }}</h3>
          <button class="close-btn" @click="closeReport">×</button>
        </div>

        <div class="modal-body">
          <div class="panel-left">
            <h4 style="color: #38bdf8;">📝 行为与信用分析</h4>
            <div class="typewriter" :key="currentMatch.matchId">{{ currentMatch.reportText }}</div>
          </div>

          <div class="panel-right">
            <h4 style="color: #38bdf8;">🕸️ 图谱溯源</h4>
            <div ref="graphDom" class="trace-graph"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';
import * as echarts from 'echarts';

// 模拟的对局存储记录
const historyRecords = ref([
  {
    matchId: "GAME_8829_A",
    timestamp: "2026-03-22 21:15:00",
    reportText: "【高风险警告】检测到该对局中语音内容与实际操作严重不符。\n玩家在关键团战期间频繁发送“进攻”指令，但实际操作轨迹显示其停留在安全区域。结合历史数据分析，判定存在明显的消极比赛和恶意引导行为。信用分扣除：5分。",
    graphNodes: [
      { id: '0', name: '玩家A', symbolSize: 50, itemStyle: { color: '#ef4444' } },
      { id: '1', name: '异常语音频次', symbolSize: 40 },
      { id: '2', name: '消极位移轨迹', symbolSize: 40 },
      { id: '3', name: '多名队友举报', symbolSize: 40 }
    ],
    graphLinks: [
      { source: '0', target: '1' }, { source: '0', target: '2' }, { source: '0', target: '3' }
    ]
  },
  {
    matchId: "GAME_8830_B",
    timestamp: "2026-03-22 22:30:00",
    reportText: "【状态良好】本次对局未检测到明显的言行不一情况。\n玩家语音指令与战术意图高度吻合，团队协作指标正常。环境净化系统未触发警报。",
    graphNodes: [
      { id: '0', name: '玩家B', symbolSize: 50, itemStyle: { color: '#22c55e' } },
      { id: '1', name: '正常交流', symbolSize: 30 },
      { id: '2', name: '有效助攻', symbolSize: 30 }
    ],
    graphLinks: [
      { source: '0', target: '1' }, { source: '0', target: '2' }
    ]
  }
]);

const isModalOpen = ref(false);
const currentMatch = ref(null);
const graphDom = ref(null); // 获取图表容器的引用
let myChart = null;

// 打开报告弹窗
const openReport = async (match) => {
  currentMatch.value = match;
  isModalOpen.value = true;

  // 必须等待弹窗渲染完成
  await nextTick();
  renderGraph(match.graphNodes, match.graphLinks);
};

// 关闭报告弹窗
const closeReport = () => {
  isModalOpen.value = false;
  if (myChart) {
    myChart.dispose();
    myChart = null;
  }
};

// 渲染 ECharts 关系图
const renderGraph = (nodes, links) => {
  if (!graphDom.value) return;

  myChart = echarts.init(graphDom.value, 'dark');

  const option = {
    backgroundColor: 'transparent',
    tooltip: {},
    series: [
      {
        type: 'graph',
        layout: 'force',
        animation: false,
        label: { show: true, position: 'right', color: '#fff' },
        draggable: true,
        data: nodes,
        links: links,
        roam: true,
        force: {
          repulsion: 300,
          edgeLength: [50, 100]
        },
        lineStyle: {
          color: '#3b82f6',
          width: 2,
          curveness: 0.3
        }
      }
    ]
  };
  myChart.setOption(option);
};
</script>

<style scoped>
/* 加上 scoped 防止样式污染全局 */
.credit-report-wrapper { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #fff; padding: 20px; min-height: 100vh; }
.record-list { display: flex; flex-direction: column; gap: 15px; max-width: 600px; margin: 0 auto; }
.record-item { background: #1e293b; padding: 15px 20px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; border-left: 4px solid #3b82f6; }
.btn-view { background: #3b82f6; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; transition: 0.3s; font-weight: bold; }
.btn-view:hover { background: #2563eb; box-shadow: 0 0 10px rgba(59, 130, 246, 0.5); }

.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.7); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(5px); }
.modal-content { background: #0f172a; width: 80%; max-width: 1000px; height: 60vh; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 0 20px rgba(59, 130, 246, 0.2); display: flex; flex-direction: column; overflow: hidden; animation: popIn 0.3s ease-out; }
.modal-header { padding: 15px 20px; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; background: #1e293b; }
.close-btn { background: transparent; color: #94a3b8; border: none; font-size: 24px; cursor: pointer; }
.close-btn:hover { color: #ef4444; }

.modal-body { display: flex; flex: 1; overflow: hidden; }
.panel-left { flex: 1; padding: 20px; border-right: 1px solid #334155; overflow-y: auto; }
.panel-right { flex: 1; padding: 20px; display: flex; flex-direction: column; }

.typewriter { overflow: hidden; white-space: pre-wrap; border-right: .15em solid #3b82f6; animation: typing 2s steps(40, end), blink-caret .75s step-end infinite; color: #cbd5e1; line-height: 1.6; }
.trace-graph { flex: 1; width: 100%; min-height: 300px; border-radius: 8px; background: #020617; }

@keyframes popIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
@keyframes blink-caret { from, to { border-color: transparent } 50% { border-color: #3b82f6; } }
</style>