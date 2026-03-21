import os
import sys
import json
import uuid
import shutil
import asyncio
import traceback
from typing import List

# ================= 修复 Windows 下 Playwright 的 NotImplementedError =================
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, APIRouter, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel

# ================= 业务模块导入 (路径已重构) =================

# 1. 核心层：数据库配置
from app.core.database import engine, Base, get_db, SessionLocal

# 2. 模型层：数据库表模型
from app.models.behavior_model import InconsistencyRecord, CrawledDataRecord, CreditReportRecord

# 3. 服务层：核心 AI 业务逻辑
from app.services.video_analysis_service import process_video_for_inconsistency
from app.services.credit_service import generate_cross_platform_credit
from app.services.report_service import generate_comprehensive_report
from app.services.graph_processor import build_graph_data
from app.services.crawler_service import GameEcologyCrawler

# 4. 表现层/API 路由
from app.text_api import router as text_router

# 5. 模型层：机器学习/图算法模型
from app.ml_models.gat_model import train_gat

# 6. 工具类
from utils import gexf_to_echarts

# ================= 初始化配置与建表 =================
# 自动创建所有定义的数据库表
Base.metadata.create_all(bind=engine)

# 👇 💡 核心修复 1：数据库补丁，自动修复 report_path 缺失问题
try:
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE credit_report_records ADD COLUMN report_path VARCHAR(255)"))
        print("✅ 数据库补丁：已自动为 credit_report_records 表补充 report_path 字段！")
except Exception:
    pass  # 如果列已经存在，会直接跳过，不会报错
# 👆 核心修复 1 结束

# 全局路径绝对定位
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")

for directory in [OUTPUT_DIR, DATA_DIR, UPLOAD_DIR, REPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)

app = FastAPI(title="深蓝卫士 (全链路架构版)", description="基于多模态博弈大数据的网络游戏生态健康度监测平台")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================= 💡 核心修复 2：将后台任务改为同步函数，交由 FastAPI 线程池运行 =================
def update_risk_topology_task():
    """在后台重新构建社交图谱并进行风险溯源分析 (避免卡死主线程)"""
    try:
        csv_path = os.path.join(DATA_DIR, "raw_chats.csv")
        if not os.path.exists(csv_path):
            print("⚠️ 拓扑动态更新跳过: raw_chats.csv 不存在")
            return

        # 重新构建图数据
        G, x, edge_index, nodes = build_graph_data(csv_path)
        # 触发GAT热训练以更新风险权重
        import torch
        y = torch.zeros(len(nodes), dtype=torch.long)
        if len(y) >= 2:
            y[:2] = 1  # 简单模拟源头节点标签
        train_gat(x, edge_index, y)
        print(f"🔄 风险拓扑已在后台动态更新完成，当前网络节点数: {len(nodes)}")
    except Exception as e:
        print(f"⚠️ 拓扑动态更新失败: {str(e)}")


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
def run_analysis():
    # 💡 修复：去掉了 async，让 CPU 密集型任务在线程池运行
    try:
        update_risk_topology_task()
        return {"status": "success", "message": "图神经网络训练与溯源完毕"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, f"GAT模块运行崩溃: {str(e)}")


app.include_router(slang_router)

# ================= 路由 3: 爬虫与数据标注模块 =================
crawl_router = APIRouter(prefix="/api/v1/data", tags=["数据爬取与标注"])
CRAWL_TASKS = {}


async def run_crawler_task(task_id: str, platform: str):
    db = SessionLocal()
    try:
        def progress_callback(progress: int, message: str, count: int):
            CRAWL_TASKS[task_id]["progress"] = progress
            CRAWL_TASKS[task_id]["message"] = message
            CRAWL_TASKS[task_id]["count"] = count

        crawler = GameEcologyCrawler(platform=platform, progress_cb=progress_callback)
        final_count = await crawler.run()

        for item in crawler.results:
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
        db.commit()

        CRAWL_TASKS[task_id]["status"] = "completed"
        CRAWL_TASKS[task_id]["progress"] = 100
        CRAWL_TASKS[task_id]["message"] = f"✅ 爬取完毕！共获取 {final_count} 条多模态语料并入库"
    except Exception as e:
        db.rollback()
        CRAWL_TASKS[task_id]["status"] = "failed"
        CRAWL_TASKS[task_id]["message"] = f"❌ 引擎异常: {str(e)}"
        traceback.print_exc()
    finally:
        db.close()


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
def get_spider_progress(task_id: str):
    if task_id not in CRAWL_TASKS:
        raise HTTPException(status_code=404, detail="未找到该爬虫任务")
    return CRAWL_TASKS[task_id]


@crawl_router.get("/unlabeled")
def get_unlabeled_data(db: Session = Depends(get_db)):
    # 💡 修复：去掉了 async，防止数据库查询阻塞事件循环
    records = db.query(CrawledDataRecord).order_by(CrawledDataRecord.id.desc()).all()
    result = [{
        "id": r.id,
        "text": r.content,
        "source": r.platform,
        "time": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "未知",
        "annotated": r.is_annotated,
        "pre_matched": r.pre_matched
    } for r in records]
    return {"data": result}


class AnnotationSubmit(BaseModel):
    isSarcastic: str
    hasSlang: List[str]
    isRegionalDiscrimination: bool
    sentiment: str


