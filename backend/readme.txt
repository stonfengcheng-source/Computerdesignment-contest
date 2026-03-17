
# 🛡️ 深蓝卫士 - “言行不一”多模态检测后端模块 (M-IARD)

本模块负责处理并分析游戏对局中玩家的“文本流”与“时序行为流”，通过双塔神经网络（RoBERTa + LSTM）提取特征，并融合判定玩家是否存在“嘴上积极、行为摆烂”等言行不一的隐性破坏游戏生态行为。

## 📁 核心目录结构
```text
backend/
├── app/
│   ├── api/             # 路由控制层
│   ├── ml_models/       # 真实的深度学习模型加载层 (RoBERTa & LSTM)
│   ├── services/        # 多模态数据对齐与 XGBoost 融合业务逻辑
│   └── schemas/         # Pydantic 数据契约
├── data/
│   └── weights/         # [重点] 算法组产出的本地模型权重存放处
├── main.py              # FastAPI 启动入口
├── requirements.txt     # 依赖清单 (包含 hf-transfer 极速下载引擎)
└── local_test.db        # 本地 SQLite 测试数据库
🛠️ 环境配置与安装
确保已安装 Python 3.8+，并在项目根目录创建虚拟环境。

安装所有核心与 AI 依赖：

Bash
pip install -r requirements.txt
🚀 启动与部署模式 (重要！)
为了兼顾“前端同学的低性能电脑”与“算法同学的真实推理需求”，本模块采用了 环境变量动态挂载机制。

模式 A：纯业务开发模式 (前端/数据库同学使用)
不加载几百兆的大模型，瞬间启动，接口直接返回测试数据供 UI 渲染和数据库测试。
启动命令：

Bash
# 直接启动即可，默认不开启 AI 引擎
uvicorn main:app --reload
模式 B：真实 AI 推理模式 (算法/后端联调使用)
将全量加载 RoBERTa 预训练模型与 LSTM 行为特征重构模型。
启动命令 (Windows PowerShell)：

PowerShell
$env:ENABLE_AI="True"
uvicorn main:app --reload
启动命令 (Mac/Linux)：

Bash
export ENABLE_AI=True
uvicorn main:app --reload
注：首次在模式 B 下启动时，系统将自动利用 Rust 并发引擎 (hf-transfer) 与国内镜像源下载约 400MB 的 RoBERTa 基础权重并全局缓存。后续启动将在 1 秒内完成热加载。

🔌 API 接口测试
服务启动后，访问 http://127.0.0.1:8000/docs 进入 Swagger UI 交互式测试文档。

核心端点：POST /api/v1/analyze/video

接收：player_id (表单) 和 video_file (文件流)

返回：包含 NLP 置信度、LSTM 重构误差、XGBoost 融合毒性分 (Toxicity Score) 的标准 JSON。

语义挖掘模块 —— 部署说明 & 代码上传步骤

一、模块说明
本模块负责游戏黑话 / 毒性文本检测，输入一段聊天文本，输出 0~1 的毒性分数（toxicity_score）。
分数可直接供其他模块（如言行不一检测）调用，便于整合。
对外暴露的接口
方法路径说明POST/api/v1/text/analyze_text输入文本，返回毒性分数
请求参数（Form 表单）：
chat_text: string   # 要检测的文本
返回示例：
json{
  "status": "success",
  "chat_text": "你这操作真下饭",
  "toxicity_score": 0.8812
}
供其他模块直接调用的 Python 函数
python# 在你的代码里这样引入即可，不需要走 HTTP 接口
from app.ml_models.text_model import get_toxicity_score

score = get_toxicity_score("你这操作真下饭")
# 返回 float，范围 0.0 ~ 1.0

二、文件结构（只涉及本模块的文件）
backend/
├── app/
│   ├── text_api.py              # 本模块路由（独立文件，不改队友代码）
│   └── ml_models/
│       └── text_model.py        # 模型加载 & 算分函数
├── data/
│   └── weights/
│       └── toxicity_model/      # ← 训练好的模型文件放这里（不上传 git）
│           ├── config.json
│           ├── pytorch_model.bin
│           ├── tokenizer.json
│           └── vocab.txt
└── main.py                      # 队长维护，本模块只在此注册路由（两行）
