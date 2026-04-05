import os
import cv2
import re
import time
import numpy as np
from tqdm import tqdm
from difflib import SequenceMatcher
from datetime import datetime

# ========================
# 1. 引擎初始化
# ========================
try:
    from rapidocr_onnxruntime import RapidOCR

    ocr_engine = RapidOCR()
    print("✅ 成功加载 RapidOCR (高精度模式)")
except ImportError:
    print("❌ 严重错误: 必须安装 RapidOCR。终端执行: pip install rapidocr_onnxruntime")
    exit(1)

# ========================
# 2. 路径配置 (确保前端能读到)
# ========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
output_dir = os.path.join(BASE_DIR, "output")
legacy_dir = os.path.join(BASE_DIR, "app", "ml_models")
os.makedirs(output_dir, exist_ok=True)
os.makedirs(legacy_dir, exist_ok=True)

latest_log_path_1 = os.path.join(output_dir, "文本识别.txt")
latest_log_path_2 = os.path.join(legacy_dir, "文本识别.txt")

for path in [latest_log_path_1, latest_log_path_2]:
    with open(path, "w", encoding="utf-8") as f_init:
        f_init.write("===== 游戏多模态实时捕获流 =====\n\n")


def write_and_flush(filepath, text):
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(text + "\n")
        f.flush()
        os.fsync(f.fileno())


# ========================
# 3. 词表与名字锁定机制
# ========================
HERO_LIST = [
    "暃", "云缨", "百里玄策", "百里守约", "李白", "荆轲", "澜", "孙悟空", "赵云", "镜", "橘右京",
    "马超", "娜可露露", "云中君", "不知火舞", "上官婉儿", "花木兰", "司马懿", "兰陵王", "元歌",
    "韩信", "裴擒虎", "貂蝉", "嫦娥", "沈梦溪", "米莱狄", "弈星", "杨玉环", "女娲", "干将莫邪",
    "诸葛亮", "钟馗", "张良", "王昭君", "姜子牙", "露娜", "安琪拉", "武则天", "甄姬", "周瑜",
    "芈月", "扁鹊", "孙膑", "高渐离", "嬴政", "妲己", "墨子", "小乔", "后羿", "黄忠", "狄仁杰",
    "鲁班七号", "成吉思汗", "虞姬", "伽罗", "孙尚香", "李元芳", "公孙离", "马可波罗", "司空震",
    "夏洛特", "蒙恬", "曜", "盘古", "孙策", "狂铁", "苏烈", "铠", "李信", "哪吒", "杨戬",
    "雅典娜", "夏侯惇", "关羽", "刘备", "曹操", "典韦", "宫本武藏", "吕布", "钟无艳", "亚瑟",
    "达摩", "老夫子", "程咬金", "猪八戒", "梦奇", "瑶", "明世隐"
]

hero_fix_map = {
    "马": "马超", "写超": "马超", "马操": "马超", "马曹": "马超",
    "貂": "貂蝉", "婵": "貂蝉", "掉婵": "貂蝉",
    "乔": "小乔", "少乔": "小乔", "乔乔": "小乔",
    "李": "李白", "白": "李白", "小白": "李白",
    "半月": "芈月", "辈月": "芈月", "月": "芈月", "半": "芈月",
    "娥": "嫦娥", "常娥": "嫦娥", "鲁班": "鲁班七号"
}


def refine_hero_name(raw_name):
    clean_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '', raw_name).strip()
    if not clean_name: return "未知"
    if clean_name in hero_fix_map: return hero_fix_map[clean_name]

    best_match, highest_sim = clean_name, 0
    for hero in HERO_LIST:
        sim = SequenceMatcher(None, clean_name, hero).ratio()
        if sim > highest_sim:
            highest_sim, best_match = sim, hero
    return best_match if highest_sim > 0.4 else clean_name


def is_garbage(text_line):
    upper_text = text_line.upper()
    if re.search(r'(Q.*W.*E|A.*S.*D|符号|分词|中英)', upper_text): return True
    if len(re.findall(r'[\u4e00-\u9fa5]', upper_text)) < 2: return True
    return False


