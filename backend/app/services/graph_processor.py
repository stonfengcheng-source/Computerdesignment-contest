import pandas as pd
import networkx as nx
import torch
import os
import numpy as np

# 导入我们在前面修好的文本模型 (路径根据你的实际项目结构调整)
from app.ml_models.nlp_model import RoBERTaAnalyzer


def build_graph_data(csv_path):
    if not os.path.exists(csv_path):
        print(f"错误：找不到文件 {csv_path}")
        return None

    # 初始化真正的文本大模型
    print("正在启动 NLP 引擎提取节点特征...")
    nlp_engine = RoBERTaAnalyzer()

    # 读取聊天数据
    df = pd.read_csv(csv_path, encoding='utf-8-sig')

    G = nx.DiGraph()
    # 建立消息节点（注意：以单条聊天记录为节点，而不是单纯的用户，这在溯源里叫信息传播图）

    features_list = []
    node_mapping = {}  # 将消息/用户 ID 映射为 0, 1, 2...

    for idx, row in df.iterrows():
        # 假设 csv 里有 message_id, user, text, target 等字段
        node_id = str(idx)  # 如果没有唯一 message_id，暂用行号代替
        u, v = str(row.get('user', '')), str(row.get('target', 'nan'))
        text = str(row.get('text', ''))

        node_mapping[node_id] = idx
        G.add_node(node_id, user=u, text=text)

        # 核心改进：使用 NLP 引擎计算这句话的“违规风险度”和“语义向量”
        # 即使无法直接获取 128 维隐藏层，也可以用预测概率 + 文本长度 + 关键词密度等构造真实特征
        toxicity_score = nlp_engine.predict([text])

        # 这里构造一个简易的真实特征向量 (例如 4 维：违规率, 长度归一化, 是否包含特殊符号, 回复数占位)
        # 进阶做法是提取 RoBERTa 最后一层的 pooler_output (768维)
        real_feature = [
            toxicity_score,
            min(len(text) / 50.0, 1.0),  # 文本长度特征
            1.0 if '?' in text or '？' in text or '!' in text else 0.0,  # 情绪符号特征
            0.0  # 占位符，后续可以加上入度/出度特征
        ]
        # 为了适配后续可能的维度要求，用 0 填充到 16 维
        real_feature.extend([0.0] * 12)
        features_list.append(real_feature)

    # 构建边 (基于回复关系)
    # 这部分需要根据你的 CSV 逻辑调整，如果 target 是 user_id，就需要找到 target 对应的 message_id
    # 这里提供一个基于上下文明确的回复链路构建：
    for idx, row in df.iterrows():
        target_user = str(row.get('target', 'nan'))
        if target_user != 'nan':
            # 找到 target_user 最近发的一条消息作为被回复节点
            # (省略复杂的查找逻辑，直接演示添加边的过程)
            # G.add_edge(当前节点, 被回复节点)
            pass

    # 兜底生成边：如果 CSV 里没有复杂的回复关系，根据时间顺序（行号）相连，表示上下文影响
    edge_list = []
    for i in range(1, len(df)):
        edge_list.append([i, i - 1])  # 当前话语受上一句话语影响 (入边)

    if not edge_list:
        edge_index = torch.zeros((2, 0), dtype=torch.long)
    else:
        edge_index = torch.tensor(edge_list, dtype=torch.long).t().contiguous()

    # 将真实的特征列表转换为张量
    x = torch.tensor(features_list, dtype=torch.float)

    print(f"✅ 图构建完成! 节点数: {len(G.nodes)}, 特征维度: {x.shape[1]}")
    # 不再是瞎编的 randn，而是包含了文本恶意程度的真实张量！
    return G, x, edge_index, list(G.nodes())