# 文件路径: backend/app/services/video_analysis_service.py
import os
import warnings

warnings.filterwarnings("ignore")

# 引入你的底层真实大模型
from app.ml_models.nlp_model import RoBERTaAnalyzer
from app.ml_models.behavior_model import LSTMAutoencoder

# 【大模型加载开关】尊重原架构，通过环境变量控制 (建议真实联调时设为 True)
ENABLE_AI = os.getenv("ENABLE_AI", "True") == "True"

roberta_model = None
lstm_model = None

if ENABLE_AI:
    print(">> [言行不一模块] 准备加载序列重构与语义双塔模型...")
    try:
        # 这里的路径和初始化取决于你们组内部 models 的实现，保持原有调用方式
        roberta_model = RoBERTaAnalyzer()
        lstm_model = LSTMAutoencoder()
        print(">> [言行不一模块] 🎉 RoBERTa 与 LSTM 模型加载成功！")
    except Exception as e:
        raise RuntimeError(f">> [言行不一模块] ❌ 模型加载失败，请检查权重文件: {e}")
else:
    print(">> [言行不一模块] ⚠️ 注意：未开启真实 AI 引擎 (ENABLE_AI=False)")


def process_video_for_inconsistency(video_path: str, player_id: str, extracted_texts: list = None,
                                    extracted_actions: list = None):
    """
    真实的言行不一特征计算逻辑
    参数:
        video_path: 视频文件存储路径
        player_id: 玩家标识
        extracted_texts: 真实的语音转文字列表 (应由 Whisper 提取后传入)
        extracted_actions: 真实的行为序列列表 (应由 CV 提取后传入)
    """
    print(f"\n--- [深蓝卫士] 开始真实言行不一特征计算: 针对视频流 {video_path} ---")

    # 【防拟合锁 1】如果没开 AI，拒绝返回假分数！
    if not ENABLE_AI or roberta_model is None or lstm_model is None:
        raise ValueError("AI引擎未加载！拒绝使用拟合假数据，请开启真实模型后再试。")

    # 【防拟合锁 2】特征提取阶段 (严格要求真实数据)
    if not extracted_texts or not extracted_actions:
        # 实际项目中，这里应当调用 Whisper 从 video_path 提取音频转文字
        # 调用 CV/规则脚本从 video_path 提取玩家游戏动作序列
        raise ValueError(f"缺少真实的视频文本或动作特征！当前视频路径: {video_path}。请在传入前完成真实特征提取。")

    # 1. 真实大模型前向推理
    try:
        # 预测文本的积极概率 (嘴上说的话)
        text_prob = roberta_model.predict(extracted_texts)
        # 预测行为的重构误差 (实际的操作到底送没送，异常度)
        behavior_error = lstm_model.predict(extracted_actions)
    except Exception as e:
        raise RuntimeError(f"模型推理计算过程中出错: {e}")

    print(f">> 真实矩阵计算结果 -> 表面语义积极概率: {text_prob:.4f}, LSTM行为异常误差: {behavior_error:.4f}")

    # 2. 局部言行不一裁定逻辑
    # 核心逻辑：如果嘴上说得很积极(>0.6)，但行为异常度极高(>0.7)，判定为言行不一(典型的“边送边鼓励队友”的阴阳人)
    is_inconsistent = bool(text_prob >= 0.6 and behavior_error >= 0.7)

    # 这里的局部风险等级仅供参考，最终全局毒性应由 report_service 里的 XGBoost 决定
    local_risk_level = "HIGH" if is_inconsistent else "LOW"

    # 注意：不再在这里自己算拟合的 toxicity_score 了，保证各模块职责单一
    return {
        "text_sentiment_prob": float(text_prob),
        "behavior_anomaly_score": float(behavior_error),
        "is_inconsistent": is_inconsistent,
        "local_risk_level": local_risk_level
    }