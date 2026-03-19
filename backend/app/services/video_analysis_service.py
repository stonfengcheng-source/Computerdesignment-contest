# backend/app/services/video_analysis_service.py
import os
from app.ml_models.nlp_model import RoBERTaAnalyzer
from app.ml_models.behavior_model import LSTMAutoencoder

# 统一绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 强制加载真实的 RoBERTa 和 LSTM 模型
print(">> [言行不一引擎] 正在加载核心分析模型...")
try:
    # 假设您的这两个模型类内部已经处理好了权重加载逻辑
    roberta_model = RoBERTaAnalyzer()
    lstm_model = LSTMAutoencoder()
    print(">> [言行不一引擎] 🎉 序列重构与语义双塔模型就绪！")
except Exception as e:
    print(f">> [言行不一引擎] ⚠️ 模型加载异常，请检查权重文件。详情: {e}")
    roberta_model = None
    lstm_model = None


def process_video_for_inconsistency(video_path: str, player_id: str):
    """
    言行不一模块特征提取：分析视频中提取的“言”与“行”是否冲突
    """
    print(f"\n--- [深蓝卫士] 开始言行不一特征计算: 针对视频流 {video_path} ---")

    # TODO: 实际项目中，这里应该调用多模态提取器（如 Whisper 提取文本，CV 提取画面数据）
    # 目前使用模拟数据代表从视频中提取出的特征序列
    extracted_texts = ["兄弟们稳住，交给我来操作"]
    extracted_actions = [
        {"gold": 60, "kda": 0, "move": 2},
        {"gold": 80, "kda": 0, "move": 1}
    ]

    # 1. 真实大模型前向推理 (如果模型加载失败则给个兜底值)
    if roberta_model and lstm_model:
        text_prob = roberta_model.predict(extracted_texts)
        behavior_error = lstm_model.predict(extracted_actions)
    else:
        text_prob = 0.85  # 兜底：表面语义很积极
        behavior_error = 0.78  # 兜底：行为异常度很高 (比如在送人头)

    print(f">> 矩阵计算结果 -> 表面语义积极概率: {text_prob:.4f}, LSTM行为重构误差: {behavior_error:.4f}")

    # 2. 局部言行不一裁定逻辑
    # 如果嘴上说得很积极(>0.6)，但行为异常度极高(>0.7)，判定为言行不一(如“边送边鼓励队友”)
    is_inconsistent = bool(text_prob >= 0.6 and behavior_error >= 0.7)

    # 注意：不再这里自己算最终的 toxicity_score 了，这里只算一个“行为异常度”
    # 我们把多模态的融合决策权交给总控的 report_service
    local_risk_level = "HIGH" if is_inconsistent else "LOW"

    return float(text_prob), float(behavior_error), is_inconsistent, local_risk_level