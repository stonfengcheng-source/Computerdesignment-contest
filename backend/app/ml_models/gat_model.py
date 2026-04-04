import os
import torch
import cv2
import re
import time
import numpy as np
from tqdm import tqdm
from difflib import SequenceMatcher

# ========================
# 💡 核心升级：切换至 RapidOCR 引擎 (高精度中文识别)
# ========================
try:
    from rapidocr_onnxruntime import RapidOCR

    ocr_engine = RapidOCR()
    print("✅ 成功加载高精度中文引擎: RapidOCR")
except ImportError:
    print("❌ 严重错误: 请务必在终端执行 'pip install rapidocr_onnxruntime'！")
    exit(1)

# ========================
# 路径配置
# ========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
save_dir = os.path.join(BASE_DIR, "output")
os.makedirs(save_dir, exist_ok=True)

txt_original_path = os.path.join(save_dir, "文本识别.txt")
txt_cleaned_path = os.path.join(save_dir, "文本识别_清洗后.txt")
txt_final_cleaned_path = os.path.join(save_dir, "文本识别_最终干净版.txt")

with open(txt_original_path, "w", encoding="utf-8") as f_init:
    f_init.write("===== 游戏多模态实时捕获流 =====\n\n")

cleaned_records = []
SIMILAR_THRESHOLD = 0.7
MIN_CONTENT_LENGTH = 5

# ==============================================
# 英雄名修正 + 模糊匹配 (原版逻辑)
# ==============================================
standard_players = {}
hero_name_list = [
    "马超", "貂蝉", "小乔", "李白", "刘备", "诸葛亮", "韩信", "后羿", "亚瑟",
    "安琪拉", "妲己", "狄仁杰", "典韦", "墨子", "孙斌", "鲁班七号", "庄周",
    "刘禅", "高渐离", "阿轲", "钟无艳", "孙尚香"
]

hero_fix_map = {"马": "马超", "写超": "马超", "马操": "马超", "马曹": "马超",
                "貂": "貂蝉", "婵": "貂蝉", "掉婵": "貂蝉", "貂'": "貂蝉",
                "乔": "小乔", "少乔": "小乔", "乔乔": "小乔", "少赤": "小乔",
                "李": "李白", "白": "李白", "小白": "李白"}


def fix_player_and_hero(player, hero):
    global standard_players
    player = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '', player).strip()
    hero = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '', hero).strip()
    if hero in hero_fix_map: hero = hero_fix_map[hero]

    best_hero, max_sim = hero, 0
    for h in hero_name_list:
        sim = SequenceMatcher(None, hero, h).ratio()
        if sim > max_sim: max_sim, best_hero = sim, h
    if max_sim > 0.5: hero = best_hero

    if hero not in standard_players: standard_players[hero] = []
    for std_p in standard_players[hero]:
        if SequenceMatcher(None, player, std_p).ratio() > 0.7: return std_p, hero
    standard_players[hero].append(player)
    return player, hero


def is_keyboard_or_garbage(text_line):
    """单行文本的键盘及垃圾字符拦截器"""
    upper_text = text_line.upper()
    # 拦截键盘特征
    if re.search(r'(Q.*W.*E|符号|中英|分词|A.*S.*D|发送)', upper_text):
        return True
    return False


