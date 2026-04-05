# backend/app/api/api.py
from fastapi import APIRouter
from pydantic import BaseModel
import json
import os

# 这里引入的是图谱处理函数，而不是直接引入模型
from app.services.graph_processor import build_graph_data

# 创建一个路由实例
router = APIRouter()


class MatchRequest(BaseModel):
    match_id: str


# 创建一个专门存放对局图谱数据的文件夹（模拟数据库，路径放在项目根目录下比较好找）
GRAPH_DB_DIR = "app/data/graph_records"
os.makedirs(GRAPH_DB_DIR, exist_ok=True)


# 1. 分析并保存图谱的接口
@router.post("/api/v1/trace/analyze")
async def analyze_match(request: MatchRequest):
    # 请确保这个 raw_chats.csv 文件存在，或者改成你真实的 CSV 路径
    csv_path = "app/data/raw_chats.csv"

    # 调用 graph_processor.py 里的函数
    G, x, edge_index, frontend_nodes, frontend_edges = build_graph_data(csv_path)

    if frontend_nodes is None:
        return {"status": "error", "message": "图谱构建失败，找不到CSV文件"}

    # 组装要存入本地 JSON 的数据
    record_data = {
        "match_id": request.match_id,
        "nodes": frontend_nodes,
        "edges": frontend_edges
    }

    # 写入 JSON 文件持久化保存
    file_path = os.path.join(GRAPH_DB_DIR, f"{request.match_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(record_data, f, ensure_ascii=False)

    return {"status": "success", "message": "溯源分析完毕并已入库"}


# 2. 前端请求图谱数据的接口
@router.get("/api/v1/trace/graph/{match_id}")
async def get_match_graph(match_id: str):
    file_path = os.path.join(GRAPH_DB_DIR, f"{match_id}.json")

    # 如果找不到对应对局的记录，返回空数组
    if not os.path.exists(file_path):
        return {"data": {"nodes": [], "edges": []}}

    # 读取并返回给前端 Echarts
    with open(file_path, "r", encoding="utf-8") as f:
        graph_data = json.load(f)

    return {"data": graph_data}