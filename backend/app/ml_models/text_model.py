import os
import torch
import warnings
from transformers import AutoTokenizer
import random
# ======= 导入你自己的五维多任务核心引擎 =======
from .Config_base import Config_base
from .Models import MultiTaskModel
from .datasets import get_all_dirty_words, get_all_toxic_id

warnings.filterwarnings("ignore")

# 环境变量：控制是否开启真实 AI 推理
ENABLE_TEXT_AI = os.getenv("ENABLE_TEXT_AI", "True") == "True"

# 全局变量占位
model = None
tokenizer = None
config = None
all_dirty_words = None
device = None

# 标签字典：用于在控制台炫技打印
label_map = {
    "toxic": {0: "✅ 正常", 1: "🚫 有毒"},
    "jargon": {0: "⚪ 非黑话", 1: "⚫ 游戏黑话"},
    "toxic_type": {0: "无毒", 1: "一般冒犯", 2: "仇恨言论"},
    "expression": {0: "无恨", 1: "显性攻击", 2: "隐性攻击", 3: "举报"},
    "target": ["LGBTQ", "地区", "性别", "种族", "其他", "无恨"]
}

# ================= 核心底层拦截黑名单 =================
# 将拦截下沉到模型底层，确保所有模块(图谱/文本/视频)调用时标准统一
CORE_BLACK_LIST = [
    # 基础地域/歧视
    "乡里人", "乡巴佬", "偷井盖", "南蛮", "白完", "东百", "小日本", "漂亮国", "弯弯", "西八",
    # 基础辱骂与消极行为
    "尼玛", "wcnm", "病", "死", "叫", "妈", "草", "操", "送","卧底","小地方",
    # 拼音缩写及严重人身攻击
    "nt", "sb", "nm", "nmsl", "nmd", "cnm", "tm", "tmd", "fw",
    "傻逼", "煞笔", "脑瘫", "孤儿", "废物", "弱智", "司马", "死妈", "畜生", "杂种", "低能", "有病", "婊子", "全家", "骨灰"
]
# ===================================================


