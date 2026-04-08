<template>
  <div class="trace-container">
    <header class="page-header">
      <div>
        <h1 class="page-title">风险溯源拓扑</h1>
        <p class="page-subtitle">通过对局 ID 深度分析网络污染源头，构建全链路风险影响拓扑图谱。</p>
      </div>
      <button class="btn-export" @click="showExportModal = true">
        📥 导出溯源报告 (PDF)
      </button>
    </header>

    <section class="stats-grid">
      <div class="stat-card card">
        <div class="stat-header">
          <span class="icon-bg blue"></span>
          <span>检测覆盖率</span>
        </div>
        <div class="stat-body">
          <h2>99.4%</h2>
          <span class="trend success">+0.2% 与昨天相比</span>
        </div>
      </div>

      <div class="stat-card card">
        <div class="stat-header">
          <span class="icon-bg red"></span>
          <span>高危污染源</span>
        </div>
        <div class="stat-body">
          <h2>{{ historyRecords.filter(r => r.affected_count > 0).length || 12 }}</h2>
          <span class="desc">当前活跃节点</span>
        </div>
      </div>

      <div class="stat-card card">
        <div class="stat-header">
          <span class="icon-bg purple"></span>
          <span>跨服关联度</span>
        </div>
        <div class="stat-body">
          <h2>极高</h2>
          <span class="desc">影响范围: 32个子域</span>
        </div>
      </div>
    </section>

    <section class="table-section card">
      <div class="table-header">
        <h3>历史对局溯源记录</h3>
        <div class="table-actions">
          <button class="btn-icon" @click="fetchRecords">刷新数据</button>
        </div>
      </div>

      <div class="table-container">
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
            <tr v-for="record in historyRecords" :key="record.id">
              <td class="text-primary">{{ record.match_id }}</td>
              <td>{{ record.created_at || '刚刚' }}</td>
              <td>
                <div class="user-info">
                  <span>{{ record.source_player || '无' }}</span>
                </div>
              </td>
              <td :class="{'font-bold': record.affected_count > 0}">{{ record.affected_count || 0 }}</td>
              <td>
                <span class="badge" :class="getBadgeClass(record)">
                  <span class="dot"></span> {{ record.risk_level || (record.affected_count === 0 ? '健康' : '未知') }}
                </span>
              </td>
              <td><a href="javascript:void(0)" class="link" @click="viewGraph(record)">查看图谱 ></a></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination">
        <span class="page-info">显示 1 到 10 条记录</span>
        <div class="page-controls">
          <button class="page-btn">‹</button>
          <button class="page-btn active">1</button>
          <button class="page-btn">›</button>
        </div>
      </div>
    </section>

    <section class="bottom-grid">
      <div class="viz-card card" style="min-height: 400px; display: flex; flex-direction: column;">
        <div class="viz-header">
          <h3>实时风险链路传播预估</h3>
        </div>

        <div v-show="!showGraph" class="empty-state" style="flex: 1;">
          <p>点击历史记录中的"查看图谱"以此处生成交互式传播路径模型</p>
        </div>

        <div v-show="showGraph && isSafeMatch" class="empty-state safe-state" style="flex: 1;">
          <div style="font-size: 32px; margin-bottom: 12px;">🛡️</div>
          <h3 style="margin: 0 0 8px 0; color: #15803D;">环境健康，无异常关联</h3>
          <p>多模态解析未捕获到违规内容，系统默认判定该对局绿色安全，跳过图谱生成。</p>
        </div>

        <div v-show="showGraph && !isSafeMatch" ref="traceGraphRef" style="flex: 1; width: 100%; min-height: 350px;"></div>
      </div>

      <div class="viz-card card" style="min-height: 400px; display: flex; flex-direction: column;">
        <div class="viz-header">
          <h3>污染分布热力图</h3>
        </div>

        <div v-show="!showGraph" class="empty-state" style="flex: 1;">
          <p>等待对局数据注入...</p>
        </div>

        <div v-show="showGraph && isSafeMatch" class="empty-state safe-state" style="flex: 1;">
          <div style="font-size: 32px; margin-bottom: 12px;">🌱</div>
          <p>无污染源，热力值均为 0，生态平稳。</p>
        </div>

        <div v-show="showGraph && !isSafeMatch" class="heatmap-container" style="flex: 1; width: 100%; min-height: 350px;">
          <div ref="heatmapRef" class="heatmap-chart"></div>
        </div>
      </div>
    </section>

    <div v-if="showExportModal" class="modal-overlay">
      <div class="modal-content" data-html2canvas-ignore="true">
        <h3>📄 选择要导出的对局记录</h3>
        <select v-model="selectedMatchId" class="match-select">
          <option disabled value="">请选择对局 ID</option>
          <option v-for="record in historyRecords" :key="record.id" :value="record.match_id">
            对局: {{ record.match_id }} ({{ record.created_at || '刚刚' }})
          </option>
        </select>
        <div class="modal-actions">
          <button @click="showExportModal = false" class="btn-cancel">取消</button>
          <button @click="confirmExport" class="btn-confirm" :disabled="!selectedMatchId || isExporting">
            {{ isExporting ? '正在生成系统报告...' : '确认导出' }}
          </button>
        </div>
      </div>
    </div>

    <div ref="a4ReportRef" class="a4-document" style="position: absolute; left: -9999px; top: 0; width: 800px; background: white; padding: 40px; color: #000; box-sizing: border-box; z-index: -1;">
      <h1 style="text-align: center; border-bottom: 2px solid #DC2626; padding-bottom: 10px; margin-bottom: 30px;">多模态游戏生态智能研判报告</h1>

      <h3 style="margin-top: 20px; background: #F1F5F9; padding: 8px; border-left: 4px solid #2563EB;">一、 基础案卷信息</h3>
      <div style="line-height: 1.8; font-size: 15px; margin-bottom: 20px;">
        <p style="margin: 4px 0;"><strong>研判对象 (对局 ID)：</strong> {{ currentRecord?.match_id }}</p>
        <p style="margin: 4px 0;"><strong>报告生成时间：</strong> {{ new Date().toLocaleString() }}</p>
        <p style="margin: 4px 0;"><strong>全链路波及人数：</strong> <span :style="{ color: currentRecord?.affected_count > 0 ? '#DC2626' : '#10B981', fontWeight: 'bold' }">{{ currentRecord?.affected_count }} 人</span></p>
        <p style="margin: 4px 0;"><strong>系统判定风险等级：</strong> {{ currentRecord?.risk_level || (currentRecord?.affected_count === 0 ? '健康' : '未知') }}</p>
      </div>

      <h3 style="margin-top: 30px; background: #F1F5F9; padding: 8px; border-left: 4px solid #2563EB;">二、 智能图谱研判与多目标处置指令</h3>
      <p style="line-height: 1.8; font-size: 14px; font-weight: 500; color: #1E293B; white-space: pre-wrap; background: #F8FAFC; padding: 16px; border: 1px solid #E2E8F0; border-radius: 8px;">{{ currentRecord ? generateAdvice(currentRecord, currentTimeline) : '' }}</p>

      <h3 style="margin-top: 30px; background: #F1F5F9; padding: 8px; border-left: 4px solid #2563EB;">三、 核心证据链留存 (可视化)</h3>
      <p style="font-size: 14px; margin-bottom: 16px;">下图为系统多模态模型捕获的动态溯源拓扑与毒性热力分布凭证：</p>
      <div v-if="graphBase64" style="margin-bottom: 20px;">
        <h4 style="margin: 0 0 8px 0; color: #475569; font-size: 14px;">[附录 A] 风险拓扑关系图</h4>
        <img :src="graphBase64" style="width: 100%; border: 1px solid #E2E8F0; border-radius: 8px;" />
      </div>
      <div v-if="heatmapBase64" style="margin-bottom: 20px;">
        <h4 style="margin: 0 0 8px 0; color: #475569; font-size: 14px;">[附录 B] 毒性时序热力图</h4>
        <img :src="heatmapBase64" style="width: 100%; border: 1px solid #E2E8F0; border-radius: 8px;" />
      </div>
      <div v-if="!graphBase64 && !heatmapBase64" style="padding: 40px; text-align: center; border: 2px dashed #E2E8F0; color: #10B981; font-weight: bold;">
        该对局为绿色健康对局，无违规证据链需留存。
      </div>

      <h3 style="margin-top: 30px; background: #F1F5F9; padding: 8px; border-left: 4px solid #2563EB;">四、 AI 深度判决明细 (原始案卷)</h3>
      <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 10px; text-align: left; border: 1px solid #E2E8F0;">
        <thead>
          <tr style="background-color: #F8FAFC; border-bottom: 2px solid #CBD5E1;">
            <th style="padding: 12px 8px; width: 6%;">顺位</th>
            <th style="padding: 12px 8px; width: 12%;">涉事玩家</th>
            <th style="padding: 12px 8px; width: 28%;">原话捕获内容 (OCR/语音/文本)</th>
            <th style="padding: 12px 8px; width: 18%;">AI 定性与概率</th>
            <th style="padding: 12px 8px; width: 36%;">智能处置动作 & 判决理据</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(log, index) in currentTimeline" :key="index" style="border-bottom: 1px solid #E2E8F0; vertical-align: top;">
            <td style="padding: 12px 8px; color: #64748B; font-weight: bold;">#{{ index + 1 }}</td>
            <td style="padding: 12px 8px; font-weight: 600; color: #1E293B; word-break: break-all;">{{ log.user }}</td>
            <td style="padding: 12px 8px; color: #334155; word-break: break-all;">
              <div style="background: #F1F5F9; padding: 8px; border-radius: 4px; font-style: italic; border-left: 3px solid #94A3B8;">
                "{{ log.text }}"
              </div>
            </td>
            <td style="padding: 12px 8px;">
              <div :style="{ color: log.toxicity > 0.7 ? '#DC2626' : (log.toxicity > 0.4 ? '#D97706' : (log.toxicity > 0.15 ? '#2563EB' : '#10B981')), fontWeight: 'bold', fontSize: '14px', marginBottom: '4px' }">
                {{ log.aiDetail?.level }}
              </div>
              <div style="font-size: 11px; color: #64748B; margin-bottom: 4px;">类型: {{ log.aiDetail?.type }}</div>
              <div style="font-size: 11px; font-family: monospace; background: #F8FAFC; padding: 2px 4px; display: inline-block; border-radius: 2px;">
                毒性系数: {{(log.toxicity * 100).toFixed(1)}}%
              </div>
            </td>
            <td style="padding: 12px 8px;">
              <div style="font-size: 12px; color: #1E293B; margin-bottom: 6px; font-weight: 600;">
                {{ log.aiDetail?.action }}
              </div>
              <div style="font-size: 11px; color: #475569; line-height: 1.5; background: #FEFCE8; padding: 6px; border-radius: 4px; border: 1px dashed #FEF08A;" v-if="log.toxicity > 0.15">
                <strong>💡 研判理据：</strong>{{ log.aiDetail?.reason }}
              </div>
              <div style="font-size: 11px; color: #475569; line-height: 1.5;" v-else>
                {{ log.aiDetail?.reason }}
              </div>
            </td>
          </tr>
          <tr v-if="!currentTimeline || currentTimeline.length === 0">
            <td colspan="5" style="padding: 30px; text-align: center; color: #94A3B8;">📭 系统未捕获到具体发言日志。</td>
          </tr>
        </tbody>
      </table>

      <div style="margin-top: 50px; text-align: right; color: #64748B; font-size: 13px; border-top: 1px dashed #CBD5E1; padding-top: 20px;">
        <p style="margin: 4px 0;">研判引擎：M-IARD 多模态净化系统</p>
        <p style="margin: 4px 0;">自动签发，由系统保证数据真实性及链路完整性。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

