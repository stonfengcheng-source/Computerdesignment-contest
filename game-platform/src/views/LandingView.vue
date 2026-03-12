<template>
  <div class="landing-container" @mousemove="handleMouseMove">
    <div class="top-nav">
      <div class="logo-text">Deep Blue AI</div>
      <button class="login-btn" @click="goToLogin">
        <span>控制台登录</span>
        <div class="btn-glow"></div>
      </button>
    </div>

    <section class="hero-section">
      <div class="bg-title-wrapper" :style="titleTransform">
        <h1 class="massive-title">深蓝卫士</h1>
        <p class="massive-subtitle">多模态网络游戏生态健康度监测与信用评级平台</p>
      </div>

      <div ref="bubbleChart" class="bubble-container" :style="bubbleTransform"></div>

      <div class="scroll-indicator">
        <div class="mouse"></div>
        <span>探索净化链路</span>
      </div>
    </section>

    <div class="story-wrapper">
      <section
        v-for="(section, index) in storySections"
        :key="index"
        :class="`story-section section-${index}`"
        ref="sectionRefs"
      >
        <div class="glass-panel" :class="{ 'reverse': index % 2 !== 0 }">
          <div class="panel-content">
            <div class="tag-label">{{ section.tag }}</div>
            <h2 class="section-title">{{ section.title }}</h2>
            <p class="section-desc">{{ section.desc }}</p>
            <ul class="tech-list">
              <li v-for="(tech, tIndex) in section.techs" :key="tIndex">{{ tech }}</li>
            </ul>
          </div>
          <div class="panel-visual">
             <div class="visual-placeholder">{{ section.visualText }}</div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import * as d3 from 'd3';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);
const router = useRouter();

// --- 鼠标视差交互逻辑 ---
const mousePos = reactive({ x: 0, y: 0 });
const handleMouseMove = (e) => {
  // 计算鼠标相对屏幕中心的偏移量，范围大致在 -1 到 1 之间
  const x = (e.clientX / window.innerWidth) * 2 - 1;
  const y = (e.clientY / window.innerHeight) * 2 - 1;
  mousePos.x = x;
  mousePos.y = y;
};

// 标题和气泡采用不同速率的反向移动，形成 3D 景深
const titleTransform = computed(() => {
  return `transform: translate(${mousePos.x * -30}px, ${mousePos.y * -20}px)`;
});
const bubbleTransform = computed(() => {
  return `transform: translate(${mousePos.x * 40}px, ${mousePos.y * 30}px)`;
});

// --- 页面内容数据 (严格对标 PDF) ---
const storySections = [
  {
    tag: '核心引擎', title: '首创多模态分析净化平台', desc: '聚焦复杂游戏环境，将“关系流+文本流+行为流”深度融合，打破传统单一文本检测瓶颈，精准打击隐蔽违规行为。', techs: ['XGBoost 决策融合', '跨流特征提取'], visualText: '多模态融合模型图'
  },
 {
    tag: '语义解析', title: '阴阳怪气与网络黑话', desc: '面向游戏特色交流体系，结合情感与黑话词库，综合剥离语言毒性，精准识别暗语和嘲讽。', techs: ['BERT 语义理解', 'Wav2Vec2 情绪识别'], visualText: '毒性文本过滤演示'
  },
  {
    tag: '图谱追踪', title: '风险溯源拓扑图', desc: '找出谁先开始的，谁的“污染”最大。通过复杂的图神经网络，追踪社交关系链和攻击传播路径。', techs: ['GAT 图注意力网络', '传播路径计算'], visualText: '关系溯源动态图'
  },
  {
    tag: '信用体系', title: '跨平台用户信用评分', desc: '构建专属于深蓝卫士的复杂异构大数据样本集，综合生成用户总体的游戏信用画像，提供行业接入标准。', techs: ['LSTM 异常检测', '多维数据打分模型'], visualText: '六边形信用雷达图'
  }
];

const sectionRefs = ref([]);
const bubbleChart = ref(null);

const goToLogin = () => {
  router.push('/login');
};

// --- D3 气泡数据 (已去重并设置中心跳转) ---
const bubbleDataTree = {
  // 修改中心节点：设置 route 为 /dashboard
  id: 'core', radius: 110, label: '多模态融合核心', desc: '进入控制台', type: 'center', route: '/dashboard',
  children: [
    { id: 'trace', radius: 85, label: '风险溯源', desc: '找出污染源', type: 'feature', route: '/trace' },
    { id: 'credit', radius: 85, label: '信用评级', desc: '跨平台打分', type: 'feature', route: '/credit' },
    { id: 'sarcasm', radius: 75, label: '情感剥离', desc: '阴阳怪气检测', type: 'feature', route: '/detect' },
    { id: 'slang', radius: 75, label: '对抗词库', desc: '网络黑话解析', type: 'feature', route: '/label' },
    // 仅保留一个异常定位（言行不一）节点，指向新创建的路由
    { id: 'behavior', radius: 75, label: '言行不一', desc: '异常行为定位', type: 'feature', route: '/behavior' }
  ]
};

