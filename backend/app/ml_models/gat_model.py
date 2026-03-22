# 文件路径: backend/app/ml_models/gat_model.py

import os
import torch
import torch.nn.functional as F
from torch_geometric.nn import GATConv
from torch_geometric.data import Data
import networkx as nx


class SlangGAT(torch.nn.Module):
    def __init__(self, in_channels, out_channels):
        super(SlangGAT, self).__init__()
        # 使用多头注意力机制捕捉不同维度的传播特征
        self.conv1 = GATConv(in_channels, 16, heads=8, dropout=0.2)
        self.conv2 = GATConv(16 * 8, out_channels, heads=1, concat=False)

    def forward(self, x, edge_index):
        x = F.dropout(x, p=0.2, training=self.training)
        x = F.elu(self.conv1(x, edge_index))
        x = F.dropout(x, p=0.2, training=self.training)
        x = self.conv2(x, edge_index)
        return F.log_softmax(x, dim=1)


# ==========================================
# 模块 1：离线训练与保存 (仅在需要更新模型时运行)
# ==========================================
def train_and_save_gat(node_features, edge_index, labels, train_mask=None, epochs=100, save_path="gat_weights.pt"):
    """
    带掩码的半监督图节点分类训练
    """
    # 如果没有提供掩码，默认使用 80% 的数据进行训练，防止数据泄露
    if train_mask is None:
        num_nodes = node_features.shape[0]
        train_mask = torch.rand(num_nodes) < 0.8

    data = Data(x=node_features, edge_index=edge_index, y=labels, train_mask=train_mask)
    model = SlangGAT(in_channels=node_features.shape[1], out_channels=2)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)

    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        out = model(data.x, data.edge_index)
        # 核心修正：只对训练集节点计算 Loss，防止模型死记硬背
        loss = F.nll_loss(out[data.train_mask], data.y[data.train_mask])
        loss.backward()
        optimizer.step()

    # 确保持久化保存模型
    os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
    torch.save(model.state_dict(), save_path)
    print(f"GAT 模型已成功训练并保存至: {save_path}")


# ==========================================
# 模块 2：线上真实溯源服务 (供后端 API 实时调用)
# ==========================================
def trace_pollution_source(node_features, edge_index, num_nodes, model_path="gat_weights.pt"):
    """
    结合 GAT 风险评估与 PageRank 拓扑分析的复合溯源算法
    """
    # 1. 初始化模型并尝试加载权重
    in_channels = node_features.shape[1] if node_features.ndim > 1 else 1
    model = SlangGAT(in_channels=in_channels, out_channels=2)

    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path))
    else:
        print("警告: 未找到 GAT 预训练权重，将使用随机初始化特征进行演示。建议先运行训练模块。")

    model.eval()

    # 2. GNN 空间：计算每个节点的违规（被污染）概率
    with torch.no_grad():
        out = model(node_features, edge_index)
        # 取类别 1 (违规/阴阳怪气) 的预测概率
        risk_scores = torch.exp(out[:, 1]).numpy()

        # 3. 拓扑空间：使用 NetworkX 构建有向图并计算向心性 (PageRank)
    # 边关系代表互动方向 (例如：A 回复 B，说明 A 受到 B 的影响，B 的传播力更强)
    edges = edge_index.t().tolist()
    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from(range(num_nodes))
    nx_graph.add_edges_from(edges)

    try:
        # 计算 PageRank，衡量节点在图结构中的传播枢纽地位
        centrality_scores = nx.pagerank(nx_graph, alpha=0.85)
    except Exception:
        # 图太小或无法收敛时的兜底
        centrality_scores = {i: 1.0 / num_nodes for i in range(num_nodes)}

    # 4. 融合计算：最终溯源得分 = 自身违规概率 × 网络传播枢纽度
    final_source_scores = []
    for i in range(num_nodes):
        # 归一化处理（避免某些孤立节点引发异常）
        c_score = centrality_scores.get(i, 0)
        r_score = risk_scores[i]

        # 乘积作为最终溯源得分
        tracing_score = float(r_score * c_score)
        final_source_scores.append(tracing_score)

    # 将结果转换为张量并返回，数值越大的节点，越是整个对局/聊天室内的“罪魁祸首”
    return torch.tensor(final_source_scores)