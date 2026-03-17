import pandas as pd
import json
import os
import random

def get_data():
    os.makedirs('data', exist_ok=True)
    # 1. 原始对照字典 (Baseline)
    slang_dict = {
        "classic": ["TP", "补刀", "上高", "买活", "肉山"],
        "pollution": ["xxs", "演员", "压力怪", "红温", "这就是DOTA"]
    }
    with open('data/slang_dict.json', 'w', encoding='utf-8') as f:
        json.dump(slang_dict, f, ensure_ascii=False)

    # 2. 模拟爬取真实对话 (包含传播关系)
    # 模拟50个玩家在不同时间点的对话
    players = [f"Player_ID_{i:03d}" for i in range(50)]
    data = []
    for i in range(300):
        sender = random.choice(players)
        # 模拟传播：50%的概率是回复某人
        target = random.choice(players) if random.random() > 0.5 else None
        slang = random.choice(slang_dict["classic"] + slang_dict["pollution"])
        data.append({
            "timestamp": 1710000000 + (i * 60), # 模拟每分钟一条
            "user": sender,
            "target": target,
            "content": f"你这操作真是{slang}...",
            "slang_used": slang
        })
    
    df = pd.DataFrame(data)
    df.to_csv('data/raw_chats.csv', index=False, encoding='utf-8-sig')
    print("[Success] 数据集已生成至 data/raw_chats.csv")

if __name__ == "__main__":
    get_data()