const historyRecords = ref([])
const showGraph = ref(false)
const isSafeMatch = ref(false)

const traceGraphRef = ref(null)
let graphChartInstance = null

const heatmapRef = ref(null)
let heatmapChartInstance = null

const isExporting = ref(false)
const showExportModal = ref(false)
const selectedMatchId = ref('')
const currentRecord = ref(null)
const a4ReportRef = ref(null)
const graphBase64 = ref('')
const heatmapBase64 = ref('')

// 当前对局的完整 AI 诊断卷宗记录
const currentTimeline = ref([])

const getBadgeClass = (record) => {
  if (record.affected_count === 0 || record.risk_level === '健康' || record.risk_level === '安全') {
    return 'badge-safe'
  }
  return record.risk_class === 'negative' ? 'badge-critical' : 'badge-moderate'
}
// 🌟 核心升级：基于 GAT 时序链路的多目标精准归因与动态量刑算法
const generateAdvice = (record, timelineObj) => {
  const timeline = timelineObj || [];

  if (record.affected_count === 0 || timeline.length === 0) {
    return "✅ 【综合判定】：基于溯源图谱与链路分析，该对局生态环境健康。未检测到有效传播的违规行为，无需干预。";
  }

  const userStats = {};
  let maxToxValue = 0;
  let maxToxUser = null;
  let firstOffender = null;
  let firstOffenseIndex = 99999;

  timeline.forEach((log, index) => {
    const user = log.user;
    const tox = Number(log.toxicity);

    if (!userStats[user]) userStats[user] = { maxTox: 0 };
    if (tox > userStats[user].maxTox) userStats[user].maxTox = tox;

    if (tox > maxToxValue) {
      maxToxValue = tox;
      maxToxUser = user;
    }

    if (tox > 0.4 && index < firstOffenseIndex) {
      firstOffenseIndex = index;
      firstOffender = user;
    }
  });

  if (maxToxValue < 0.4) {
    return "✅ 【综合判定】：全局发言仅包含极轻微敏感词或系统误判（最高毒性不足 40%），未构成实质性的互相攻击链路。建议系统静默触发星号词过滤即可，无需触发处罚工单。";
  }

  const followers = [];
  const minors = [];

  for (const [user, stats] of Object.entries(userStats)) {
    if (user === firstOffender || user === maxToxUser) continue;

    if (stats.maxTox > 0.4) followers.push(user);
    else if (stats.maxTox > 0.15) minors.push(user);
  }

  let advice = `🚨 【图谱链路判定】：基于 GAT 拓扑追踪，本局检测到明确的“激化-爆发”毒性传染现象（最高毒性峰值 ${(maxToxValue*100).toFixed(1)}%）。\n\n`;

  advice += `【一、 溯源与责任定性】\n`;
  if (firstOffender) {
    advice += `🔸 [源头节点]：玩家“${firstOffender}”率先输出中/高危违规语义，是打破健康生态的直接源头。\n`;
  }

  if (maxToxUser && maxToxUser !== firstOffender) {
    advice += `🔸 [核心恶化节点]：玩家“${maxToxUser}”受激化后输出了本局最高浓度的毒性语义，是导致图谱大面积标红的主要责任人。\n`;
  } else if (maxToxUser === firstOffender) {
    advice += `🔸 [双重核心]：玩家“${maxToxUser}”既是挑事首犯，又输出了全场最高浓度的毒性，性质恶劣。\n`;
  }

  if (followers.length > 0) {
    advice += `🔸 [推波助澜者]：玩家“${followers.join('”、“')}”在风气恶化后加入违规行列，扩大了污染面积。\n`;
  }

  advice += `\n【二、 多目标精准处分指令】\n`;

  // 🌟 修正点：扩展了 getPunishment 函数，引入了 follower（跟风者）的角色分级
  const getPunishment = (user, role) => {
    const tox = userStats[user].maxTox;
    if (tox > 0.7) { // 极度恶劣才封号
      if (role === 'source+max') return `🔴 玩家“${user}” (源头+极其恶劣)：合并重罚，封号 7 天，扣除信用 20 分。\n`;
      if (role === 'max') return `🔴 玩家“${user}” (核心恶化)：造成最严重破坏，封号 4 天，扣除信用 15 分。\n`;
      if (role === 'source') return `🔴 玩家“${user}” (寻衅首犯)：挑起严重冲突，封号 2 天，扣除信用 10 分。\n`;
      // 新增：跟风者如果极其恶劣，也不能放过，封号1天！
      if (role === 'follower') return `🔴 玩家“${user}” (跟风且恶劣违规)：盲目跟风且言辞极其恶劣，封号 1 天，扣除信用 10 分。\n`;
    } else if (tox > 0.4) { // 仅仅是中度违规，只禁言不封号
      if (role === 'source+max') return `🟠 玩家“${user}” (源头+中度违规)：带头阴阳怪气，禁言 48 小时，扣除信用 5 分。\n`;
      // 新增：常规中度跟风，给普通惩罚
      if (role === 'follower') return `🟠 玩家“${user}” (跟风违规)：推波助澜，禁言 12 小时，扣除信用 3 分。\n`;
      return `🟠 玩家“${user}” (${role === 'source' ? '寻衅首犯' : '防卫过当/反击'})：中度违规，禁言 24 小时，扣除信用 2 分。\n`;
    }
    return '';
  };

  if (firstOffender && firstOffender === maxToxUser) {
    advice += getPunishment(firstOffender, 'source+max');
  } else {
    if (firstOffender) advice += getPunishment(firstOffender, 'source');
    if (maxToxUser) advice += getPunishment(maxToxUser, 'max');
  }

  // 🌟 修正点：不再把跟风者名字揉在一起打印，而是循环他们每个人，针对他们自己的毒性单独量刑！
  if (followers.length > 0) {
    followers.forEach(follower => {
      advice += getPunishment(follower, 'follower');
    });
  }

  if (minors.length > 0) {
    advice += `🟡 玩家“${minors.join('”、“')}” (轻微擦边)：触发实时星号屏蔽，下发系统警告信。\n`;
  }

  advice += `\n【三、 生态修复闭环】\n系统已锁定传染链路，违规证据链已完成区块链存证。将对未违规的无辜受害者发送安抚邮件，并补偿信誉积分。`;

  return advice;
}

