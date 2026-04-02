<template>
  <div class="landing-container">
    <section class="hero-section">
      <div class="hero-content">
        <p class="subtitle">专业级净化平台</p>
        <h1 class="title">游戏网络环境净化平台</h1>
        <p class="desc">
          响应“十五五“规划，打造纯净网络环境。多维度精准识别违规行为，守护游戏生态安全，构建文明健康的数字化娱乐空间。
        </p>
        <div class="action-buttons">
          <button class="btn-primary" @click="$router.push('/dashboard')">开始体验</button>
          <button class="btn-outline">了解更多</button>
        </div>
      </div>
      <div class="hero-illustration">
        <div class="mock-window">
          <div class="window-header">
            <span class="dot red"></span>
            <span class="dot yellow"></span>
            <span class="dot blue"></span>
            <svg class="icon-shield text-right" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          </div>
          <div class="window-body">
            <div class="skeleton-line long"></div>
            <div class="skeleton-line medium"></div>
            <div class="skeleton-line short"></div>
            <svg class="shield-big" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          </div>
        </div>
      </div>
    </section>

    <section class="defense-section">
      <div class="defense-text">
        <div class="section-tag">
          <span class="blue-dot"></span> 平台实时监控
        </div>
        <h2>全时段主动防御系统</h2>
        <p>深蓝卫士提供接口，可达成毫秒级的实时流量扫描与行为建模，精准识别违规内容。我们的系统不仅关注文本语义，更深度集成多模态分析技术，能够有效识别图像、语音及各类变体符号中的违规倾向。</p>
        <p>依托自研的深度神经网络，平台可以实现 24/7 无间断监测，自动生成实时风险趋势图，帮助管理人员快速定位网络污染源，确保社区氛围的持续净化与健康发展。</p>
      </div>

      <div class="defense-stats">
        <div class="stats-grid">
          <div class="stat-item">
            <h3>99.9%</h3>
            <p>拦截准确率</p>
          </div>
          <div class="stat-item">
            <h3>15ms</h3>
            <p>平均响应速度</p>
          </div>
          <div class="stat-item">
            <h3>1.2B</h3>
            <p>日均处理请求</p>
          </div>
          <div class="stat-item">
            <h3>24h</h3>
            <p>实时智能轮巡</p>
          </div>
        </div>
        <div class="mock-bar-chart">
          <div class="bar" style="height: 30%;"></div>
          <div class="bar" style="height: 50%;"></div>
          <div class="bar highlight" style="height: 80%;"></div>
          <div class="bar" style="height: 40%;"></div>
          <div class="bar" style="height: 60%;"></div>
          <div class="bar" style="height: 45%;"></div>
          <div class="bar" style="height: 30%;"></div>
          <div class="bar" style="height: 70%;"></div>
          <div class="bar highlight" style="height: 90%;"></div>
        </div>
      </div>
    </section>

    <section class="modules-section">
      <div class="modules-header">
        <h2>核心功能模块</h2>
        <p>整合尖端 AI 能力，提供全链路安全治理方案</p>
      </div>

      <div class="modules-grid">
        <div class="module-card" @click="$router.push('/monitor')">
          <div class="icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
          </div>
          <h3>实时监控</h3>
          <p>毫秒级数据流分析，实时捕获异常动态与违规交互，确保安全无死角。</p>
          <a class="explore-link">立即探索 →</a>
        </div>

        <div class="module-card" @click="$router.push('/detect')">
          <div class="icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
          </div>
          <h3>毒性分析</h3>
          <p>深度语义解析，识别隐晦恶意言论、仇恨词汇及其各种变体形态。</p>
          <a class="explore-link">立即探索 →</a>
        </div>

        <div class="module-card" @click="$router.push('/trace')">
          <div class="icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
          </div>
          <h3>风险溯源拓扑</h3>
          <p>追溯恶意行为的传播链条与源头，构建全链路风险影响拓扑图谱。</p>
          <a class="explore-link">立即探索 →</a>
        </div>

        <div class="module-card" @click="$router.push('/label')">
          <div class="icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
          </div>
          <h3>对抗数据标注</h3>
          <p>利用主动学习机制，针对新型对抗攻击进行高效样本标注与模型迭代。</p>
          <a class="explore-link">立即探索 →</a>
        </div>
      </div>
    </section>

    <footer class="landing-footer">
      <div class="footer-left">
        <span class="footer-logo">深蓝卫士</span>
        <span class="copyright">© 2026 深蓝卫士 - 网络环境净化领导者</span>
      </div>
      <div class="footer-links">
        <a>服务条款</a>
        <a>隐私政策</a>
        <a>联系我们</a>
      </div>
      <div class="footer-icons">
        <button class="icon-btn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg></button>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.landing-container {
  display: flex;
  flex-direction: column;
  gap: 40px;
  margin: -24px; /* 抵消 Layout 中 default padding */
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
}

