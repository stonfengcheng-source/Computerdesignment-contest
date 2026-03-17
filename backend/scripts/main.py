import os
import pandas as pd
import torch
import networkx as nx
import matplotlib.pyplot as plt
from scripts.crawler import get_data
from scripts.model_gat import train_gat

# 修改后的 main.py 入口部分
from scripts.crawler import get_data
from scripts.processor import build_graph_data # 导入新补全的模块
from scripts.model_gat import train_gat
from scripts.visualize import save_visualizations # 导入新补全的模块

def main():
    # 1. 抓取/生成数据
    get_data()
    
    # 2. 处理数据构建图
    G, x, edge_index, nodes = build_graph_data('data/raw_chats.csv')
    
    # 3. 训练模型 (假设前几个节点是标记过的源头)
    y = torch.zeros(len(nodes), dtype=torch.long)
    y[:3] = 1 
    scores = train_gat(x, edge_index, y)
    
    # 4. 定位源头
    source_idx = torch.argmax(scores).item()
    source_player = nodes[source_idx]
    
    # 5. 调用可视化脚本
    save_visualizations(G, source_player)

if __name__ == "__main__":
    main()

    
# 设置支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False

def main():
    print(">>> 1. 正在获取DOTA2黑话数据...")
    get_data()

    print(">>> 2. 正在构建玩家传播链路图...")
    df = pd.read_csv('data/raw_chats.csv')
    G = nx.DiGraph()
    
    # 构建有向边 (回复关系)
    for _, row in df.iterrows():
        if pd.notna(row['target']):
            G.add_edge(row['user'], row['target'])

    # 准备GAT输入
    nodes = list(G.nodes())
    node_map = {node: i for i, node in enumerate(nodes)}
    edge_index = torch.tensor([[node_map[u], node_map[v]] for u, v in G.edges()]).t().contiguous()
    
    # 模拟节点特征 (128维)
    x = torch.randn((len(nodes), 128))
    # 模拟标签 (前3个玩家设定为初始源头)
    y = torch.zeros(len(nodes), dtype=torch.long)
    y[:3] = 1 

    print(">>> 3. GAT模型训练中，正在识别核心污染源...")
    scores = train_gat(x, edge_index, y)
    
    # 找到得分最高的节点
    source_idx = torch.argmax(scores).item()
    source_player = nodes[source_idx]

    print(f"\n[结果] 识别到核心污染源: {source_player}")

    print(">>> 4. 正在生成可视化溯源图谱...")
    os.makedirs('output', exist_ok=True)
    
    # 绘图
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=600, node_color='orange', font_size=8, arrowsize=15)
    plt.title(f"DOTA2黑话溯源图谱 - 核心源头: {source_player}")
    plt.savefig('output/graph_viz.png')
    
    # 导出GEXF
    nx.write_gexf(G, 'output/traceback_graph.gexf')
    
    with open('output/source_report.txt', 'w', encoding='utf-8') as f:
        f.write(f"溯源分析报告\n{'='*20}\n核心污染源: {source_player}\n传播节点数: {len(nodes)}\n传播边数: {len(G.edges())}")

    print(">>> 所有流程已完成！请查看 output 目录。")

if __name__ == "__main__":
    main()