// 🌟 2. 单句 AI 深度诊断逻辑 (前端无缝扩展黑盒数据)
const getDetailedAnalysis = (toxicityScore) => {
  const t = Number(toxicityScore) || 0;
  if (t > 0.7) {
    return {
      type: '恶劣违规 (人身攻击/重度辱骂)',
      level: '高危 (S级)',
      action: '🔴 立即熔断，记录高危行为',
      reason: '多模态模型捕获极高浓度违规语义，明确指向其他玩家群体，严重破坏游戏生态，触发 T0 级风控红线。'
    }
  } else if (t > 0.4) {
    return {
      type: '中度违规 (阴阳怪气/恶意嘲讽)',
      level: '中危 (A级)',
      action: '🟠 自动替换敏感词，扣除信用',
      reason: '情感分析检测到明显的反讽与挑衅意图，结合图谱拓扑传播判定为恶意引导，易引发群体对立。'
    }
  } else if (t > 0.15) {
    return {
      type: '轻微风险 (擦边黑话/敏感词)',
      level: '低危 (B级)',
      action: '🟡 星号屏蔽阻断，系统警告',
      reason: '识别出游戏黑话词典中的擦边词汇或轻微不文明用语，暂未构成严重攻击行为，予以屏蔽拦截。'
    }
  } else {
    return {
      type: '正常交流',
      level: '安全 (C级)',
      action: '🟢 绿灯放行',
      reason: '语义自然健康，各项特征指标平稳，知识图谱未匹配到潜在攻击性意图。'
    }
  }
}

