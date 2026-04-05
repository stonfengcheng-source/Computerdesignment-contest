import pandas as pd
import networkx as nx
import torch
import os
import numpy as np

# 统一使用原生文本大模型
from app.ml_models.text_model import get_toxicity_score

BLACK_LIST = ["乡里人", "乡巴佬", "偷井盖", "南蛮", "白完", "东百", "小日本", "漂亮国", "弯弯", "西八"]


def build_graph_data(csv_path):
    if not os.path.exists(csv_path):
        return None, None, None, None, None, None

    print("正在启动 NLP 引擎提取节点特征...")
    df = pd.read_csv(csv_path, encoding='utf-8-sig')

    G = nx.DiGraph()

    player_stats = {}
    risk_source_player = None
    timeline_data = []  # 🌟 新增：专门为前端真实热力图准备的完整时间线

    for idx, row in df.iterrows():
        node_id = str(idx)
        u = str(row.get('user', f'未知用户{idx}'))
        text = str(row.get('text', ''))

        if any(bw in text for bw in BLACK_LIST):
            score = 0.95
        else:
            # 🌟 核心修复：只把纯净的【text】喂给模型，绝对不要把前缀拼进去，否则模型会掉精度！
            prob_dict = get_toxicity_score(text)
            score = float(prob_dict.get("toxicity_score", 0.0))

        # 记录到时间线数组
        timeline_data.append({
            "user": u,
            "text": text,
            "toxicity": score,
            "step": idx
        })

        if u not in player_stats:
            player_stats[u] = {"max_score": score, "history": [], "is_source": False}

        player_stats[u]["max_score"] = max(player_stats[u]["max_score"], score)
        # 🌟 核心改进：把这个玩家说过的每一句话都存起来！
        player_stats[u]["history"].append({"text": text, "score": score})

        # 抓出第一个高危爆发点作为源头
        if score > 0.8 and risk_source_player is None:
            risk_source_player = u
            player_stats[u]["is_source"] = True

    # 构建前端节点 (以玩家为单位)
    frontend_nodes = []
    features_list = []
    for player, stats in player_stats.items():
        color = '#F56C6C' if stats['is_source'] else ('#E6A23C' if stats['max_score'] > 0.6 else '#67C23A')
        size = 60 if stats['is_source'] else (45 if stats['max_score'] > 0.6 else 30)

        frontend_nodes.append({
            "id": player,
            "label": player,
            "toxicity": stats['max_score'],
            "size": size,
            "color": color,
            "history": stats['history']  # 将他的所有历史发言传给前端
        })
        G.add_node(player)

        real_feature = [stats['max_score']] + [0.0] * 15
        features_list.append(real_feature)

    # 构建溯源传播边
    frontend_edges = []
    if risk_source_player:
        for player in player_stats.keys():
            if player != risk_source_player:
                weight = player_stats[player]["max_score"]
                frontend_edges.append({
                    "source": risk_source_player,
                    "target": player,
                    "lineStyle": {"width": weight * 5 + 1, "curveness": 0.2}
                })

    x = torch.tensor(features_list, dtype=torch.float)
    edge_index = torch.zeros((2, 0), dtype=torch.long)

    # 🌟 注意：这里返回了 6 个变量！多了一个 timeline_data
    return G, x, edge_index, frontend_nodes, frontend_edges, timeline_data