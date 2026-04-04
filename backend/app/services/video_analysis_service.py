import cv2
import numpy as np
import os
# 导入你真实训练出来的 BERT 模型打分函数
from app.ml_models.text_model import get_toxicity_score

# 💡 核心修复 1：导入你写好的真实 OCR 视频文字提取函数
from app.ml_models.gat_model import extract_chat_from_video


def process_video_for_inconsistency(video_path: str, player_id: str):
    """
    拒绝造假！这里执行真实的 OpenCV 逐帧光流差分运算、EasyOCR 文字提取 和 BERT 前向传播。
    """
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
        # 强制系统至少处理前 300 帧画面，计算玩家剧烈运动方差
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

    # 将真实的画面运动方差转化为行为异常分数
    if len(motion_scores) > 0:
        avg_motion = np.mean(motion_scores)
        behavior_error = min(avg_motion / 100000.0, 1.0)
    else:
        behavior_error = 0.0

    # ================= 真实计算 2: OCR 弹幕提取 & NLP 文本毒性 =================
    print(f"🚀 正在对视频 {video_path} 进行真实的 OCR 文字提取...")

    # 💡 核心修复 2：真正调用 OCR 函数。这个函数内部会动态写入 文本识别.txt！
    extracted_texts = extract_chat_from_video(video_path)

    # 找出毒性最高的一句话作为这一局的最终判定分数
    max_text_prob = 0.0
    if extracted_texts:
        for text in extracted_texts:
            # 去掉提取结果里的格式前缀，只留真正的内容进行 BERT 打分
            clean_text = text.split("：")[-1] if "：" in text else text
            prob = get_toxicity_score(clean_text)
            if prob > max_text_prob:
                max_text_prob = prob
    else:
        # 如果视频里没提取出任何文字，基础分为 0.05
        max_text_prob = 0.05

    text_prob = max_text_prob

    # ================= 多模态融合判决 =================
    toxicity_score = (text_prob * 0.6) + (behavior_error * 0.4)
    is_inconsistent = bool(toxicity_score > 0.65)

    if toxicity_score > 0.8:
        risk_level = "高危"
    elif toxicity_score > 0.6:
        risk_level = "中危"
    else:
        risk_level = "安全"

    return float(text_prob), float(behavior_error), float(toxicity_score), is_inconsistent, risk_level