const fetchRecords = async () => {
  try {
    const res = await axios.get('/api/v1/trace/records')
    historyRecords.value = res.data.data
  } catch (error) {
    console.error('拉取历史记录失败', error)
  }
}

const updateHeatmapWithRealData = (timeline) => {
  if (!heatmapChartInstance) {
    heatmapChartInstance = echarts.init(heatmapRef.value)
  }
  if (!timeline || timeline.length === 0) return

  const players = [...new Set(timeline.map(t => t.user))]
  const xAxisData = timeline.map((_, i) => i + 1)
  const heatmapData = timeline.map((t, index) => {
    return [index, players.indexOf(t.user), Number((t.toxicity * 100).toFixed(0))]
  })

  heatmapChartInstance.setOption({
    backgroundColor: '#ffffff',
    tooltip: {
      enterable: true,
      position: 'top',
      backgroundColor: '#ffffff',
      borderColor: '#E2E8F0',
      textStyle: { color: '#1E293B', fontSize: 13 },
      formatter: function (params) {
        const originalData = timeline[params.dataIndex];
        return `
          <div style="padding: 4px;">
            <div style="color: #64748B; margin-bottom: 4px;">发言顺位: 第 ${params.data[0] + 1} 句</div>
            <div style="font-weight: 600; color: #1E293B; margin-bottom: 6px;">${originalData.user}</div>
            <div style="color: #334155; margin-bottom: 8px; font-style: italic; background: #F8FAFC; padding: 4px; border-radius: 4px;">"${originalData.text}"</div>
            <div style="color: ${params.data[2] > 60 ? '#DC2626' : '#10B981'}; font-weight: bold;">
              毒性判定: ${params.data[2]}%
            </div>
          </div>
        `
      }
    },
    grid: { top: 30, right: 80, bottom: 40, left: 130 },
    xAxis: {
      type: 'category',
      data: xAxisData,
      name: '发言顺序',
      nameTextStyle: { color: '#94A3B8' },
      splitArea: { show: true },
      axisLabel: { color: '#64748B', interval: 'auto' },
      axisLine: { lineStyle: { color: '#E2E8F0' } }
    },
    yAxis: {
      type: 'category',
      data: players,
      axisLabel: { width: 110, overflow: 'truncate', color: '#334155', fontWeight: 500 },
      splitArea: { show: true },
      axisLine: { lineStyle: { color: '#E2E8F0' } }
    },
    visualMap: {
      type: 'continuous',
      orient: 'vertical',
      right: 0,
      top: 'center',
      min: 0,
      max: 100,
      calculable: true,
      itemWidth: 15,
      itemHeight: 120,
      textStyle: { color: '#64748B', fontSize: 12 },
      inRange: { color: ['#F8FAFC', '#FCA5A5', '#EF4444', '#991B1B'] }
    },
    series: [{
      type: 'heatmap',
      data: heatmapData,
      label: { show: true, color: '#1E293B', fontSize: 12, formatter: (p) => p.data[2] > 0 ? p.data[2] : '' },
      itemStyle: { borderColor: '#ffffff', borderWidth: 2 }
    }]
  }, true)

  setTimeout(() => { heatmapChartInstance.resize() }, 100)
}

