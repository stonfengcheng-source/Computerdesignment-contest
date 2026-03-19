import os
import shutil
import json
import traceback
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

# ================= 业务模块导入 (极其重要：顺序不能乱) =================
# 1. 数据库引擎与基础基类
from app.core.database import engine, Base, get_db

# 2. 数据库表模型 (必须在 create_all 之前导入，否则 SQLite 无法建表！)
from app.models.behavior_model import InconsistencyRecord

# 3. 核心 AI 分析服务
from app.services.video_analysis_service import process_video_for_inconsistency
from app.text_api import router as text_router
from app.services.credit_service import generate_cross_platform_credit
from app.services.report_service import generate_comprehensive_report

# 4. 黑话图谱模块
from utils import gexf_to_echarts, img_to_b64
from scripts.crawler import get_data
from scripts.processor import build_graph_data
from scripts.model_gat import train_gat

# ================= 初始化配置与建表 =================
# 自动创建所有定义的数据库表 (必须在导入 Model 之后执行)
Base.metadata.create_all(bind=engine)

# 全局路径绝对定位，防止相对路径导致的 FileNotFoundError
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")

# 确保必要的目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="深蓝卫士 (全链路架构版)", description="基于多模态博弈大数据的网络游戏生态健康度监测平台")

# 跨域设置
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
        get_data()
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


# ================= 路由 3: 主控制台多模态输入口 (视频流聚合) =================
@app.post("/api/v1/analyze/video", tags=["多模态综合检测调度器"])
async def upload_and_analyze_video(
        player_id: str = Form(...),
        video_file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    """
    这是前端 Dashboard 调用的核心引擎。
    它接收一个多模态源(视频)，在内部剥离出声音和图像，分别送入 NLP 和 CV 模块。
    """
    try:
        # 1. 安全保存文件
        file_path = os.path.join(UPLOAD_DIR, video_file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)

        # 2. 调度多模态分析 (OpenCV提取行为, BERT提取文本毒性)
        text_prob, behavior_error, toxicity_score, is_inconsistent, risk_level = process_video_for_inconsistency(
            video_path=file_path,
            player_id=player_id
        )

        # 3. 结果持久化入库
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

        # 4. 组装多模态视图数据返回
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
        # 打印完整的错误栈到终端，绝不死得不明不白
        traceback.print_exc()
        return {"status": "error", "message": f"多模态引擎运行异常: {str(e)}"}

@app.get("/api/v1/records", tags=["多模态综合检测调度器"])
async def get_all_records(db: Session = Depends(get_db)):
    records = db.query(InconsistencyRecord).all()
    return {"data": records}


# ================= 路由 4: 跨平台信用分模块 =================
@app.get("/api/v1/credit/{player_id}", tags=["跨平台信用评级"])
async def get_player_credit(player_id: str):
    try:
        result = await generate_cross_platform_credit(player_id)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ================= 路由 5: 最终多模态融合报告模块 (XGBoost) =================
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