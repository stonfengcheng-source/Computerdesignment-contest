import cv2
import numpy as np
import os

from app.ml_models.text_model import get_toxicity_score
from app.ml_models.gat_model import extract_chat_from_video

BLACK_LIST = ["乡里人", "乡巴佬", "偷井盖", "南蛮", "白完", "东百", "小日本", "漂亮国", "弯弯", "西八"]

def process_video_for_inconsistency(video_path: str, player_id: str):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"视频文件未找到: {video_path}")

    # ================= 真实计算 1: 行为流特征提取 =================
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception("无法解码此视频文件")

    frame_count = 0
    motion_scores = []
    ret, prev_frame = cap.read()

    if ret:
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        while True:
            ret, frame = cap.read()
            if not ret or frame_count > 300:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_diff = cv2.absdiff(prev_gray, gray)
            motion_score = np.sum(frame_diff) / 255.0
            motion_scores.append(motion_score)

            prev_gray = gray
            frame_count += 1
    cap.release()

    behavior_error = min(np.mean(motion_scores) / 100000.0, 1.0) if motion_scores else 0.0

    # ================= 真实计算 2: OCR 弹幕提取 & NLP 文本毒性 =================
    print(f"🚀 正在对视频 {video_path} 进行真实的 OCR 文字提取...")
    extracted_texts = extract_chat_from_video(video_path)

    max_text_prob = 0.0
    if extracted_texts:
        for text in extracted_texts:
            clean_text = text.split("：")[-1] if "：" in text else text

            # 🚀 绝杀拦截逻辑
            if any(bw in clean_text for bw in BLACK_LIST):
                print(f"🚨 [视频流拦截]: 检测到歧视词汇，强制标红！")
                prob = 0.95
            else:
                prob_dict = get_toxicity_score(clean_text)
                prob = float(prob_dict.get("toxicity_score", 0.0))

            print(f"💬 [实时分析]: 【{clean_text}】 👉 违规概率: {prob:.4f}")

            if prob > max_text_prob:
                max_text_prob = prob
    else:
        max_text_prob = 0.05

    text_prob = max_text_prob
    toxicity_score = (text_prob * 0.6) + (behavior_error * 0.4)
    is_inconsistent = bool(toxicity_score > 0.65)

    if toxicity_score > 0.8:
        risk_level = "高危"
    elif toxicity_score > 0.6:
        risk_level = "中危"
    else:
        risk_level = "安全"

    return float(text_prob), float(behavior_error), float(toxicity_score), is_inconsistent, risk_level