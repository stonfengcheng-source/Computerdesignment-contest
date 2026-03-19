import os
import shutil
import json
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

# ================= 业务模块导入 =================
# 1. 数据库与基础模型
from app.core.database import engine, Base, get_db
from app.models.behavior_model import InconsistencyRecord

# 2. 视频分析服务 (言行不一)
from app.services.video_analysis_service import process_video_for_inconsistency
from app.text_api import router as text_router

# 3. 新增核心服务: 跨平台信用分与多模态报告
from app.services.credit_service import generate_cross_platform_credit
from app.services.report_service import generate_comprehensive_report

# 4. 黑话图谱模块导入
from utils import gexf_to_echarts, img_to_b64
from scripts.crawler import get_data
from scripts.processor import build_graph_data
from scripts.model_gat import train_gat

# ================= 初始化配置 =================
# 初始化数据库
Base.metadata.create_all(bind=engine)

# 路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DATA_DIR = os.path.join(BASE_DIR, "data")

app = FastAPI(title="深蓝卫士 (校赛展示版)", description="基于多模态博弈大数据的网络游戏生态健康度监测与信用评级平台")

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
        raise HTTPException(404, "Dict not found")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

@slang_router.get("/graph")
def get_graph():
    return gexf_to_echarts(os.path.join(OUTPUT_DIR, "traceback_graph.gexf"))

@slang_router.get("/image")
def get_image():
    return {"image": img_to_b64(os.path.join(OUTPUT_DIR, "graph_viz.png"))}

@slang_router.post("/analyze")
async def run_analysis():
    try:
        get_data() # 1. 爬取/生成
        G, x, edge_index, nodes = build_graph_data(os.path.join(DATA_DIR, "raw_chats.csv")) # 2. 构建
        # 3. 训练溯源 (简化示例)
        import torch
        y = torch.zeros(len(nodes), dtype=torch.long)
        y[:2] = 1
        train_gat(x, edge_index, y)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(500, str(e))

app.include_router(slang_router)

# ================= 路由 3: 视频行为分析模块 =================
# === 替换 main.py 中的 /api/v1/analyze/video 路由 ===

@app.post("/api/v1/analyze/video", tags=["言行不一检测模块"])
async def upload_and_analyze_video(
        player_id: str = Form(...),
        video_file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    upload_dir = os.path.join(DATA_DIR, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, video_file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(video_file.file, buffer)

    # ================= 核心桥梁：特征提取层 =================
    print(f">> [特征提取] 正在处理视频 {video_file.filename}...")
    # 按照您的文档规划，这里未来会接入 OpenAI Whisper 提取语音
    # 和 CV 模型提取画面中的 KDA/经济数据。
    # 【注意】在您的提取模型写好前，这里暂时用测试提取数据代替（这不是拟合最终分数，而是模拟前置提取器的输出）
    mock_extracted_texts = ["兄弟们稳住，交给我来操作，看我秀他"]
    mock_extracted_actions = [
        {"gold": 50, "kda": "0-5-0", "move": "异常停留"},
        {"gold": 50, "kda": "0-6-0", "move": "向敌方泉水移动"}
    ]
    # ========================================================

    # 将提取出的真实/模拟特征喂给刚刚改好的严格算力引擎
    try:
        analysis_result = process_video_for_inconsistency(
            video_path=file_path,
            player_id=player_id,
            extracted_texts=mock_extracted_texts,
            extracted_actions=mock_extracted_actions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 存入数据库
    new_record = InconsistencyRecord(
        video_filename=video_file.filename,
        player_id=player_id,
        text_prob=analysis_result["text_sentiment_prob"],
        behavior_error=analysis_result["behavior_anomaly_score"],
        toxicity_score=analysis_result["behavior_anomaly_score"],  # 暂代
        is_inconsistent=analysis_result["is_inconsistent"],
        risk_level=analysis_result["local_risk_level"]
    )
    db.add(new_record)
    db.commit()

    return {
        "status": "success",
        "result": analysis_result
    }

# ================= 路由 4: 跨平台信用分模块 =================
@app.get("/api/v1/credit/{player_id}", tags=["跨平台信用评级"])
async def get_player_credit(player_id: str):
    """输入玩家MOBA ID，并发拉取多平台数据，生成信用得分及雷达图"""
    result = await generate_cross_platform_credit(player_id)
    return {"status": "success", "data": result}

# ================= 路由 5: 多模态融合报告模块 =================
class ReportRequest(BaseModel):
    player_id: str
    text_toxicity: float
    audio_toxicity: float
    behavior_anomaly: float
    graph_risk: float

@app.post("/api/v1/report/generate", tags=["多模态综合报告生成"])
async def generate_report(req: ReportRequest):
    """基于 XGBoost 融合各模块毒性特征，输出最终裁决报告"""
    result = generate_comprehensive_report(
        player_id=req.player_id,
        text_toxicity=req.text_toxicity,
        audio_toxicity=req.audio_toxicity,
        behavior_anomaly=req.behavior_anomaly,
        graph_risk=req.graph_risk
    )
    return {"status": "success", "data": result}

# ================= 启动入口 =================
if __name__ == "__main__":
    import uvicorn
    # 统一在 8000 端口启动整个大后端的服务
    uvicorn.run(app, host="127.0.0.1", port=8000)