@crawl_router.post("/annotate/{record_id}")
def submit_annotation(record_id: int, data: AnnotationSubmit, db: Session = Depends(get_db)):
    # 💡 修复：去掉了 async
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
def upload_and_analyze_video(  # 💡 核心修复 3：去掉了 async！让沉重的视频处理进入线程池
        player_id: str = Form(...),
        video_file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    try:
        file_path = os.path.join(UPLOAD_DIR, video_file.filename)
        # 阻塞的磁盘 I/O 操作
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)

        # 阻塞的 CPU 密集型操作 (OpenCV 分析)
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
def get_all_records(db: Session = Depends(get_db)):  # 💡 修复：去掉 async
    records = db.query(InconsistencyRecord).all()
    return {"data": records}


# ================= 路由 5: 跨平台信用分与报告模块 (重构版) =================
@app.get("/api/v1/credit/{player_id}", tags=["跨平台信用评级"])
async def get_player_credit(player_id: str, db: Session = Depends(get_db)):
    try:
        # 这里有 await，所以保留 async def
        result = await generate_cross_platform_credit(player_id, db)
        return {"status": "success", "data": result}
    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


class ReportRequest(BaseModel):
    player_id: str
    text_toxicity: float
    audio_toxicity: float
    behavior_anomaly: float
    graph_risk: float


@app.post("/api/v1/report/generate", tags=["多模态综合报告生成"])
def generate_report(req: ReportRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # 💡 核心修复 4：使用 BackgroundTasks 执行图谱更新，去掉了 async
    try:
        # 1. 调用原有的服务层逻辑生成诊断文本
        result = generate_comprehensive_report(
            player_id=req.player_id,
            text_toxicity=req.text_toxicity,
            audio_toxicity=req.audio_toxicity,
            behavior_anomaly=req.behavior_anomaly,
            graph_risk=req.graph_risk
        )

        # 2. 计算最终的综合信用分
        penalty = (req.text_toxicity * 15) + (req.behavior_anomaly * 25) + (req.graph_risk * 20)
        final_score = max(0, min(100, int(100 - penalty)))
        summary_text = result.get("summary", "系统检测到玩家行为异常") if isinstance(result, dict) else str(result)

        # 3. 物理存储
        report_id_str = uuid.uuid4().hex[:8]
        report_filename = f"Report_{req.player_id}_{report_id_str}.txt"
        file_path = os.path.join(REPORTS_DIR, report_filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"=========== 深蓝卫士 - 玩家信用诊断报告 ===========\n")
            f.write(f"报告单号: {report_id_str}\n玩家 ID: {req.player_id}\n")
            f.write(f"综合信用分: {final_score}\n评级结论: {summary_text}\n\n")
            f.write(f"[多模态异常指标拆解]\n")
            f.write(f"文本毒性: {req.text_toxicity}\n语音情绪违规: {req.audio_toxicity}\n")
            f.write(f"行为异常(如挂机/送人头): {req.behavior_anomaly}\n社交网络感染风险: {req.graph_risk}\n")
            f.write(f"===================================================\n")

        # 4. 存入数据库
        new_report = CreditReportRecord(
            player_id=req.player_id,
            text_toxicity=req.text_toxicity,
            audio_toxicity=req.audio_toxicity,
            behavior_anomaly=req.behavior_anomaly,
            graph_risk=req.graph_risk,
            final_credit_score=final_score,
            summary=summary_text,
            report_path=file_path
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        # 5. 💡 使用 FastAPI 原生的后台任务机制处理耗时的图网络重构
        background_tasks.add_task(update_risk_topology_task)

        return {
            "status": "success",
            "message": "信用报告已生成，拓扑热更新已在后台运行",
            "record_id": new_report.id
        }
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        return {"status": "error", "message": str(e)}


@app.get("/api/v1/report/download/{report_id}", tags=["多模态综合报告下载"])
def download_report_file(report_id: int, db: Session = Depends(get_db)):  # 💡 修复：去掉 async
    record = db.query(CreditReportRecord).filter(CreditReportRecord.id == report_id).first()

    if not record or not record.report_path or not os.path.exists(record.report_path):
        raise HTTPException(status_code=404, detail="报告文件不存在或已被删除")

    return FileResponse(
        path=record.report_path,
        filename=f"Credit_Report_{record.player_id}.txt",
        media_type='text/plain'
    )


@app.get("/api/v1/report/download_latest/{player_id}", tags=["多模态综合报告下载"])
def download_latest_report(player_id: str, db: Session = Depends(get_db)):  # 💡 修复：去掉 async
    record = db.query(CreditReportRecord).filter(CreditReportRecord.player_id == player_id).order_by(
        CreditReportRecord.id.desc()).first()

    if not record or not record.report_path or not os.path.exists(record.report_path):
        raise HTTPException(status_code=404, detail="该玩家尚无信用报告或文件已丢失")

    return FileResponse(
        path=record.report_path,
        filename=f"Credit_Report_{player_id}.txt",
        media_type='text/plain'
    )


# ================= 启动入口 =================
if __name__ == "__main__":
    import uvicorn

    print("🚀 深蓝卫士核心引擎启动中...")
    uvicorn.run(app, host="127.0.0.1", port=8000, loop="none")