const flattenNodes = (root) => {
  const nodes = [];
  const stack = [root];
  while (stack.length > 0) {
    const current = stack.pop();
    if (current) {
      nodes.push({ ...current, r: current.radius });
      if (current.children?.length > 0) {
        let i = current.children.length - 1;
        while (i >= 0) {
          stack.push(current.children[i]);
          i--;
        }
      }
    }
  }
  return nodes;
};

let simulation;
let timer;

const initBubbleChart = () => {
  const width = window.innerWidth;
  const height = window.innerHeight;
  const nodes = flattenNodes(bubbleDataTree);
  const featureNodes = nodes.filter(n => n.type === 'feature');

  let idx = 0;
  while (idx < featureNodes.length) {
    const node = featureNodes[idx];
    const angle = (Math.PI * 2 * idx) / featureNodes.length;
    const spreadRadius = Math.min(width, height) * 0.26;
    node.x = width / 2 + Math.cos(angle) * spreadRadius;
    node.y = height / 2 + Math.sin(angle) * spreadRadius;
    idx++;
  }

  const centerNode = nodes.find(n => n.type === 'center');
  if (centerNode) {
    centerNode.x = width / 2;
    centerNode.y = height / 2;
  }

  d3.select(bubbleChart.value).selectAll('*').remove();
  const svg = d3.select(bubbleChart.value).append('svg').attr('width', width).attr('height', height);

  // 强化物理引擎：增加向中心的聚拢力和节点间的弹性碰撞
  simulation = d3.forceSimulation(nodes)
    .force('charge', d3.forceManyBody().strength(-150)) // 适当的排斥力
    .force('charge', d3.forceManyBody().strength(-250)) // 增强排斥力，让布局更松弛
    .force('center', d3.forceCenter(width / 2, height / 2 - 30))
    .force('collide', d3.forceCollide().radius(d => d.r + 8).iterations(4))
    .force('collide', d3.forceCollide().radius(d => d.r + 24).iterations(4))
    .force('radial', d3.forceRadial(d => d.type === 'center' ? 0 : Math.min(width, height) * 0.23, width / 2, height / 2).strength(0.16))
    .force('y', d3.forceY(height / 2).strength(0.05)) // 增加 Y 轴维稳力
    .force('x', d3.forceX(width / 2).strength(0.05)); // 增加 X 轴维稳力

  const nodeGroups = svg.selectAll('.node')
    .data(nodes).enter().append('g').attr('class', 'node')
    .call(d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended))
    .on('click', (event, d) => {
      // 【核心修复】：防止拖拽结束后触发点击跳转
      if (event.defaultPrevented) return;

      // 触发路由跳转
      if (d.route) {
        router.push(d.route);
      }
    });

  // 渲染玻璃质感的气泡
  nodeGroups.append('circle')
    .attr('r', d => d.r)
    .style('fill', d => d.type === 'center' ? 'rgba(255, 255, 255, 0.8)' : 'rgba(240, 248, 255, 0.6)')
    .style('stroke', d => d.type === 'center' ? '#0ea5e9' : '#bae6fd')
    .style('stroke-width', 2)
    .style('box-shadow', '0 10px 25px rgba(14, 165, 233, 0.2)')
    .style('cursor', 'pointer');

  nodeGroups.append('text')
    .text(d => d.label)
    .attr('text-anchor', 'middle').attr('dy', '-0.2em')
    .style('fill', '#0f172a').style('font-size', d => d.r / 3.8 + 'px').style('font-weight', '800')
    .style('pointer-events', 'none');

  nodeGroups.append('text')
    .text(d => d.desc)
    .attr('text-anchor', 'middle').attr('dy', '1.6em')
    .style('fill', '#475569').style('font-size', d => d.r / 6 + 'px').style('font-weight', '600')

  // 【核心修复】：让气泡出场时产生强烈的弹跳感
  simulation.alpha(1).restart();

  simulation.on('tick', () => {
    // 限制气泡不飞出屏幕边界
    let i = 0;
    while(i < nodes.length) {
      let d = nodes[i];
      d.x = Math.max(d.r, Math.min(width - d.r, d.x));
      d.y = Math.max(d.r, Math.min(height - d.r, d.y));
      i++;
    }
  });

  // 持续的呼吸漂浮效果
  timer = d3.timer((elapsed) => {
    nodeGroups.attr('transform', d => {
      const floatY = Math.sin(elapsed * 0.002 + d.id.charCodeAt(0)) * 5;
      return `translate(${d.x},${d.y + floatY})`;
    });
  });

  // 拖拽逻辑完善
  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }
  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }
  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
};

