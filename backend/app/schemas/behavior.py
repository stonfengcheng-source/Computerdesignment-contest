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


# 3. 信用报告存储表 (新增：将生成的评级报告持久化入库)
class CreditReportRecord(Base):
    __tablename__ = "credit_report_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    player_id = Column(String(100), index=True)

    # 四大维度的风险得分
    text_toxicity = Column(Float)
    audio_toxicity = Column(Float)
    behavior_anomaly = Column(Float)
    graph_risk = Column(Float)

    # 最终计算出的信用分与判决书
    final_credit_score = Column(Float)
    summary = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())