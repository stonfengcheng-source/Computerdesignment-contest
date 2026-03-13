# 文件路径: app/services/video_analysis_service.py
import os
from app.ml_models.nlp_model import RoBERTaAnalyzer
from app.ml_models.behavior_model import LSTMAutoencoder

# 从系统的环境变量中读取配置，默认不开 AI
ENABLE_AI = os.getenv("ENABLE_AI", "False") == "True"

roberta_model = None
lstm_model = None

# 只有当开关打开时，才去加载这几百兆的真实模型
if ENABLE_AI:
    print(">> [AI 引擎] 已启用，正在加载真实模型...")
    weight_dir = os.path.join(os.getcwd(), "data", "weights")
    roberta_model = RoBERTaAnalyzer() # 或者填入你的本地路径
    lstm_model = LSTMAutoencoder()
else:
    print(">> [AI 引擎] 未启用 (开发测试模式)，使用 Mock 数据。")


def process_video_for_inconsistency(video_path: str, player_id: str):
    """
    言行不一模块的核心逻辑层
    注意：根据分治策略，此时的文本和行为数据由前置模块（或 Mock 数据）提供
    """
    print(f"\n--- [深蓝卫士] 开始言行不一模块分析: 针对视频流 {video_path} ---")

    # 严谨的预留接口：当前使用模拟测试数据，后续直接对接特征提取模块的输出
    extracted_texts = ["兄弟们稳住，交给我来操作"]
    extracted_actions = [
        {"gold": 60, "kda": 0, "move": 2},
        {"gold": 80, "kda": 0, "move": 1}
    ]

    # 1. 真实大模型推理层
    print(">> 双塔神经网络前向传播计算中...")
    text_prob = roberta_model.predict(extracted_texts)
    behavior_error = lstm_model.predict(extracted_actions)

    print(f">> 底层矩阵计算结果 -> NLP积极概率: {text_prob:.4f}, LSTM重构误差: {behavior_error:.4f}")

    # 2. 多模态特征融合层 (M-IARD)
    toxicity_score = (text_prob * 0.4) + (behavior_error * 0.6)

    is_inconsistent = False
    risk_level = "LOW"

    if text_prob >= 0.6 and behavior_error >= 0.7:
        is_inconsistent = True
        risk_level = "HIGH"

    return text_prob, behavior_error, toxicity_score, is_inconsistent, risk_level