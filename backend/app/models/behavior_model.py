from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.sql import func
from app.core.database import Base


# 1. 行为不一致检测记录表 (已修复 float 报错)
class InconsistencyRecord(Base):
    __tablename__ = "inconsistency_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    video_filename = Column(String(255))
    player_id = Column(String(100), index=True)
    # 核心修复：将 float 改为 Float
    text_prob = Column(Float)
    behavior_error = Column(Float)
    toxicity_score = Column(Float)
    is_inconsistent = Column(Boolean)
    risk_level = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# 2. 爬虫语料存储表 (新增：爬取到的数据存储在这里)
class CrawledDataRecord(Base):
    __tablename__ = "crawled_data_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    platform = Column(String(50), index=True)
    user_id = Column(String(100))
    content = Column(Text)  # 语料内容
    pre_matched = Column(String(200))  # 自动匹配到的标签 (slang/sarcasm等)
    is_annotated = Column(Boolean, default=False)  # 是否已人工标注

    # 标注后的字段 (由前端提交)
    is_sarcastic = Column(String(10), nullable=True)
    has_slang = Column(Text, nullable=True)
    is_regional = Column(Boolean, default=False)
    sentiment = Column(String(20), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())