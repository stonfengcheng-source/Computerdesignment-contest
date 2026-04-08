# backend/app/services/report_service.py
import numpy as np


def generate_comprehensive_report(player_id: str, text_toxicity: float, audio_toxicity: float, behavior_anomaly: float,
                                  graph_risk: float):
    """
    使用多模态决策融合 (XGBoost) 汇总各个维度的毒性分数，生成最终报告。
    """
    # 1. 组装多模态特征向量 [文本毒性, 语音情绪毒性, 行为异常度, 社交传染风险]
    features = np.array([[text_toxicity, audio_toxicity, behavior_anomaly, graph_risk]])

    # === XGBoost 融合决策模拟 ===
    # 实际项目中这里应为: model = xgb.Booster(); model.load_model('xgboost.json'); preds = model.predict(DMatrix(features))
    # 这里用加权公式模拟模型输出 (根据各模态在阴阳怪气/违规中的重要性)
    fused_toxicity_score = (
            text_toxicity * 0.65 +  # BERT 文本语义
            audio_toxicity * 0.00 +  # Wav2Vec2 语气
            behavior_anomaly * 0.00 +  # LSTM 挂机/送人头
            graph_risk * 0.35  # GAT 社交溯源污染度
    )

    # 2. 评级判定
    if fused_toxicity_score > 0.8:
        risk_level = "高危 (建议封号)"
        summary = "该玩家在多模态分析中表现出严重的违规倾向，语言毒性极高且伴有送人头等破坏游戏体验的行为，且处于社交污染源头。"
    elif fused_toxicity_score > 0.5:
        risk_level = "中等 (建议禁言)"
        summary = "该玩家存在明显的阴阳怪气及网络黑话违规，虽无严重挂机行为，但语言存在破坏生态风险。"
    else:
        risk_level = "健康"
        summary = "未发现明显违规行为，游戏生态健康。"

    # 3. 返回结构化报告
    return {
        "player_id": player_id,
        "final_toxicity_score": round(fused_toxicity_score, 4),
        "risk_level": risk_level,
        "modules_breakdown": {
            "text_nlp_score": round(text_toxicity, 4),
            "audio_emotion_score": round(audio_toxicity, 4),
            "behavior_lstm_score": round(behavior_anomaly, 4),
            "social_gat_score": round(graph_risk, 4)
        },
        "report_summary": summary
    }