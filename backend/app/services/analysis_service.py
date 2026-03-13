# 文件路径: app/services/analysis_service.py
from app.ml_models.nlp_model import RoBERTaAnalyzer
from app.ml_models.behavior_model import LSTMAutoencoder
import xgboost as xgb
import numpy as np

# 实例化真实的 AI 模型
print("正在初始化后端 AI 引擎...")
roberta_model = RoBERTaAnalyzer()
lstm_model = LSTMAutoencoder()


# 初始化真实的 XGBoost
# ！！！预留给算法同学的位置！！！
# xgb_classifier = xgb.XGBClassifier()
# xgb_classifier.load_model("./models/fusion_xgboost.json")

def process_inconsistency_detection(text_logs, action_logs):
    # 1. 真实大模型推理：提取文本概率 (0.0~1.0)
    text_prob = roberta_model.extract_semantic_prob(text_logs)

    # 2. 真实深度学习推理：计算行为重构误差 Tensor Loss
    reconstruction_error = lstm_model.compute_reconstruction_error(action_logs)

    # 3. 真实 XGBoost 推理阵列对接 (目前用数学权重替代，等算法同学发来 json 模型直接替换此处)
    # 真实写法：
    # features = np.array([[text_prob, reconstruction_error]])
    # is_inconsistent = bool(xgb_classifier.predict(features)[0])

    # 当前过渡写法：
    fusion_score = (text_prob * 0.4) + (reconstruction_error * 0.6)

    is_inconsistent = False
    risk_level = "LOW"

    # 言行不一的严苛判定标准：文本偏正面(>0.6) + 行为重构误差极大(>0.7)
    if text_prob >= 0.6 and reconstruction_error >= 0.7:
        is_inconsistent = True
        risk_level = "HIGH"

    text_feat = {
        "sentiment": "positive_or_sarcastic" if text_prob >= 0.6 else "negative",
        "prob": text_prob
    }

    # 不再返回 toxicity_score，只返回当前模块负责的数据
    return text_feat, reconstruction_error, is_inconsistent, risk_level