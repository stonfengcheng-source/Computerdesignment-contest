// src/mock/dashboard.js
export default {
  // 顶部卡片数据
  cardData: {
    riskStatements: 1243, // 今日风险言论数
    highRiskUsers: 86,    // 高危用户数
    avgCreditScore: 687,  // 平均信用分
    realTimeProcessing: 35 // 实时处理量
  },

  // 近7天风险趋势
  trendData: {
    dates: ['02-06', '02-07', '02-08', '02-09', '02-10', '02-11', '02-12'],
    values: [120, 135, 142, 158, 149, 165, 172] // 对应风险言论数
  },

  // 风险等级分布（百分比）
  riskDistribution: {
    high: 15,   // 高危
    medium: 30, // 中危
    low: 55     // 低危
  },

  // 平台健康度雷达图指标
  healthIndicators: {
    textToxicity: 82,     // 文本毒性
    abnormalBehavior: 65, // 行为异常
    socialPollution: 71,  // 社交污染
    responseSpeed: 90,    // 响应速度
    coverage: 78          // 覆盖广度
  }
}