# ========================
# 4. 核心提取与多行合并逻辑
# ========================
def extract_chat_from_video(video_path):
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_log_path = os.path.join(output_dir, f"ocr_result_{timestamp_str}.txt")
    print(f"\n▶ 引擎启动：【多行合并+极速版】 -> 永久记录保存至 {os.path.basename(run_log_path)}")

    with open(run_log_path, "w", encoding="utf-8") as f:
        f.write(f"===== 游戏识别日志 ({timestamp_str}) =====\n\n")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened(): return []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30

    # 🎯 提速关键 1：采样率改为 fps（即 1 秒只扫描 1 次，弹幕停留长达 5 秒，绝对扫得到）
    sample_rate = int(fps)

    chat_x1, chat_y1, chat_x2, chat_y2 = 0.00, 0.45, 0.45, 0.90
    pattern = re.compile(r'(.*?)[\(（](.*?)[\)）][:：](.*)')

    MATCH_HERO_PLAYER_MAP = {}
    HERO_CHAT_HISTORY = {}

    final_output = []
    frame_idx = 0
    pbar = tqdm(total=total_frames, desc="视频解析中", unit="帧")
    last_update_time = time.time()

    prev_gray = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        if frame_idx % sample_rate == 0:
            h, w = frame.shape[:2]
            roi = frame[int(h * chat_y1):int(h * chat_y2), int(w * chat_x1):int(w * chat_x2)]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            # 🎯 提速关键 2：放宽光流对比阈值，游戏背景有特效抖动，4.0 以内都算静止
            skip_ocr = False
            if prev_gray is not None:
                if np.mean(cv2.absdiff(prev_gray, gray)) < 4.0:
                    skip_ocr = True
            prev_gray = gray.copy()

            if not skip_ocr:
                result, _ = ocr_engine(gray)

                if result:
                    # 💡 解决截断关键：同一帧内的状态机，负责拼合换行文字
                    current_speaker_player = None
                    current_speaker_hero = None
                    current_content = ""
                    parsed_messages = []

                    for item in result:
                        text_line = item[1].replace(" ", "")
                        if is_garbage(text_line): continue

                        match = pattern.search(text_line)
                        if match:
                            # 发现了新的发言人头部，把刚才积攒的“老发言”先存起来
                            if current_speaker_hero and current_content:
                                parsed_messages.append((current_speaker_player, current_speaker_hero, current_content))

                            raw_player = match.group(1)
                            raw_hero = match.group(2)
                            current_content = match.group(3).strip()

                            # 净化与锁定
                            player = re.sub(r'^[\[【\(（].*?[\]】\)）]', '', raw_player).strip()
                            player = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5\_]', '', player)
                            hero = refine_hero_name(raw_hero)

                            if hero != "未知":
                                if hero not in MATCH_HERO_PLAYER_MAP:
                                    MATCH_HERO_PLAYER_MAP[hero] = player
                                current_speaker_player = MATCH_HERO_PLAYER_MAP[hero]
                                current_speaker_hero = hero
                            else:
                                current_speaker_player, current_speaker_hero = player, hero

                        else:
                            # 💡 没匹配到头部？这很可能是第二行被截断的文本！
                            if current_speaker_hero and current_content:
                                # 剔除标点符号以外的乱码，拼接到刚才的文字末尾
                                clean_cont = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5，。！？、]', '', text_line)
                                if clean_cont:
                                    current_content += clean_cont

                    # 收尾帧内最后一句
                    if current_speaker_hero and current_content:
                        parsed_messages.append((current_speaker_player, current_speaker_hero, current_content))

                    # ==================================
                    # 进行极严格的防漏、防重复校验
                    # ==================================
                    for player, hero, content in parsed_messages:
                        is_duplicate = False
                        if hero in HERO_CHAT_HISTORY:
                            for exist_msg in HERO_CHAT_HISTORY[hero][-8:]:
                                # 如果新内容包含老内容（说明新内容是老内容的完整换行版），我们应该保留新内容！
                                if exist_msg in content and len(content) > len(exist_msg):
                                    pass  # 放行完整版
                                # 如果新内容只是老内容的一部分，或者高度相似，就是重复
                                elif content in exist_msg or SequenceMatcher(None, content, exist_msg).ratio() > 0.80:
                                    is_duplicate = True
                                    break

                        if is_duplicate: continue

                        # 确认是新内容
                        if hero not in HERO_CHAT_HISTORY: HERO_CHAT_HISTORY[hero] = []
                        HERO_CHAT_HISTORY[hero].append(content)

                        cur_sec = int(frame_idx / fps)
                        ts = f"[{cur_sec // 60:02d}:{cur_sec % 60:02d}]"
                        full_entry = f"{ts} {player}({hero}) | [发言] {content}"

                        final_output.append(full_entry)
                        write_and_flush(run_log_path, full_entry)
                        write_and_flush(latest_log_path_1, full_entry)
                        write_and_flush(latest_log_path_2, full_entry)
                        print(f"\n✅ 精准捕获: {full_entry}")

        if time.time() - last_update_time >= 0.5:
            pbar.update(frame_idx - pbar.n)
            pbar.set_postfix({"已捕获": len(final_output)})
            last_update_time = time.time()

        frame_idx += 1

    pbar.update(total_frames - pbar.n)
    pbar.close()
    cap.release()
    return final_output


if __name__ == "__main__":
    test_video = os.path.join(BASE_DIR, "data", "uploads", "测试文件.mp4")
    if os.path.exists(test_video):
        extract_chat_from_video(test_video)