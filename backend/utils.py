import networkx as nx
import base64
import os


def gexf_to_echarts(file_path):
    """转换 GEXF 为前端支持的格式，保留颜色和大小属性"""
    if not os.path.exists(file_path):
        return {"nodes": [], "links": []}

    G = nx.read_gexf(file_path)
    nodes = []
    for n, d in G.nodes(data=True):
        nodes.append({
            "id": str(n),
            "name": d.get("name", str(n)),
            "label": d.get("label", str(n)),
            "symbolSize": d.get("symbolSize", 30),
            "color": d.get("color", "#67C23A")  # 提取节点真实颜色
        })

    links = [{"source": str(u), "target": str(v)} for u, v in G.edges()]
    return {"nodes": nodes, "links": links}

def img_to_b64(img_path):
    """图片转 Base64 供前端预览"""
    if not os.path.exists(img_path): return ""
    with open(img_path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()