# ==============================================
# 核心提取流
# ==============================================
def extract_chat_from_video(video_path, sample_rate=15):
    print(f"\n▶ 引擎启动：基于 RapidOCR 的高精度实机提取 -> {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ 无法打开视频")
        return []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0: fps = 30

    # 聊天区域框定 (只保留左下角聊天区，切掉多余部分)
    chat_x1, chat_y1 = 0.00, 0.50
    chat_x2, chat_y2 = 0.45, 0.90

    # 【极致宽容的正则】：支持带前缀的玩家名、中英文括号、可选的冒号
    # 格式示例： [蓝色ID]张三(李白)：请求集合  或  (队伍)李四（韩信）发起进攻
    pattern_standard = re.compile(r'(?:\[.*?\]|【.*?】|\(.*?\))?\s*(.*?)[\(（](.*?)[\)）][:：]?(.*)')

    already_recognized = set()
    final_result = []

    def calc_similarity(a, b):
        return SequenceMatcher(None, a, b).ratio()

    def is_similar_to_existing(new_text):
        for existing_text in cleaned_records:
            new_content = new_text.split("| [发言] ")[-1] if "| [发言] " in new_text else new_text
            existing_content = existing_text.split("| [发言] ")[-1] if "| [发言] " in existing_text else existing_text
            if calc_similarity(new_content, existing_content) >= SIMILAR_THRESHOLD:
                return True
        return False

    frame_idx = 0
    pbar = tqdm(total=total_frames, desc="视频智能解析中", unit="帧")
    last_update_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        if frame_idx % sample_rate == 0:
            h, w = frame.shape[:2]
            chat_region = frame[int(h * chat_y1):int(h * chat_y2), int(w * chat_x1):int(w * chat_x2)]

            # 使用 RapidOCR 读取（不需要转灰度，它内部处理得更好）
            ocr_result, _ = ocr_engine(chat_region)

            if ocr_result:
                # RapidOCR 会把一整句话作为一个 list item 返回，不需要我们去拼接碎片！
                for item in ocr_result:
                    text_line = item[1].strip()  # 提取出的文本内容

                    if len(text_line) < 5 or is_keyboard_or_garbage(text_line):
                        continue

                    # 计算时间戳
                    current_seconds = int(frame_idx / fps)
                    ts = f"[{current_seconds // 60:02d}:{current_seconds % 60:02d}]"

                    # 尝试匹配格式
                    match = pattern_standard.search(text_line)
                    if match:
                        player = match.group(1).replace("|", "").strip()
                        hero = match.group(2).replace("|", "").strip()
                        content = match.group(3).replace("|", "").strip()

                        if not player or not hero or not content:
                            continue

                        # 剥离杂乱前缀
                        player = re.sub(r'^[【\[\(（].*?[】\]\)）]', '', player).strip()
                        player, hero = fix_player_and_hero(player, hero)

                        final_text = f"{ts} {player}({hero}) | [发言] {content}"

                        if final_text not in already_recognized:
                            with open(txt_original_path, "a", encoding="utf-8") as f_out:
                                f_out.write(final_text + "\n")

                            already_recognized.add(final_text)
                            final_result.append(final_text)
                            print(f"\n✅ 捕获: {final_text}")

                            if not is_similar_to_existing(final_text):
                                cleaned_records.append(final_text)

        if time.time() - last_update_time >= 0.5:
            pbar.update(frame_idx - pbar.n)
            pbar.set_postfix({"已捕获": len(final_result)})
            last_update_time = time.time()

        frame_idx += 1

    pbar.update(total_frames - pbar.n)
    pbar.close()
    cap.release()
    return final_result


if __name__ == "__main__":
    VIDEO_PATH = os.path.join(BASE_DIR, "data", "uploads", "测试文件.mp4")
    if os.path.exists(VIDEO_PATH):
        extract_chat_from_video(VIDEO_PATH)
    else:
        print(f"\n❌ 未找到视频: {VIDEO_PATH}")

    with open(txt_cleaned_path, "w", encoding="utf-8") as f_cleaned:
        f_cleaned.write("===== 游戏聊天识别结果（已清洗去重）=====\n\n")
        for idx, r in enumerate(cleaned_records, 1):
            f_cleaned.write(f"{idx}. {r}\n")

    final_clean_records = []
    for line in cleaned_records:
        try:
            content = line.split("| [发言] ")[1]
            if len(content.strip()) >= MIN_CONTENT_LENGTH:
                final_clean_records.append(line)
        except:
            continue

    with open(txt_final_cleaned_path, "w", encoding="utf-8") as f_final:
        f_final.write("===== 最终干净版（已去重+过滤短句）=====\n\n")
        for idx, r in enumerate(final_clean_records, 1):
            f_final.write(f"{idx}. {r}\n")