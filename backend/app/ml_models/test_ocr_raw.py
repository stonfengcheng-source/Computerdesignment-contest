import os
import cv2
import easyocr
import re
from tqdm import tqdm

# ========================
# 初始化 OCR 引擎
# ========================
print("正在加载 OCR 模型...")
ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=True)

# ========================
# 路径配置
# ========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
save_dir = os.path.join(BASE_DIR, "output")
os.makedirs(save_dir, exist_ok=True)

# 暴力输出文件
dump_path = os.path.join(save_dir, "纯净无过滤_原始视觉.txt")


def raw_video_ocr_dump(video_path, sample_rate=30):
    print(f"\n▶ 启动【全量无过滤】暴力提取模式 -> {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ 无法打开视频：{video_path}")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    with open(dump_path, "w", encoding="utf-8") as f:
        f.write("===== 毫无保留的原始 OCR 视觉日志 =====\n")
        f.write("（此文件记录了 AI 看到的所有碎片，无任何过滤）\n\n")

    frame_idx = 0
    with tqdm(total=total_frames, desc="全量扫描中", unit="帧") as pbar:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            if frame_idx % sample_rate == 0:
                h, w = frame.shape[:2]

                # 🎯 截取整个左半屏 (0~50%宽, 40%~100%高)
                # 必定能覆盖到聊天区，且避开右侧满屏的技能按键干扰
                chat_region = frame[int(h * 0.4):int(h * 1.0), 0:int(w * 0.5)]
                gray = cv2.cvtColor(chat_region, cv2.COLOR_BGR2GRAY)

                # 没有任何修饰，直接读图
                result = ocr_reader.readtext(gray, detail=0)

                if result:
                    raw_text = " | ".join(result)
                    log_line = f"[帧 {frame_idx}] 看到了：{raw_text}"

                    # 实时写入文件
                    with open(dump_path, "a", encoding="utf-8") as f:
                        f.write(log_line + "\n")

                    # 只要包含中文，就在控制台打印，方便你直观感受
                    if re.search(r'[\u4e00-\u9fa5]', raw_text):
                        print(f"\n👀 {log_line}")

            pbar.update(1)
            frame_idx += 1

    cap.release()
    print(f"\n✅ 提取完毕！快去查看文件：{dump_path}")


if __name__ == "__main__":
    VIDEO_PATH = os.path.join(BASE_DIR, "data", "uploads", "测试文件.mp4")
    if os.path.exists(VIDEO_PATH):
        raw_video_ocr_dump(VIDEO_PATH)
    else:
        print(f"❌ 找不到视频文件：{VIDEO_PATH}")