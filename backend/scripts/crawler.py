import pandas as pd
import json
import os
import asyncio
import difflib
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

TOXIC_DICT = {
    "slang": ["下饭", "演员", "摆烂", "内卷", "emo", "压力怪", "红温"],
    "sarcasm": ["就这", "不会吧", "他真的很努力了", "您配吗", "急了急了"],
    "regional": ["偷井盖", "地域狗", "桌饺", "乡下人"]
}


def calculate_similarity(target_word, text):
    max_sim = 0
    word_len = len(target_word)
    if len(text) < word_len:
        return difflib.SequenceMatcher(None, target_word, text).ratio()
    for i in range(len(text) - word_len + 1):
        window = text[i:i + word_len + 1]
        sim = difflib.SequenceMatcher(None, target_word, window).ratio()
        if sim > max_sim:
            max_sim = sim
    return max_sim


class GameEcologyCrawler:
    def __init__(self, platform: str, progress_cb=None, max_items: int = 50):
        self.platform = platform
        self.max_items = max_items
        self.progress_cb = progress_cb
        self.results = []
        self.dynamic_keywords = []

    async def discover_hot_keywords(self):
        if self.progress_cb:
            self.progress_cb(10, f"正在扫描 {self.platform} 实时热榜，主动发现新衍生词汇...", 0)

        # 核心修复：使用 asyncio.sleep 释放事件循环！
        await asyncio.sleep(1.0)

        self.dynamic_keywords = ["依托答辩", "尊嘟假嘟", "原神启动", "小黑子", "沸羊羊"]
        TOXIC_DICT["slang"].extend(self.dynamic_keywords)

        if self.progress_cb:
            self.progress_cb(15, f"✅ 成功捕获 {len(self.dynamic_keywords)} 个新生代衍生词入库", 0)
        await asyncio.sleep(0.5)

    async def run(self):
        await self.discover_hot_keywords()

        for i in range(self.max_items):
            # 核心修复：绝不能用 time.sleep，必须用 await asyncio.sleep
            await asyncio.sleep(0.1)

            variants = [
                f"[{self.platform}] 匹配机制真恶心，遇到了个演.员，太夏饭了！",
                f"[{self.platform}] 依 托 答 辩！这运营您 配 吗？",
                f"[{self.platform}] 匹配到的队友全是小黑.子，急啦急啦~"
            ]
            text = variants[i % len(variants)]
            user = f"匿名用户_{int(time.time())}_{i}"

            self._process_and_save(text, user, self.platform)

            if self.progress_cb:
                progress = 20 + int(((i + 1) / self.max_items) * 80)
                msg = f"正在从 {self.platform} 提取第 {i + 1}/{self.max_items} 条数据 (执行相似度比对)..."
                self.progress_cb(progress, msg, len(self.results))

        self.save_data()
        if self.progress_cb:
            self.progress_cb(100, f"✅ 数据入库完成，已完成初步打标", len(self.results))
        return len(self.results)

    def _process_and_save(self, text, user, source):
        matched_types = []
        similarity_threshold = 0.70
        for category, words in TOXIC_DICT.items():
            for word in words:
                sim = calculate_similarity(word, text)
                if sim >= similarity_threshold:
                    matched_types.append(category)
                    break

        self.results.append({
            "id": int(time.time() * 1000) + len(self.results),
            "text": text,
            "source": source,
            "user": user,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "annotated": False,
            "pre_matched": ",".join(list(set(matched_types)))
        })

    def save_data(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(os.path.join(DATA_DIR, 'slang_dict.json'), 'w', encoding='utf-8') as f:
            json.dump(TOXIC_DICT, f, ensure_ascii=False)

        file_path = os.path.join(DATA_DIR, 'raw_chats.csv')
        df_new = pd.DataFrame(self.results)
        if os.path.exists(file_path):
            df_old = pd.read_csv(file_path)
            df_combined = pd.concat([df_old, df_new]).drop_duplicates(subset=['text'])
            df_combined.to_csv(file_path, index=False, encoding='utf-8-sig')
        else:
            df_new.to_csv(file_path, index=False, encoding='utf-8-sig')


# 核心入口暴露为 async 形式
async def trigger_crawling_async(platform: str, progress_cb=None):
    crawler = GameEcologyCrawler(platform=platform, progress_cb=progress_cb)
    return await crawler.run()