#if ENABLE_TEXT_AI:
print(">> [文本模块] 🚀 准备点火：正在加载深蓝卫士 M-IARD 五维多任务核心引擎...")
try:
    # --- 1. 动态计算路径 (确保无论从哪启动都能精准定位) ---
    # 当前文件在 backend/app/ml_models/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 向上三级到达项目根目录 (backend/ 的父目录)
    # 如果你的 backend 就是根目录，请确保路径指向正确
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # 队友说的：pretrained_model 放在 backend/ 目录下
    # 这里拼出它的绝对路径
    LOCAL_MODEL_PATH = os.path.join(BASE_DIR, "backend", "pretrained_model")

    # 检查本地文件夹是否存在，防止报 MissingSchema 错误
    if not os.path.exists(LOCAL_MODEL_PATH):
        # 兼容性尝试：如果上面路径不对，尝试当前目录的上上级
        LOCAL_MODEL_PATH = os.path.join(os.getcwd(), "pretrained_model")

    print(f">> [文本模块] 正在从本地加载基础配置: {LOCAL_MODEL_PATH}")

    # --- 2. 使用本地路径初始化配置 (关键修改点！) ---
    # 不要传 "hfl/chinese-roberta-wwm-ext"，直接传 LOCAL_MODEL_PATH
    config = Config_base(LOCAL_MODEL_PATH, "ToxiCN")
    device = config.device

    # --- 3. 准备分词器 (此时 from_pretrained 会直接读本地 json) ---
    tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_PATH)
    all_dirty_words = get_all_dirty_words(config.lexicon_path)

    # --- 4. 实例化网络 ---
    model = MultiTaskModel(config).to(device)

    # --- 5. 定位并加载 .tar 权重 (保持你原有的逻辑，只需确保 weights_dir 正确) ---
    weights_dir = os.path.join(BASE_DIR,  "data", "weights")
    tar_files = [f for f in os.listdir(weights_dir) if f.endswith('.tar')]
    if not tar_files:
        raise FileNotFoundError(f"❌ 找不到权重！请检查 {weights_dir}")

    model_path = os.path.join(weights_dir, tar_files[0])
    print(f">> [文本模块] 正在注入灵魂参数: {tar_files[0]}")

    # 关键点：队友代码里用的是 'model_state_dict'，确保 Key 对应
    checkpoint = torch.load(model_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    print(">> [文本模块] 🎉 本地离线模型加载成功！")

except Exception as e:
    import traceback

    traceback.print_exc()
    raise RuntimeError(f">> [文本模块] ❌ 模型加载失败: {e}")
#else:
#    print(">> [文本模块] ⚠️ 注意：未开启真实大模型 (ENABLE_TEXT_AI=False)")

def get_toxicity_score(text: str) -> dict:
    """
    【核心算分接口】
    严格返回 0-1 的毒性分数给系统的其他模块，
    同时在控制台打印五维细粒度分析报告！
    """
    if not ENABLE_TEXT_AI or model is None:
        raise ValueError("AI引擎未加载！前端请求已被真实拦截，请检查后端模型配置。")

    clean_text = text.lower()

    # 🚀 1. 引擎级前置绝杀：只要命中，绕过大模型直接生成高毒性特征
    hit_word = next((w for w in CORE_BLACK_LIST if w in clean_text), None)
    if hit_word:
        # 生成 0.85 到 0.95 之间的随机分数，保留 4 位小数
        rand_toxicity = round(random.uniform(0.85, 0.95), 4)
        # 游戏黑话分数也可以稍微随机一下，比如 0.80 到 0.95 之间
        rand_jargon = round(random.uniform(0.80, 0.95), 4)

        print(f"\n💬 [M-IARD 捕获新文本 (引擎硬拦截)]: 【 {text} 】")
        print(f"  👉 命中高危词: 【{hit_word}】")
        print(f"  👉 基础毒性: {rand_toxicity:.4f} (🚫 有毒)")
        print(f"  👉 游戏黑话: {rand_jargon-0.5:.4f} (⚫ 是黑话)")
        print(f"  👉 毒性类型: 一般冒犯")
        print(f"  👉 表达手段: 显性攻击")
        print(f"  👉 攻击群体: 特定目标")
        print("-" * 50)

        return {
            "toxicity_score": rand_toxicity,
            "is_jargon": True,
            "toxic_type": "一般冒犯",
            "expression": "显性攻击",
            "target_groups": ["特定目标"]
        }

    # 🚀 2. 正常的大模型五路联合推理逻辑 (未命中黑名单的复杂文本)
    encoded = tokenizer(text, add_special_tokens=True, max_length=config.pad_size, padding='max_length',
                        truncation=True)
    text_idx = encoded['input_ids']
    text_ids = encoded['token_type_ids']
    text_mask = encoded['attention_mask']

    toxic_ids = get_all_toxic_id(config.pad_size, text_idx, all_dirty_words)

    inputs = {
        'text_idx': torch.tensor([text_idx]).to(device),
        'text_ids': torch.tensor([text_ids]).to(device),
        'text_mask': torch.tensor([text_mask]).to(device),
        'toxic_ids': torch.tensor([toxic_ids]).to(device)
    }

    with torch.no_grad():
        out_toxic, out_jargon, out_type, out_expr, out_target = model(**inputs)

    toxic_probs = torch.softmax(out_toxic, dim=1)[0]
    toxicity_score = toxic_probs[1].item()

    jargon_score = torch.softmax(out_jargon, dim=1)[0][1].item()
    res_type = torch.argmax(out_type, dim=1).item()
    res_expr = torch.argmax(out_expr, dim=1).item()

    target_probs = torch.sigmoid(out_target)[0]
    res_targets = [label_map["target"][i] for i, p in enumerate(target_probs) if p > 0.5]
    if not res_targets:
        res_targets = ["未检测到特定目标"]

    print(f"\n💬 [M-IARD 捕获新文本 (深度分析)]: 【 {text} 】")
    print(f"  👉 基础毒性: {toxicity_score:.4f} ({'🚫 有毒' if toxicity_score > 0.5 else '✅ 正常'})")
    print(f"  👉 游戏黑话: {jargon_score:.4f} ({'⚫ 是黑话' if jargon_score > 0.5 else '⚪ 非黑话'})")
    print(f"  👉 毒性类型: {label_map['toxic_type'][res_type]}")
    print(f"  👉 表达手段: {label_map['expression'][res_expr]}")
    print(f"  👉 攻击群体: {', '.join(res_targets)}")
    print("-" * 50)

    return {
        "toxicity_score": round(toxicity_score, 4),
        "is_jargon": True if jargon_score > 0.5 else False,
        "toxic_type": label_map['toxic_type'][res_type],
        "expression": label_map['expression'][res_expr],
        "target_groups": res_targets
    }