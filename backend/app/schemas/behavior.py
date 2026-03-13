# 文件路径: app/schemas/behavior.py
from pydantic import BaseModel
from typing import List, Optional

class TimeSeriesFeature(BaseModel):
    timestamp: float
    gold_change_rate: float      # 金币变化率
    kda_change_rate: float       # KDA变化率
    moving_distance: float       # 移动距离

class BehaviorStream(BaseModel):
    player_id: str
    match_id: str
    text_logs: List[str]         # 聊天记录，供 RoBERTa 处理
    audio_file_url: Optional[str] = None
    action_logs: List[TimeSeriesFeature] # 供 LSTM Autoencoder 分析的时序行为特征