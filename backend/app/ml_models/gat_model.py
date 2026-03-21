import torch
import torch.nn.functional as F
from torch_geometric.nn import GATConv
from torch_geometric.data import Data

class SlangGAT(torch.nn.Module):
    def __init__(self, in_channels, out_channels):
        super(SlangGAT, self).__init__()
        self.conv1 = GATConv(in_channels, 16, heads=8, dropout=0.2)
        self.conv2 = GATConv(16 * 8, out_channels, heads=1, concat=False)

    def forward(self, x, edge_index):
        x = F.dropout(x, p=0.2, training=self.training)
        x = F.elu(self.conv1(x, edge_index))
        x = F.dropout(x, p=0.2, training=self.training)
        x = self.conv2(x, edge_index)
        return F.log_softmax(x, dim=1)

def train_gat(node_features, edge_index, labels, epochs=100):
    data = Data(x=node_features, edge_index=edge_index, y=labels)
    model = SlangGAT(in_channels=node_features.shape[1], out_channels=2)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)
    
    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        out = model(data.x, data.edge_index)
        loss = F.nll_loss(out, data.y)
        loss.backward()
        optimizer.step()
    
    # 返回预测概率，概率最高的节点即为潜在污染源
    model.eval()
    with torch.no_grad():
        out = model(data.x, data.edge_index)
        # 这里的得分反映了节点的传播影响力
        scores = torch.exp(out[:, 1]) 
    return scores