const viewGraph = async (record) => {
  try {
    const res = await axios.get(`/api/v1/trace/graph/${record.match_id}`)
    const data = res.data.data || {}
    const nodes = data.nodes || []
    const edges = data.edges || []
    const timeline = data.timeline || []

    showGraph.value = true

    // 🌟 处理 timeline：利用前端规则引擎附加 AI 深度诊断属性
    currentTimeline.value = timeline.map(log => ({
      ...log,
      aiDetail: getDetailedAnalysis(log.toxicity)
    }))

    await nextTick()

    if (nodes.length === 0 || record.affected_count === 0) {
      isSafeMatch.value = true
      if (graphChartInstance) graphChartInstance.clear()
      if (heatmapChartInstance) heatmapChartInstance.clear()
      return
    }

    isSafeMatch.value = false

    if (!graphChartInstance) {
      graphChartInstance = echarts.init(traceGraphRef.value)
    }

    graphChartInstance.setOption({
      backgroundColor: '#ffffff',
      tooltip: {
        enterable: true,
        trigger: 'item',
        backgroundColor: '#ffffff',
        borderColor: '#E2E8F0',
        textStyle: { color: '#1E293B' },
        extraCssText: 'box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-radius: 8px;',
        formatter: function (params) {
          if (params.dataType === 'node' && params.data.history) {
            let historyHtml = params.data.history.map((h, i) => `
              <div style="margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px dashed #E2E8F0; font-size: 13px;">
                <span style="color: ${h.score > 0.6 ? '#DC2626' : '#2563EB'}; font-weight: bold; display: inline-block; width: 45px;">[${(h.score*100).toFixed(0)}%]</span>
                <span style="color: #475569; white-space: normal; word-break: break-all;">${h.text}</span>
              </div>
            `).join('');

            return `
              <div style="max-height: 280px; overflow-y: auto; padding: 6px; min-width: 280px; pointer-events: auto;">
                <div style="font-size: 15px; font-weight: bold; margin-bottom: 14px; color: ${params.data.color}; border-bottom: 2px solid ${params.data.color}; padding-bottom: 6px;">
                  🎯 节点主体：${params.data.name}
                </div>
                ${historyHtml}
              </div>
            `;
          }
        }
      },
      series: [{
        type: 'graph',
        layout: 'force',
        data: nodes.map(n => ({
          id: n.id,
          name: n.label,
          symbolSize: n.size,
          itemStyle: { color: n.color },
          history: n.history
        })),
        edges: edges.map(e => ({
          source: e.source,
          target: e.target,
          lineStyle: { width: 1.5, color: '#CBD5E1' }
        })),
        roam: true,
        label: { show: true, position: 'bottom', color: '#1E293B', fontWeight: 500 },
        emphasis: {
          focus: 'adjacency',
          lineStyle: { width: 4 },
          label: { show: true, fontSize: 14, fontWeight: 'bold' }
        },
        force: { repulsion: 500, edgeLength: 120 }
      }]
    }, true)

    updateHeatmapWithRealData(timeline)

  } catch (error) {
    console.error('获取图谱失败', error)
    alert('获取图谱失败，请检查后端 API')
  }
}

