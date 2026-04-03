import os
import torch
import torch.nn.functional as F
from torch_geometric.nn import GATConv
from torch_geometric.data import Data
import networkx as nx

# ========================
# 视频读取 + OCR 文字提取
# ========================
import cv2
import re
import easyocr
import numpy as np
import time
from tqdm import tqdm
from difflib import SequenceMatcher

# ========================
# 【GPU 加速】完全保留
# ========================
ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=True)

# ========================
# 【文件路径】完全保留
# ========================
save_dir = r"D:\cmputer\Computerdesignment-contest\backend\app\ml_models"
os.makedirs(save_dir, exist_ok=True)
txt_original_path = os.path.join(save_dir, "文本识别.txt")
txt_cleaned_path = os.path.join(save_dir, "文本识别_清洗后.txt")
txt_final_cleaned_path = os.path.join(save_dir, "文本识别_最终干净版.txt")

f_original = open(txt_original_path, "w", encoding="utf-8")
f_original.write("===== 游戏聊天识别结果（原始未清洗）=====\n\n")
f_original.flush()

cleaned_records = []
SIMILAR_THRESHOLD = 0.7
MIN_CONTENT_LENGTH = 5

# ==============================================
# 【✅ 超级强化：英雄名全修正 + 模糊匹配】
# ==============================================
standard_players = {}
hero_name_list = [
    "马超", "貂蝉", "小乔", "李白", "刘备", "诸葛亮",
    "韩信", "后羿", "亚瑟", "安琪拉", "妲己", "狄仁杰",
    "典韦", "墨子", "孙斌", "鲁班七号", "庄周", "刘禅",
    "高渐离", "阿轲", "钟无艳", "孙悟饭", "孙尚香"
]

# 英雄错别字修正
hero_fix_map = {}
for h in hero_name_list:
    if h == "马超":
        for k in ["马", "马超", "马起", "写超", "马操", "马曹", "马操"]:
            hero_fix_map[k] = "马超"
    if h == "貂蝉":
        for k in ["貂", "婵", "掉婵", "貂'"]:
            hero_fix_map[k] = "貂蝉"
    if h == "小乔":
        for k in ["乔", "少乔", "小乔", "乔乔", "少赤"]:
            hero_fix_map[k] = "小乔"
    if h == "李白":
        for k in ["李", "白", "小白"]:
            hero_fix_map[k] = "李白"

# ==============================================
# 【✅ 强化修正：玩家名自动统一】
# ==============================================
def fix_player_and_hero(player, hero):
    global standard_players

    # 1. 清理玩家名：去掉乱码符号
    player = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '', player).strip()
    hero = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '', hero).strip()

    # 2. 强制修正英雄名
    if hero in hero_fix_map:
        hero = hero_fix_map[hero]

    # 3. 模糊匹配英雄（解决OCR完全认错）
    best_hero = hero
    max_sim = 0
    for h in hero_name_list:
        sim = SequenceMatcher(None, hero, h).ratio()
        if sim > max_sim:
            max_sim = sim
            best_hero = h
    if max_sim > 0.5:
        hero = best_hero

    # 4. 同一英雄下，玩家名自动统一
    if hero not in standard_players:
        standard_players[hero] = []
    for std_p in standard_players[hero]:
        if SequenceMatcher(None, player, std_p).ratio() > 0.7:
            return std_p, hero

    # 5. 加入标准库
    standard_players[hero].append(player)
    return player, hero

# ==============================================
# 【你的原有函数】
# ==============================================
def extract_chat_from_video(video_path, sample_rate=30):
    print(f"\n▶ 开始读取视频：{video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ 无法打开视频文件：{video_path}")
        return []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    video_duration = total_frames / fps
    print(f"📊 视频信息：总帧数{total_frames} | 帧率{fps:.1f}fps")

    frame_idx = 0
    chat_x1, chat_y1 = 0.00, 0.60
    chat_x2, chat_y2 = 0.90, 0.95

    pattern = re.compile(r'(.+)\((.+)\)[:：]\s*(.+)')
    already_recognized = set()
    final_result = []
    pbar = tqdm(total=total_frames, desc="视频读取进度", unit="帧")
    last_update_time = time.time()

    def calc_similarity(a, b):
        return SequenceMatcher(None, a, b).ratio()

    def is_similar_to_existing(new_text):
        for existing_text in cleaned_records:
            new_content = new_text.split("| [发言] ")[-1]
            existing_content = existing_text.split("| [发言] ")[-1]
            similarity = calc_similarity(new_content, existing_content)
            if similarity >= SIMILAR_THRESHOLD:
                return True
        return False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % sample_rate == 0:
            h, w = frame.shape[:2]
            x1 = int(w * chat_x1)
            y1 = int(h * chat_y1)
            x2 = int(w * chat_x2)
            y2 = int(h * chat_y2)
            chat_region = frame[y1:y2, x1:x2]
            gray = cv2.cvtColor(chat_region, cv2.COLOR_BGR2GRAY)
            result = ocr_reader.readtext(gray, detail=0)

            for text in result:
                text = text.strip()
                if len(text) < 8:
                    continue

                match = pattern.search(text)
                if match:
                    player = match.group(1).strip()
                    hero = match.group(2).strip()
                    content = match.group(3).strip()

                    # ==============================================
                    # 【✅ 自动修正名字 + 英雄】
                    # ==============================================
                    player, hero = fix_player_and_hero(player, hero)
                    final_text = f"{player}({hero})：{content}"

                    if final_text not in already_recognized:
                        print(f"\n✅ {final_text}")
                        f_original.write(final_text + "\n")
                        f_original.flush()
                        already_recognized.add(final_text)
                        final_result.append(final_text)

                        if not is_similar_to_existing(final_text):
                            cleaned_records.append(final_text)

        current_time = time.time()
        if current_time - last_update_time >= 0.5:
            pbar.update(frame_idx - pbar.n)
            pbar.set_postfix({"已识别": len(final_result)})
            last_update_time = current_time

        frame_idx += 1

    pbar.update(total_frames - pbar.n)
    pbar.close()
    cap.release()
    print(f"\n✅ 视频读取完成！共识别 {len(final_result)} 条")
    return final_result

# ==============================================
# 主函数
# ==============================================
if __name__ == "__main__":
    print("="*60)
    print("📌 王者荣耀聊天识别系统（强化自动修正版）")
    print("="*60)

    VIDEO_PATH = r"D:\桌面\ScreenRecording_03-20-2026 22-58-29_1.MP4"

    if os.path.exists(VIDEO_PATH):
        texts = extract_chat_from_video(VIDEO_PATH)
    else:
        print(f"\n❌ 视频不存在")

    f_original.close()

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

    print(f"\n💾 文件已保存：")
    print(f"📄 原始文件：{txt_original_path}")
    print(f"📄 清洗后文件：{txt_cleaned_path}")
    print(f"📄 最终干净文件：{txt_final_cleaned_path}")
    print("\n" + "="*60)
    print("✅ 所有任务执行完成！")
    print("="*60)