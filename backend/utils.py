import networkx as nx
import base64
import os

def gexf_to_echarts(file_path):
    """转换 GEXF 为 ECharts 格式"""
    if not os.path.exists(file_path):
        return {"nodes": [], "links": []}
    G = nx.read_gexf(file_path)
    # 简单的节点与边转换逻辑
    nodes = [{"id": str(n), "name": str(n), "symbolSize": 30} for n in G.nodes()]
    links = [{"source": str(u), "target": str(v)} for u, v in G.edges()]
    return {"nodes": nodes, "links": links}

def img_to_b64(img_path):
    """图片转 Base64 供前端预览"""
    if not os.path.exists(img_path): return ""
    with open(img_path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()