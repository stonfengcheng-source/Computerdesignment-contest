import os
import shutil
import json
import os
import shutil
import json
import traceback
import asyncio
import uuid
from typing import List

from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

# ================= 业务模块导入 (路径已重构) =================

# 1. 核心层：数据库配置
# 确保 database.py 里的路径是绝对路径，防止搬家后找不到 db 文件
from app.core.database import engine, Base, get_db, SessionLocal

# 2. 模型层：数据库表模型
from app.models.behavior_model import InconsistencyRecord, CrawledDataRecord

# 3. 服务层：核心 AI 业务逻辑
from app.services.video_analysis_service import process_video_for_inconsistency
from app.services.credit_service import generate_cross_platform_credit
from app.services.report_service import generate_comprehensive_report
# 导入重构后的图谱处理服务
from app.services.graph_processor import build_graph_data
# 导入重构后的自动化浏览器爬虫服务
from app.services.crawler_service import GameEcologyCrawler, trigger_crawling_async

# 4. 表现层/API 路由
from app.text_api import router as text_router

# 5. 模型层：机器学习/图算法模型
from app.ml_models.gat_model import train_gat

# 6. 工具类
from utils import gexf_to_echarts

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
CRAWL_TASKS = {}


async def run_crawler_task(task_id: str, platform: str):
    """后台执行的纯异步爬虫任务，并将结果持久化到数据库"""
    db = SessionLocal()  # 在异步后台任务中手动创建 session
    try:
        def progress_callback(progress: int, message: str, count: int):
            CRAWL_TASKS[task_id]["progress"] = progress
            CRAWL_TASKS[task_id]["message"] = message
            CRAWL_TASKS[task_id]["count"] = count

        # 实例化爬虫
        crawler = GameEcologyCrawler(platform=platform, progress_cb=progress_callback)
        final_count = await crawler.run()

        # --- 核心修改：将抓取到的 item 存入数据库 ---
        for item in crawler.results:
            # 检查数据库中是否已存在该条内容，避免重复抓取存入
            exists = db.query(CrawledDataRecord).filter(CrawledDataRecord.content == item["text"]).first()
            if not exists:
                new_record = CrawledDataRecord(
                    platform=item["source"],
                    user_id=item["user"],
                    content=item["text"],
                    pre_matched=item["pre_matched"],
                    is_annotated=False
                )
                db.add(new_record)

        db.commit()  # 统一提交

        CRAWL_TASKS[task_id]["status"] = "completed"
        CRAWL_TASKS[task_id]["progress"] = 100
        CRAWL_TASKS[task_id]["message"] = f"✅ 爬取完毕！共获取 {final_count} 条多模态语料并入库"
    except Exception as e:
        db.rollback()
        CRAWL_TASKS[task_id]["status"] = "failed"
        CRAWL_TASKS[task_id]["message"] = f"❌ 引擎异常: {str(e)}"
        traceback.print_exc()
    finally:
        db.close()  # 必须关闭会话


@crawl_router.post("/crawl")
async def start_spider(platform: str = Form("tieba")):
    task_id = str(uuid.uuid4())
    CRAWL_TASKS[task_id] = {
        "status": "running",
        "progress": 0,
        "message": f"正在唤醒 {platform} 平台的节点探测器...",
        "count": 0
    }
    asyncio.create_task(run_crawler_task(task_id, platform))
    return {"status": "success", "task_id": task_id}


@crawl_router.get("/crawl/progress/{task_id}")
async def get_spider_progress(task_id: str):
    if task_id not in CRAWL_TASKS:
        raise HTTPException(status_code=404, detail="未找到该爬虫任务")
    return CRAWL_TASKS[task_id]


@crawl_router.get("/unlabeled")
async def get_unlabeled_data(db: Session = Depends(get_db)):
    """核心修改：从数据库读取并转换为前端能识别的 text 和 source 字段"""
    records = db.query(CrawledDataRecord).order_by(CrawledDataRecord.id.desc()).all()
    result = []
    for r in records:
        result.append({
            "id": r.id,
            "text": r.content,  # 映射 content 到 text
            "source": r.platform,  # 映射 platform 到 source
            "time": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "未知",
            "annotated": r.is_annotated,
            "pre_matched": r.pre_matched
        })
    return {"data": result}


# --- 新增：标注保存接口 ---
class AnnotationSubmit(BaseModel):
    isSarcastic: str
    hasSlang: List[str]
    isRegionalDiscrimination: bool
    sentiment: str


@crawl_router.post("/annotate/{record_id}")
async def submit_annotation(record_id: int, data: AnnotationSubmit, db: Session = Depends(get_db)):
    record = db.query(CrawledDataRecord).filter(CrawledDataRecord.id == record_id).first()
    if not record:
        raise HTTPException(404, "记录不存在")

    record.is_sarcastic = data.isSarcastic
    record.has_slang = ",".join(data.hasSlang)
    record.is_regional = data.isRegionalDiscrimination
    record.sentiment = data.sentiment
    record.is_annotated = True

    db.commit()
    return {"status": "success"}


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