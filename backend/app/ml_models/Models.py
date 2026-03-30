from transformers import BertModel
# from chinesebert import ChineseBertForMaskedLM, ChineseBertTokenizerFast, ChineseBertConfig
from .BERT import BertModel
import torch
import torch.nn as nn
from torch.autograd import Variable
import numpy as np

# 2022.4.28 Glove + LSTM
class BiLSTM(nn.Module):
    def __init__(self, config, embedding_weight):
        super(BiLSTM, self).__init__()
        self.device = config.device
        self.vocab_size = embedding_weight.shape[0]
        self.embed_dim = embedding_weight.shape[1]
        # Embedding Layer
        embedding_weight = torch.from_numpy(embedding_weight).float()        
        embedding_weight = Variable(embedding_weight, requires_grad=config.if_grad)
        self.embedding = nn.Embedding(self.vocab_size, self.embed_dim, _weight=embedding_weight)
        # Encoder layer
        self.bi_lstm = nn.LSTM(self.embed_dim, config.lstm_hidden_dim, bidirectional=True, batch_first=True) 

    def forward(self, **kwargs):
        emb = self.embedding(kwargs["title_text_token_ids"].to(self.device)) # [batch, len] --> [batch, len, embed_dim]
        lstm_out, _ = self.bi_lstm(emb)  # [batch, len, embed_dim] --> [batch, len, lstm_hidden_dim*2]
        lstm_out_pool = torch.mean(lstm_out, dim=1)  # [batch, lstm_hidden_dim*2]
        return lstm_out, lstm_out_pool
    

class Bert_Layer(torch.nn.Module):
    def __init__(self, config):
        super(Bert_Layer, self).__init__()
        
        # 1. 挂载设备 (解决 to(self.device) 报错)
        self.device = config.device
        
        # 2. 从本地文件夹加载我们下载好的 RoBERTa 模型权重
        self.bert_layer = BertModel.from_pretrained('./pretrained_model')
        
        # 3. 记录隐藏层维度
        self.dim = config.vocab_dim

    def forward(self, **kwargs):
        # 保留原作者魔改的带有 toxic_ids 的前向传播逻辑
        bert_output = self.bert_layer(input_ids=kwargs['text_idx'].to(self.device),
                                 token_type_ids=kwargs['text_ids'].to(self.device),
                                 attention_mask=kwargs['text_mask'].to(self.device),
                                 toxic_ids=kwargs["toxic_ids"].to(self.device))
        return bert_output[0], bert_output[1]


class TwoLayerFFNNLayer(torch.nn.Module):
    '''
    2-layer FFNN with specified nonlinear function
    must be followed with some kind of prediction layer for actual prediction
    '''
    def __init__(self, config):
        super(TwoLayerFFNNLayer, self).__init__()
        self.output = config.dropout
        self.input_dim = config.vocab_dim
        self.hidden_dim = config.fc_hidden_dim
        self.out_dim = config.num_classes
        self.dropout = nn.Dropout(config.dropout)
        self.model = nn.Sequential(nn.Linear(self.input_dim, self.hidden_dim),
                                   nn.Tanh(),
                                   nn.Linear(self.hidden_dim, self.out_dim))

    def forward(self, att_input, pooled_emb):
        att_input = self.dropout(att_input)
        pooled_emb = self.dropout(pooled_emb)
        return self.model(pooled_emb)
    
class MultiTaskModel(nn.Module):
    def __init__(self, config):
        super(MultiTaskModel, self).__init__()
        self.device = config.device
        self.bert = Bert_Layer(config)
        
        # 1. 任务：基本毒性 (toxic: 0, 1 -> 2类)
        self.toxic_classifier = nn.Sequential(
            nn.Dropout(config.dropout), nn.Linear(config.vocab_dim, 2)
        )
        # 2. 任务：游戏黑话 (jargon: 0, 1 -> 2类)
        self.jargon_classifier = nn.Sequential(
            nn.Dropout(config.dropout), nn.Linear(config.vocab_dim, 2)
        )
        
        # 3. 任务：毒性细分 (toxic_type -> 3类：0无毒, 1一般冒犯, 2仇恨)
        self.type_classifier = nn.Sequential(
            nn.Dropout(config.dropout), nn.Linear(config.vocab_dim, 3)
        )
        # 4. 任务：识别手段 (expression -> 4类：0无恨, 1显性, 2隐性, 3举报)
        self.expression_classifier = nn.Sequential(
            nn.Dropout(config.dropout), nn.Linear(config.vocab_dim, 4)
        )
        # 5. 任务：群体标签 (target -> 多选 6 类：LGBTQ, 地区, 性别, 种族, 其他, 无恨)
        self.target_classifier = nn.Sequential(
            nn.Dropout(config.dropout), nn.Linear(config.vocab_dim, 6)
        )

    def forward(self, **kwargs):
        seq_out, pooled_out = self.bert(**kwargs)
        
        out_toxic = self.toxic_classifier(pooled_out)
        out_jargon = self.jargon_classifier(pooled_out)
        out_type = self.type_classifier(pooled_out)
        out_expr = self.expression_classifier(pooled_out)
        out_target = self.target_classifier(pooled_out)
        
        return out_toxic, out_jargon, out_type, out_expr, out_target