/* 1. Hero 区域 */
.hero-section {
  background: linear-gradient(135deg, #1D4ED8 0%, #3B82F6 100%);
  border-radius: 0 0 24px 24px;
  padding: 80px 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #ffffff;
}
.hero-content {
  max-width: 50%;
}
.hero-content .subtitle {
  font-size: 13px;
  letter-spacing: 2px;
  opacity: 0.8;
  margin-bottom: 16px;
  font-weight: 500;
}
.hero-content .title {
  font-size: 48px;
  font-weight: 700;
  margin: 0 0 24px 0;
  line-height: 1.2;
}
.hero-content .desc {
  font-size: 16px;
  line-height: 1.6;
  opacity: 0.9;
  margin-bottom: 40px;
}
.action-buttons {
  display: flex;
  gap: 16px;
}
.btn-primary {
  background: #ffffff;
  color: #1D4ED8;
  border: none;
  padding: 12px 32px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}
.btn-primary:hover {
  background: #F8FAFC;
  transform: translateY(-2px);
}
.btn-outline {
  background: transparent;
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.5);
  padding: 12px 32px;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}
.btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
}

.hero-illustration {
  width: 40%;
}
.mock-window {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}
.window-header {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 8px;
}
.dot { width: 10px; height: 10px; border-radius: 50%; }
.dot.red { background: #EF4444; }
.dot.yellow { background: #F59E0B; }
.dot.blue { background: #3B82F6; }
.icon-shield { width: 16px; height: 16px; opacity: 0.7; }
.text-right { margin-left: auto; }
.window-body {
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.skeleton-line { height: 12px; background: rgba(255, 255, 255, 0.2); border-radius: 6px; width: 100%;}
.skeleton-line.long { width: 90%; }
.skeleton-line.medium { width: 70%; }
.skeleton-line.short { width: 50%; }
.shield-big { width: 80px; height: 80px; margin-top: 24px; opacity: 0.8; color: #fff;}

/* 2. 防御系统区域 */
.defense-section {
  display: flex;
  padding: 40px 60px;
  gap: 60px;
  align-items: center;
}
.defense-text { flex: 1; }
.section-tag {
  color: #2563EB;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.blue-dot { width: 8px; height: 8px; background: #2563EB; border-radius: 50%; }
.defense-text h2 { font-size: 32px; margin: 0 0 24px 0; color: #1E293B; font-weight: 600; }
.defense-text p { font-size: 15px; color: #475569; line-height: 1.8; margin-bottom: 16px; }

.defense-stats { flex: 1; background: #fff; border-radius: 16px; padding: 30px; box-shadow: 0 4px 24px rgba(0,0,0,0.03); border: 1px solid #F1F5F9;}
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; text-align: center; margin-bottom: 30px; }
.stat-item h3 { font-size: 24px; color: #1D4ED8; margin: 0 0 8px 0; font-weight: 700;}
.stat-item p { font-size: 12px; color: #64748B; margin: 0; }
.mock-bar-chart { display: flex; align-items: flex-end; justify-content: space-between; height: 120px; gap: 4px; border-bottom: 1px solid #E2E8F0; padding-bottom: 8px;}
.mock-bar-chart .bar { flex: 1; background: #E2E8F0; border-radius: 4px 4px 0 0; transition: height 0.3s;}
.mock-bar-chart .bar.highlight { background: #2563EB; }

/* 3. 核心功能模块 */
.modules-section { padding: 40px 60px 80px 60px; background: #F8FAFC; }
.modules-header { text-align: center; margin-bottom: 40px; }
.modules-header h2 { font-size: 28px; color: #1E293B; margin: 0 0 12px 0; font-weight: 600;}
.modules-header p { color: #64748B; font-size: 15px; margin: 0; }
.modules-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.module-card {
  background: #ffffff;
  padding: 30px 24px;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.02);
  border: 1px solid #F1F5F9;
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
  display: flex;
  flex-direction: column;
}
.module-card:hover { transform: translateY(-4px); box-shadow: 0 12px 30px rgba(0,0,0,0.06); border-color: #DBEAFE; }
.icon-box { width: 48px; height: 48px; background: #EFF6FF; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; color: #2563EB; }
.icon-box svg { width: 24px; height: 24px; }
.module-card h3 { font-size: 18px; margin: 0 0 12px 0; color: #1E293B; font-weight: 600;}
.module-card p { font-size: 13px; color: #64748B; line-height: 1.6; flex: 1; margin: 0 0 20px 0; }
.explore-link { color: #2563EB; text-decoration: none; font-size: 14px; font-weight: 500; }

/* 4. 页脚 */
.landing-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30px 60px;
  background: #F8FAFC;
  border-top: 1px solid #E2E8F0;
  color: #64748B;
  font-size: 13px;
}
.footer-left { display: flex; align-items: center; gap: 16px; }
.footer-logo { color: #2563EB; font-size: 18px; font-weight: bold; }
.footer-links { display: flex; gap: 24px; }
.footer-links a { color: #64748B; cursor: pointer; }
.footer-links a:hover { color: #2563EB; }
.footer-icons { display: flex; gap: 12px; }
.icon-btn { background: #fff; border: 1px solid #E2E8F0; border-radius: 50%; width: 32px; height: 32px; cursor: pointer; display: flex; align-items: center; justify-content: center; color: #64748B;}
</style>