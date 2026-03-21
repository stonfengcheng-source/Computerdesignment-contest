import os
import shutil
import json
import traceback
import asyncio
import uuid
import pandas as pd
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

# ================= 业务模块导入 =================
# 1. 数据库引擎与基础基类
from app.core.database import engine, Base, get_db

# 2. 数据库表模型 (必须在 create_all 之前导入)
from app.models.behavior_model import InconsistencyRecord

# 3. 核心 AI 分析服务
from app.services.video_analysis_service import process_video_for_inconsistency
from app.text_api import router as text_router
from app.services.credit_service import generate_cross_platform_credit
from app.services.report_service import generate_comprehensive_report

# 4. 黑话图谱与爬虫模块
from utils import gexf_to_echarts
from scripts.processor import build_graph_data
from scripts.model_gat import train_gat
# 注意：导入最新的纯异步爬虫入口
from scripts.crawler import trigger_crawling_async

# ================= 初始化配置与建表 =================
# 自动创建所有定义的数据库表
Base.metadata.create_all(bind=engine)

# 全局路径绝对定位
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="深蓝卫士 (全链路架构版)", description="基于多模态博弈大数据的网络游戏生态健康度监测平台")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= 路由 1: 文本语义挖掘模块 =================
app.include_router(text_router, prefix="/api/v1/text", tags=["文本与情感分析模块"])

# ================= 路由 2: DOTA2 黑话溯源模块 =================
slang_router = APIRouter(prefix="/api/slang", tags=["网络黑话与溯源模块"])


@slang_router.get("/dict")
def get_dict():
    path = os.path.join(DATA_DIR, "slang_dict.json")
    if not os.path.exists(path):
        raise HTTPException(404, "字典文件未找到，请先运行爬虫模块")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


@slang_router.get("/graph")
def get_graph():
    return gexf_to_echarts(os.path.join(OUTPUT_DIR, "traceback_graph.gexf"))


@slang_router.post("/analyze")
async def run_analysis():
    try:
        G, x, edge_index, nodes = build_graph_data(os.path.join(DATA_DIR, "raw_chats.csv"))
        import torch
        y = torch.zeros(len(nodes), dtype=torch.long)
        y[:2] = 1
        train_gat(x, edge_index, y)
        return {"status": "success", "message": "图神经网络训练与溯源完毕"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, f"GAT模块运行崩溃: {str(e)}")


app.include_router(slang_router)

# ================= 路由 3: 爬虫与数据标注模块 =================
crawl_router = APIRouter(prefix="/api/v1/data", tags=["数据爬取与标注"])
CRAWL_TASKS = {}  # 全局任务状态字典


async def run_crawler_task(task_id: str, platform: str):
    """后台执行的纯异步爬虫任务"""
    try:
        def progress_callback(progress: int, message: str, count: int):
            CRAWL_TASKS[task_id]["progress"] = progress
            CRAWL_TASKS[task_id]["message"] = message
            CRAWL_TASKS[task_id]["count"] = count

        # Await 异步执行，绝不卡死主线程
        final_count = await trigger_crawling_async(platform, progress_callback)

        CRAWL_TASKS[task_id]["status"] = "completed"
        CRAWL_TASKS[task_id]["progress"] = 100
        CRAWL_TASKS[task_id]["message"] = f"✅ 爬取完毕！共获取 {final_count} 条多模态语料"
    except Exception as e:
        CRAWL_TASKS[task_id]["status"] = "failed"
        CRAWL_TASKS[task_id]["message"] = f"❌ 引擎异常: {str(e)}"
        traceback.print_exc()


@crawl_router.post("/crawl")
async def start_spider(platform: str = Form("tieba")):
    """前端一键启动主动探索爬虫"""
    task_id = str(uuid.uuid4())
    CRAWL_TASKS[task_id] = {
        "status": "running",
        "progress": 0,
        "message": f"正在唤醒 {platform} 平台的节点探测器...",
        "count": 0
    }
    # 使用原生 asyncio 创建独立协程
    asyncio.create_task(run_crawler_task(task_id, platform))
    return {"status": "success", "task_id": task_id}


@crawl_router.get("/crawl/progress/{task_id}")
async def get_spider_progress(task_id: str):
    if task_id not in CRAWL_TASKS:
        raise HTTPException(status_code=404, detail="未找到该爬虫任务")
    return CRAWL_TASKS[task_id]


@crawl_router.get("/unlabeled")
async def get_unlabeled_data():
    """获取未标注的数据（目前从 CSV 读取，后续可改为从数据库读取）"""
    path = os.path.join(DATA_DIR, "raw_chats.csv")
    if not os.path.exists(path):
        return {"data": []}
    df = pd.read_csv(path)
    df = df.iloc[::-1]  # 倒序，把刚刚爬到的最新的数据排在前面
    return {"data": df.to_dict(orient="records")}


app.include_router(crawl_router)


# ================= 路由 4: 主控制台多模态输入口 (视频流聚合) =================
@app.post("/api/v1/analyze/video", tags=["多模态综合检测调度器"])
async def upload_and_analyze_video(
        player_id: str = Form(...),
        video_file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    try:
        file_path = os.path.join(UPLOAD_DIR, video_file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)

        text_prob, behavior_error, toxicity_score, is_inconsistent, risk_level = process_video_for_inconsistency(
            video_path=file_path,
            player_id=player_id
        )

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

        return {
            "status": "success",
            "message": f"多模态分析完毕，记录 {new_record.id} 已入库",
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
    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": f"多模态引擎运行异常: {str(e)}"}


@app.get("/api/v1/records", tags=["多模态综合检测调度器"])
async def get_all_records(db: Session = Depends(get_db)):
    records = db.query(InconsistencyRecord).all()
    return {"data": records}


# ================= 路由 5: 跨平台信用分与报告模块 =================
@app.get("/api/v1/credit/{player_id}", tags=["跨平台信用评级"])
async def get_player_credit(player_id: str):
    try:
        result = await generate_cross_platform_credit(player_id)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


class ReportRequest(BaseModel):
    player_id: str
    text_toxicity: float
    audio_toxicity: float
    behavior_anomaly: float
    graph_risk: float


@app.post("/api/v1/report/generate", tags=["多模态综合报告生成"])
async def generate_report(req: ReportRequest):
    try:
        result = generate_comprehensive_report(
            player_id=req.player_id,
            text_toxicity=req.text_toxicity,
            audio_toxicity=req.audio_toxicity,
            behavior_anomaly=req.behavior_anomaly,
            graph_risk=req.graph_risk
        )
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ================= 启动入口 =================
if __name__ == "__main__":
    import uvicorn

    print("🚀 深蓝卫士核心引擎启动中...")
    uvicorn.run(app, host="127.0.0.1", port=8000)