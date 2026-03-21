import matplotlib.pyplot as plt
import networkx as nx
import os

def save_visualizations(G, source_node, output_dir='output'):
    os.makedirs(output_dir, exist_ok=True)
    
    # 设置支持中文（解决 Windows 系统乱码）
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False

    plt.figure(figsize=(15, 10))
    
    # 使用 Spring Layout 布局
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    # 节点颜色：污染源设为红色，普通用户设为天蓝色
    node_colors = []
    for node in G.nodes():
        if node == source_node:
            node_colors.append('red')
        else:
            node_colors.append('skyblue')

    # 绘制图形
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color=node_colors, alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, edge_color='gray', arrows=True)
    nx.draw_networkx_labels(G, pos, font_size=9, font_family='sans-serif')

    plt.title(f"DOTA2 黑话溯源传播图谱\n(识别核心污染源: {source_node})", fontsize=15)
    
    # 保存图片
    img_path = os.path.join(output_dir, 'graph_viz.png')
    plt.savefig(img_path, bbox_inches='tight')
    plt.close()

    # 导出 GEXF 文件 (Gephi 专用)
    gexf_path = os.path.join(output_dir, 'traceback_graph.gexf')
    nx.write_gexf(G, gexf_path)
    
    print(f"[Visual] 可视化结果已保存至: {output_dir}")

if __name__ == "__main__":
    print("可视化模块加载成功。")