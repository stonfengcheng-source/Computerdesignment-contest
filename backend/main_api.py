from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os, json
from utils import gexf_to_echarts, img_to_b64
# 导入之前的算法逻辑
from scripts.crawler import get_data
from scripts.processor import build_graph_data
from scripts.model_gat import train_gat

app = FastAPI(title="DOTA2 Slang API")

# 解决跨域
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DATA_DIR = os.path.join(BASE_DIR, "data")

@app.get("/api/slang/dict")
def get_dict():
    path = os.path.join(DATA_DIR, "slang_dict.json")
    if not os.path.exists(path): raise HTTPException(404, "Dict not found")
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

@app.get("/api/slang/graph")
def get_graph():
    return gexf_to_echarts(os.path.join(OUTPUT_DIR, "traceback_graph.gexf"))

@app.get("/api/slang/image")
def get_image():
    return {"image": img_to_b64(os.path.join(OUTPUT_DIR, "graph_viz.png"))}

@app.post("/api/slang/analyze")
async def run_analysis():
    try:
        get_data() # 1. 爬取/生成
        G, x, edge_index, nodes = build_graph_data(os.path.join(DATA_DIR, "raw_chats.csv")) # 2. 构建
        # 3. 训练溯源 (简化示例)
        import torch
        y = torch.zeros(len(nodes), dtype=torch.long); y[:2] = 1
        train_gat(x, edge_index, y) 
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(500, str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)