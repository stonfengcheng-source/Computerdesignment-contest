import pandas as pd
import networkx as nx
import torch
import os

def build_graph_data(csv_path):
    if not os.path.exists(csv_path):
        print(f"错误：找不到文件 {csv_path}")
        return None

    # 读取数据
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    # 1. 构建 NetworkX 有向图
    G = nx.DiGraph()
    
    # 2. 建立节点与边
    # 显式边：基于 target (回复关系)
    for _, row in df.iterrows():
        u, v = str(row['user']), str(row['target'])
        if v != 'nan': # 如果有明确的被回复者
            G.add_edge(u, v)
        else:
            G.add_node(u)

    # 3. 映射节点到索引 (用于 GAT 训练)
    nodes = list(G.nodes())
    node_map = {node: i for i, node in enumerate(nodes)}
    
    # 4. 生成 edge_index (PyTorch Geometric 格式)
    edge_list = []
    for u, v in G.edges():
        edge_list.append([node_map[u], node_map[v]])
    
    if not edge_list:
        # 兜底：如果没有边，建立自环防止 GAT 报错
        edge_index = torch.zeros((2, 0), dtype=torch.long)
    else:
        edge_index = torch.tensor(edge_list, dtype=torch.long).t().contiguous()

    # 5. 生成模拟特征 (128维)
    # 实际项目中这里可以使用 Word2Vec 向量
    x = torch.randn((len(nodes), 128))
    
    return G, x, edge_index, nodes

if __name__ == "__main__":
    # 测试代码
    res = build_graph_data('data/raw_chats.csv')
    if res:
        print(f"图构建完成，节点数: {len(res[0].nodes())}")