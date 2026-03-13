from sqlalchemy import Column, Integer, String, Boolean, Float
from app.core.database import Base


class InconsistencyRecord(Base):
    __tablename__ = "inconsistency_records"

    id = Column(Integer, primary_key=True, index=True)
    video_filename = Column(String, index=True)  # 关联上传的视频文件名
    player_id = Column(String)

    # 算法输出记录
    text_prob = Column(Float)
    behavior_error = Column(Float)
    toxicity_score = Column(Float)

    # 最终判定
    is_inconsistent = Column(Boolean, default=False)
    risk_level = Column(String)