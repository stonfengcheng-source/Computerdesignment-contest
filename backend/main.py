import os
import shutil
from fastapi import FastAPI, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core.database import engine, Base, get_db
from app.models.behavior_model import InconsistencyRecord
from app.services.video_analysis_service import process_video_for_inconsistency

# 初始化数据库
Base.metadata.create_all(bind=engine)

app = FastAPI(title="深蓝卫士 (校赛展示版)", description="视频分治处理：言行不一检测模块")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/v1/analyze/video")
async def upload_and_analyze_video(
        player_id: str = Form(...),
        video_file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    # 1. 确保上传目录存在
    upload_dir = os.path.join(os.getcwd(), "data", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # 2. 保存视频文件到本地 data/uploads 文件夹
    file_path = os.path.join(upload_dir, video_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(video_file.file, buffer)

    # 3. 将保存好的视频路径交给“言行不一”服务去分治处理
    text_prob, behavior_error, toxicity_score, is_inconsistent, risk_level = process_video_for_inconsistency(
        video_path=file_path,
        player_id=player_id
    )

    # 4. 结算结果存入本地 SQLite
    new_record = InconsistencyRecord(
        video_filename=video_file.filename,
        player_id=player_id,
        text_prob=text_prob,
        behavior_error=behavior_error,
        toxicity_score=toxicity_score,
        is_inconsistent=is_inconsistent,
        risk_level=risk_level
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    # 5. 返回校赛演示需要的数据格式
    return {
        "status": "success",
        "message": f"视频 {video_file.filename} 分析完成",
        "result": {
            "is_inconsistent": is_inconsistent,
            "risk_level": risk_level,
            "details": {
                "text_sentiment_prob": text_prob,
                "behavior_anomaly_score": behavior_error,
                "final_toxicity_score": toxicity_score
            }
        }
    }


@app.get("/api/v1/records")
async def get_all_records(db: Session = Depends(get_db)):
    records = db.query(InconsistencyRecord).all()
    return {"data": records}