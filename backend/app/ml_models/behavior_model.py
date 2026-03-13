# 文件路径: app/ml_models/behavior_model.py
import torch
import torch.nn as nn
import os


class LSTM_AE(nn.Module):
    def __init__(self, input_dim=3, hidden_dim=16):
        super(LSTM_AE, self).__init__()
        self.encoder = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.decoder = nn.LSTM(hidden_dim, input_dim, batch_first=True)

    def forward(self, x):
        _, (hidden, _) = self.encoder(x)
        hidden = hidden.permute(1, 0, 2).repeat(1, x.size(1), 1)
        reconstructed, _ = self.decoder(hidden)
        return reconstructed


class LSTMAutoencoder:
    def __init__(self, weight_path: str = None):
        print("正在初始化真实 LSTM 行为自编码器引擎...")
        self.model = LSTM_AE(input_dim=3, hidden_dim=16)

        if weight_path and os.path.exists(weight_path):
            self.model.load_state_dict(torch.load(weight_path, map_location=torch.device('cpu')))
            print(f">> 成功加载 LSTM 本地真实权重: {weight_path}")
        else:
            print(">> 未检测到本地 .pth 权重文件，当前使用随机初始化参数搭建计算图。")
            print(">> (请算法同学后续将权重放入 data/weights/lstm_model.pth)")

        self.model.eval()

    def predict(self, action_logs: list) -> float:
        if len(action_logs) < 2:
            return 0.1

        # 严谨的 Tensor 构造
        seq_data = [[log.get("gold", 0), log.get("kda", 0), log.get("move", 0)] for log in action_logs]
        tensor_data = torch.tensor([seq_data], dtype=torch.float32)

        with torch.no_grad():
            reconstructed_data = self.model(tensor_data)
            loss = nn.MSELoss()(reconstructed_data, tensor_data)

        error_score = min(float(loss.item()) / 100.0, 1.0)
        return error_score