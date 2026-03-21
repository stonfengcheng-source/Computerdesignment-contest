from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.sql import func
from app.core.database import Base


# 1. 行为不一致检测记录表
class InconsistencyRecord(Base):
    __tablename__ = "inconsistency_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    video_filename = Column(String(255))
    player_id = Column(String(100), index=True)
    text_prob = Column(Float)
    behavior_error = Column(Float)
    toxicity_score = Column(Float)
    is_inconsistent = Column(Boolean)
    risk_level = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# 2. 爬虫语料存储表
class CrawledDataRecord(Base):
    __tablename__ = "crawled_data_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    platform = Column(String(50), index=True)
    user_id = Column(String(100))
    content = Column(Text)
    pre_matched = Column(String(200))
    is_annotated = Column(Boolean, default=False)

    is_sarcastic = Column(String(10), nullable=True)
    has_slang = Column(Text, nullable=True)
    is_regional = Column(Boolean, default=False)
    sentiment = Column(String(20), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# 3. 💡 新增：信用报告存储表 (用于存储生成的评级报告)
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