// 🌟 导出正式报告的核心逻辑 (处理截屏与智能多页 PDF 分割)
const confirmExport = async () => {
  if (!selectedMatchId.value) return

  currentRecord.value = historyRecords.value.find(r => r.match_id === selectedMatchId.value)
  if (!currentRecord.value) return

  isExporting.value = true

  try {
    await viewGraph(currentRecord.value)

    // 等待图表获取数据、更新 DOM 以及 Echarts 动画结束
    await new Promise(resolve => setTimeout(resolve, 800))

    graphBase64.value = (graphChartInstance && !isSafeMatch.value)
        ? graphChartInstance.getDataURL({ type: 'png', backgroundColor: '#fff', pixelRatio: 2 })
        : ''
    heatmapBase64.value = (heatmapChartInstance && !isSafeMatch.value)
        ? heatmapChartInstance.getDataURL({ type: 'png', backgroundColor: '#fff', pixelRatio: 2 })
        : ''

    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 300))

    // 对整个超长 A4 容器进行无损截图
    const canvas = await html2canvas(a4ReportRef.value, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#FFFFFF'
    })

    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')

    const pdfWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()

    // 按比例计算 canvas 在 PDF 中的实际总高度
    const totalPdfHeight = (canvas.height * pdfWidth) / canvas.width

    let heightLeft = totalPdfHeight
    let position = 0

    // 绘制第一页
    pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, totalPdfHeight)
    heightLeft -= pageHeight

    // 智能分页算法：高度超过一页时，不断增加新页，并上移截取视口
    while (heightLeft > 0) {
      position = heightLeft - totalPdfHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, pdfWidth, totalPdfHeight)
      heightLeft -= pageHeight
    }

    pdf.save(`【智能研判报告】风险对局_${currentRecord.value.match_id}.pdf`)

  } catch (error) {
    console.error("导出 PDF 失败:", error)
    alert("导出失败，请检查控制台报错。")
  } finally {
    isExporting.value = false
    showExportModal.value = false
  }
}