// --- GSAP 滚动动画初始化 ---
const initScrollAnimations = () => {
  const sections = sectionRefs.value;
  let i = 0;

  // 使用 while 循环逐个绑定滚动触发器
  while (i < sections.length) {
    const el = sections[i];
    const isReverse = i % 2 !== 0;

    gsap.fromTo(el,
      { opacity: 0, x: isReverse ? 100 : -100, y: 50 },
      {
        opacity: 1, x: 0, y: 0,
        duration: 1.2,
        ease: "power3.out",
        scrollTrigger: {
          trigger: el,
          start: "top 75%",
          end: "center center",
          toggleActions: "play none none reverse"
        }
      }
    );
    i++;
  }
};

onMounted(() => {
  initBubbleChart();
  // 等待 DOM 渲染完成后初始化 GSAP
  setTimeout(initScrollAnimations, 100);
  window.addEventListener('resize', initBubbleChart);
});

onUnmounted(() => {
  if (simulation) simulation.stop();
  if (timer) timer.stop();
  window.removeEventListener('resize', initBubbleChart);
  ScrollTrigger.getAll().forEach(t => t.kill());
});
</script>

<style scoped>
/* 极光弥散光背景 */
.landing-container {
  width: 100vw;
  min-height: 100vh;
  background-color: #f8fafc;
  background-image:
    radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.15) 0px, transparent 50%),
    radial-gradient(at 100% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(14, 165, 233, 0.1) 0px, transparent 50%),
    radial-gradient(at 0% 100%, rgba(99, 102, 241, 0.1) 0px, transparent 50%);
  color: #0f172a;
  font-family: 'Inter', -apple-system, sans-serif;
  overflow-x: hidden;
}

/* 顶部导航与登录按钮 */
.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  padding: 24px 48px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 100;
  box-sizing: border-box;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 900;
  letter-spacing: 1px;
  color: #0ea5e9;
}

.login-btn {
  position: relative;
  padding: 12px 32px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(14, 165, 233, 0.3);
  border-radius: 30px;
  color: #0284c7;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
}

.login-btn:hover {
  background: #0ea5e9;
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(14, 165, 233, 0.3);
}

/* 视差交互区 */
.hero-section {
  position: relative;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* 融合在背景中的超大标题 */
.bg-title-wrapper {
  position: absolute;
  text-align: center;
  z-index: 1; /* 在气泡下方 */
  pointer-events: none; /* 防止遮挡气泡的鼠标事件 */
  transition: transform 0.1s linear; /* 配合鼠标平滑移动 */
}

.massive-title {
  font-size: 12vw;
  font-weight: 900;
  line-height: 1;
  margin: 0;
  background: linear-gradient(180deg, rgba(14, 165, 233, 0.15) 0%, rgba(59, 130, 246, 0.05) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.02em;
}

.massive-subtitle {
  font-size: 1.5rem;
  color: rgba(71, 85, 105, 0.6);
  font-weight: 600;
  margin-top: -20px;
}

/* 气泡层 */
.bubble-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2; /* 在标题上方 */
  transition: transform 0.1s linear;
}

/* 滚动提示 */
.scroll-indicator {
  position: absolute;
  bottom: 40px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #64748b;
  font-weight: 500;
  gap: 12px;
}

.mouse {
  width: 26px;
  height: 40px;
  border: 2px solid #94a3b8;
  border-radius: 14px;
  position: relative;
}
.mouse::after {
  content: '';
  position: absolute;
  top: 6px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 8px;
  background: #94a3b8;
  border-radius: 2px;
  animation: scrollAnim 1.5s infinite;
}

@keyframes scrollAnim {
  0% { transform: translate(-50%, 0); opacity: 1; }
  100% { transform: translate(-50%, 15px); opacity: 0; }
}

/* 下拉内容区 */
.story-wrapper {
  position: relative;
  z-index: 5;
  padding: 100px 0;
}

.story-section {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 10%;
}

.glass-panel {
  display: flex;
  align-items: center;
  gap: 60px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 40px;
  padding: 60px;
  width: 100%;
  max-width: 1200px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.05);
}

.glass-panel.reverse {
  flex-direction: row-reverse;
}

.panel-content {
  flex: 1;
}

.tag-label {
  display: inline-block;
  padding: 6px 16px;
  background: #e0f2fe;
  color: #0284c7;
  border-radius: 20px;
  font-weight: 700;
  font-size: 0.9rem;
  margin-bottom: 20px;
}

.section-title {
  font-size: 2.8rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 24px;
  line-height: 1.2;
}

.section-desc {
  font-size: 1.15rem;
  color: #475569;
  line-height: 1.7;
  margin-bottom: 32px;
}

.tech-list {
  list-style: none;
  padding: 0;
  display: flex;
  gap: 15px;
}

.tech-list li {
  background: #f1f5f9;
  color: #334155;
  padding: 8px 16px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.95rem;
  border: 1px solid #e2e8f0;
}

.panel-visual {
  flex: 1;
  height: 400px;
  background: linear-gradient(135deg, rgba(241, 245, 249, 0.8), rgba(226, 232, 240, 0.8));
  border-radius: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #cbd5e1;
}

.visual-placeholder {
  color: #94a3b8;
  font-weight: 600;
  font-size: 1.2rem;
}
</style>