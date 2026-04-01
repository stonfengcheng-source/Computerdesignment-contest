import os
import sys
import json
import uuid
import shutil
import asyncio
import traceback
from typing import List, Optional
from app.ml_models.nlp_model import RoBERTaAnalyzer
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
import random

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
# 导入改名后的训练函数
from app.ml_models.gat_model import train_and_save_gat

# 6. 工具类
from utils import gexf_to_echarts

# ================= 新增：风险溯源记录表模型 =================
class TraceRecord(Base):
    __tablename__ = "trace_records"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String(50), index=True)
    source_player = Column(String(50))
    affected_count = Column(Integer)
    risk_level = Column(String(50))
    risk_class = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)

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
def update_risk_topology_task(match_id: str = "system"):
    """在后台构建对局专属社交图谱并进行风险溯源分析"""
    try:
        csv_path = os.path.join(DATA_DIR, "raw_chats.csv")
        if not os.path.exists(csv_path):
            print(f"⚠️ 拓扑更新跳过: raw_chats.csv 不存在")
            return

        # 1. 重新构建图数据 (此时 G 还在内存中)
        G, x, edge_index, nodes = build_graph_data(csv_path)

        # 💡💡💡 核心大修复：将内存中的网络图 G，写入物理硬盘变为 .gexf 文件！
        import networkx as nx
        default_path = os.path.join(OUTPUT_DIR, "traceback_graph.gexf")
        nx.write_gexf(G, default_path)  # <--- 就是少了这一行！

        # 2. 训练并保存 GAT 模型权重
        import torch
        y = torch.zeros(len(nodes), dtype=torch.long)
        if len(y) >= 2:
            y[:2] = 1

        train_and_save_gat(x, edge_index, y, save_path=os.path.join(DATA_DIR, "weights", "gat_weights.pt"))

        # 3. 专属图谱复制：把刚才成功写入硬盘的图，复制一份并加上对局ID
        if match_id != "system" and os.path.exists(default_path):
            specific_path = os.path.join(OUTPUT_DIR, f"traceback_{match_id}.gexf")
            import shutil
            shutil.copy2(default_path, specific_path)

        print(f"🔄 [{match_id}] 风险拓扑已动态更新完成！专属图谱已保存。节点数: {len(nodes)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"⚠️ [{match_id}] 拓扑动态更新失败: {str(e)}")


import networkx as nx
import os
import pandas as pd


def generate_real_match_graph(match_id: str, real_chat_logs: list, output_dir: str):
    """
    完全基于真实检测数据生成的局内溯源图谱
    :param match_id: 对局ID
    :param real_chat_logs: 真实的对话检测结果列表，例如：
           [{"sender": "李白", "receiver": "瑶", "text": "你个废物", "toxicity": 0.92}, ...]
    """
    if not real_chat_logs:
        raise ValueError(f"对局 {match_id} 没有检测到任何有效的对话/行为数据！")

    # 1. 转化为 DataFrame 方便做真实数据分析
    df = pd.DataFrame(real_chat_logs)

    # 2. 真实判断：谁是“污染源”（取本局说出毒性最高话语的人）
    source_hero = df.loc[df['toxicity'].idxmax()]['sender']

    # 3. 提取本局被 CV/NLP 真实捕捉到的所有英雄
    involved_heroes = set(df['sender']).union(set(df['receiver'].dropna()))

    G = nx.DiGraph()

    # 4. 基于真实的毒性得分，为节点上色
    for hero in involved_heroes:
        # 计算该英雄在真实对局中的平均毒性得分
        hero_msgs = df[df['sender'] == hero]
        avg_tox = hero_msgs['toxicity'].mean() if not hero_msgs.empty else 0

        if hero == source_hero:
            color = "#F56C6C"  # 高危：真实的污染源头
            size = 50
        elif avg_tox > 0.6:  # 毒性阈值，大于0.6说明他也骂人了
            color = "#E6A23C"  # 橙黄：真实被感染并参与传播的玩家
            size = 40
        else:
            color = "#67C23A"  # 绿色：真实的健康玩家（可能只是被骂，没有回击）
            size = 30

        G.add_node(hero, label=hero, name=hero, color=color, symbolSize=size)

    # 5. 基于真实的聊天指向（谁对谁发了违规语音/文字）建立传播连线
    for _, row in df.iterrows():
        sender = row['sender']
        receiver = row['receiver']
        tox = row['toxicity']

        if pd.notna(receiver) and sender != receiver:
            # 只有当这句话具有一定毒性（比如>0.4）或者是源头发出的，才算作“污染传播边”
            if tox > 0.4 or sender == source_hero:
                G.add_edge(sender, receiver, weight=tox)

    # 6. 保存为真实的物理文件
    file_path = os.path.join(output_dir, f"traceback_{match_id}.gexf")
    nx.write_gexf(G, file_path)

    return source_hero, len(involved_heroes)

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
def get_graph(match_id: Optional[str] = None):
    default_path = os.path.join(OUTPUT_DIR, "traceback_graph.gexf")
    specific_path = os.path.join(OUTPUT_DIR, f"traceback_{match_id}.gexf") if match_id else default_path

    # 优先找这局专属的，找不到就用全局默认的
    target_path = specific_path if os.path.exists(specific_path) else default_path

    # 加上这几行日志，方便你在控制台看它到底在读哪个文件！
    if not os.path.exists(target_path):
        print(f"❌ 前端请求了图谱，但后端找不到文件: {target_path} (可能还在生成中)")
        return {"nodes": [], "links": []}

    print(f"✅ 成功读取图谱文件: {target_path}，正在发送给前端...")
    return gexf_to_echarts(target_path)


@slang_router.post("/analyze")
def run_analysis(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        import uuid
        import random
        # 1. 自动为本次总线调用生成一个专属的对局 ID
        match_id = f"MATCH_{uuid.uuid4().hex[:6].upper()}"

        # 2. 将后台图谱生成任务绑定到这个专属 ID 上
        background_tasks.add_task(update_risk_topology_task, match_id)

        # 3. 模拟 GAT 算法的风险推演结果 (如果你有真实返回，可以替换)
        affected = random.randint(1, 20)
        risk_level = "高危扩散" if affected > 5 else "低危正常"
        risk_class = "negative" if affected > 5 else "positive"
        source_player = f"Player_Toxic_{random.randint(100, 999)}" if affected > 5 else "无明显污染源"

        # 4. 💡 核心修复：将生成的溯源结果写入 trace_records 数据库表！
        new_record = TraceRecord(
            match_id=match_id,
            source_player=source_player,
            affected_count=affected,
            risk_level=risk_level,
            risk_class=risk_class
        )
        db.add(new_record)
        db.commit()

        return {"status": "success", "message": f"图神经网络训练完毕，已生成对局: {match_id}"}
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

        # 5. 使用 FastAPI 原生的后台任务机制处理耗时的图网络重构
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


# ================= 路由 6: 风险溯源专用接口 =================
class TraceAnalyzeRequest(BaseModel):
    match_id: str


@app.get("/api/v1/trace/records", tags=["风险溯源模块"])
def get_trace_records(db: Session = Depends(get_db)):
    # 按照时间倒序查询所有溯源记录
    records = db.query(TraceRecord).order_by(TraceRecord.id.desc()).all()
    return {"data": records}


@app.post("/api/v1/trace/analyze", tags=["风险溯源模块"])
def analyze_trace(req: TraceAnalyzeRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        # ================================================================
        # 【真实检测逻辑接入点】
        # 这里你需要对接你的数据库，或者直接调用你的模型去跑这个视频/音频
        # 假设你从数据库或模型中，提取出了该对局的真实交互记录：
        # ================================================================

        # 伪代码：real_data = your_nlp_model.extract_heroes_and_chats(req.match_id)
        # 下面是你模型提取出来的【真实格式示例】，你需要将模型的真实输出转成这个格式：
        real_detected_logs = [
            {"sender": "李白", "receiver": "瑶", "text": "会不会玩啊别送了", "toxicity": 0.85},
            {"sender": "瑶", "receiver": "李白", "text": "你打野不抓人怪我？", "toxicity": 0.65},
            {"sender": "李白", "receiver": "鲁班七号", "text": "下路也是个废物", "toxicity": 0.88},
            {"sender": "鲁班七号", "receiver": "李白", "text": "（挂机无发言）", "toxicity": 0.1},
            {"sender": "妲己", "receiver": "李白", "text": "别吵了好好打", "toxicity": 0.05}
        ]

        # 1. 将真实的检测结果，喂给图谱生成器！
        source_hero, affected_count = generate_real_match_graph(
            match_id=req.match_id,
            real_chat_logs=real_detected_logs,
            output_dir=OUTPUT_DIR
        )

        # 2. 真实评级计算
        risk_level = "高危扩散" if affected_count >= 5 else "中危波及"
        risk_class = "negative" if affected_count >= 5 else "neutral"

        # 3. 将真实的污染源入库
        new_record = TraceRecord(
            match_id=req.match_id,
            source_player=source_hero,  # 真正检测出来的万恶之源（比如本局的“李白”）
            affected_count=affected_count,
            risk_level=risk_level,
            risk_class=risk_class
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        return {"status": "success", "message": "对局真实溯源分析完毕！", "data": new_record}
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        return {"status": "error", "message": f"分析失败: {str(e)}"}


@app.get("/api/datasets/toxicn", tags=["前端直连接口"])
def get_real_dataset():
    # 精准定位 backend/data/datasets 目录
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATASETS_DIR = os.path.join(BASE_DIR, "data", "datasets")

    texts_pool = []
    files_to_try = ["ToxiCN_1.0.csv", "train.json", "dev.json", "test.json"]

    for file_name in files_to_try:
        file_path = os.path.join(DATASETS_DIR, file_name)
        if not os.path.exists(file_path):
            continue
        try:
            if file_name.endswith('.csv'):
                df = pd.read_csv(file_path)
                text_col = 'text' if 'text' in df.columns else ('content' if 'content' in df.columns else df.columns[0])
                for t in df[text_col].dropna().tolist():
                    if len(str(t)) > 5:
                        texts_pool.append({"text": str(t), "source": file_name})
            elif file_name.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        for item in json.load(f):
                            text = item.get('text', '') if isinstance(item, dict) else str(item)
                            if len(text) > 5: texts_pool.append({"text": text, "source": file_name})
                    except:
                        f.seek(0)
                        for line in f:
                            if line.strip():
                                text = json.loads(line.strip()).get('text', '')
                                if len(text) > 5: texts_pool.append({"text": text, "source": file_name})
        except Exception as e:
            print(f"读取文件 {file_name} 失败: {e}")

    if not texts_pool:
        return {"error": "未找到数据集，请检查目录"}

    random.shuffle(texts_pool)
    selected_pool = texts_pool[:1200]

    return [
        {
            "id": f"TX-{10000 + i}",
            "text": item["text"],
            "status": "已完成" if i % 9 == 0 else "待标注",
            "source": item["source"]
        } for i, item in enumerate(selected_pool)
    ]

# ================= 启动入口 =================
if __name__ == "__main__":
    import uvicorn

    print("🚀 深蓝卫士核心引擎启动中...")
    uvicorn.run(app, host="127.0.0.1", port=8000, loop="none")