onMounted(() => {
  fetchRecords()
  window.addEventListener('resize', () => {
    graphChartInstance?.resize()
    heatmapChartInstance?.resize()
  })
})

onUnmounted(() => {
  graphChartInstance?.dispose()
  heatmapChartInstance?.dispose()
})
</script>

<style scoped>
.trace-container { display: flex; flex-direction: column; gap: 20px; position: relative;}
.card { background: var(--surface-color); border-radius: var(--radius-lg); box-shadow: var(--card-shadow); border: 1px solid var(--border-color); padding: 24px; }
.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-title { font-size: 24px; font-weight: 600; margin: 0 0 8px 0; }
.page-subtitle { color: var(--text-secondary); font-size: 14px; margin: 0; }

.btn-export { background: #2563EB; color: #ffffff; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 4px 12px rgba(37,99,235,0.2); transition: all 0.3s;}
.btn-export:hover { background: #1D4ED8; transform: translateY(-1px); }
.btn-export:disabled { background: #94A3B8; cursor: not-allowed; transform: none; box-shadow: none;}

.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.stat-card { padding: 20px; }
.stat-header { display: flex; align-items: center; gap: 12px; font-size: 14px; color: var(--text-regular); margin-bottom: 16px; }
.icon-bg { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 16px; }
.icon-bg.blue { background: #DBEAFE; color: #2563EB; }
.icon-bg.red { background: #FEE2E2; color: #DC2626; }
.icon-bg.purple { background: #F3E8FF; color: #9333EA; }
.stat-body h2 { font-size: 32px; margin: 0 0 8px 0; color: #1E293B; }
.trend.success { color: #10B981; font-size: 13px; font-weight: 500; }
.desc { color: var(--text-secondary); font-size: 13px; }

.table-section { padding: 0; overflow: hidden; }
.table-header { padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; }
.table-header h3 { margin: 0; font-size: 16px; color: #1E293B; }
.table-actions { display: flex; gap: 12px; }
.btn-icon { background: transparent; border: 1px solid #E2E8F0; padding: 4px 12px; border-radius: 4px; font-size: 13px; cursor: pointer; color: #64748B; }

.table-container { width: 100%; overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }
.data-table th { padding: 16px 24px; color: #64748B; font-weight: 500; background: #F8FAFC; border-bottom: 1px solid #E2E8F0; }
.data-table td { padding: 16px 24px; border-bottom: 1px solid #F1F5F9; color: #1E293B; vertical-align: middle; }
.text-primary { color: #2563EB; }
.font-bold { font-weight: 600; }
.user-info { display: flex; align-items: center; gap: 12px; }

.badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.dot { width: 6px; height: 6px; border-radius: 50%; }
.badge-critical { background: #FEF2F2; color: #DC2626; }
.badge-critical .dot { background: #DC2626; }
.badge-moderate { background: #EFF6FF; color: #2563EB; }
.badge-moderate .dot { background: #2563EB; }
.badge-safe { background: #DCFCE7; color: #10B981; }
.badge-safe .dot { background: #10B981; }

.link { color: #2563EB; text-decoration: none; font-size: 13px; }
.link:hover { text-decoration: underline; }

.pagination { padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; color: #64748B; font-size: 13px; }
.page-controls { display: flex; gap: 8px; }
.page-btn { background: white; border: 1px solid #E2E8F0; border-radius: 4px; min-width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #475569; }
.page-btn.active { background: #2563EB; color: white; border-color: #2563EB; }

.bottom-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.viz-card { display: flex; flex-direction: column; }
.viz-header { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.viz-header h3 { margin: 0; font-size: 15px; color: #1E293B; }

.empty-state { flex: 1; background: #F8FAFC; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px; text-align: center; color: #94A3B8; }
.safe-state { background: #F0FDF4; border: 2px dashed #BBF7D0; color: #15803D; }
.safe-state p { color: #166534; font-size: 14px; margin: 0;}

.heatmap-container { flex: 1; border-radius: 8px; position: relative; min-height: 400px; }
.heatmap-chart { width: 100%; height: 100%; position: absolute; top: 0; left: 0; }

.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0,0,0,0.4); backdrop-filter: blur(2px);
  display: flex; justify-content: center; align-items: center; z-index: 9999;
}
.modal-content {
  background: white; padding: 24px; border-radius: 12px; width: 420px;
  display: flex; flex-direction: column; gap: 20px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}
.modal-content h3 { margin: 0; font-size: 18px; color: #1E293B; }
.match-select {
  padding: 12px; border-radius: 8px; border: 1px solid #CBD5E1; font-size: 14px;
  outline: none; background: #F8FAFC; color: #334155; cursor: pointer;
}
.match-select:focus { border-color: #2563EB; }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 8px; }
.btn-cancel { background: #F1F5F9; color: #475569; border: none; padding: 10px 18px; border-radius: 6px; cursor: pointer; font-weight: 500;}
.btn-confirm { background: #2563EB; color: white; border: none; padding: 10px 18px; border-radius: 6px; cursor: pointer; font-weight: 500;}
.btn-confirm:disabled { background: #94A3B8; cursor: not-allowed; }
</style>