import os
import warnings

warnings.filterwarnings("ignore")

# 默认建议改为 True，或者在电脑的环境变量中配置
ENABLE_TEXT_AI = os.getenv("ENABLE_TEXT_AI", "True") == "True"

toxicity_pipe = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_FOLDER_NAME = "toxicity_model"
model_path = os.path.join(BASE_DIR, "data", "weights", MODEL_FOLDER_NAME)

if ENABLE_TEXT_AI:
    print(f">> [文本模块] 准备从本地加载专属 AI 大脑...")

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"\n❌ 严重错误：找不到你的模型文件夹！\n请确认你是否把 [{MODEL_FOLDER_NAME}] 文件夹放到了 \n[{os.path.join(BASE_DIR, 'data', 'weights')}] 目录下！")

    try:
        from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)
        toxicity_pipe = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
        print(">> [文本模块] 🎉 游戏黑话模型加载成功！矩阵维度已对齐！")
    except Exception as e:
        raise RuntimeError(f">> [文本模块] ❌ 模型加载失败: {e}")
else:
    print(">> [文本模块] ⚠️ 注意：未开启真实大模型 (ENABLE_TEXT_AI=False)")


def get_toxicity_score(text: str) -> float:
    """
    【计算并返回 0-1 的毒性分数】
    """
    # ！！！核心修改：去掉原先的 0.88，拒绝对前端撒谎 ！！！
    if not ENABLE_TEXT_AI or toxicity_pipe is None:
        raise ValueError("AI引擎未加载！前端请求已被真实拦截，请检查后端模型配置。")

    # 真实的 AI 算分逻辑
    result = toxicity_pipe(text[:512])[0]
    score = result['score']
    label = result['label']

    if label == "LABEL_1" or str(label) == "1":
        return round(score, 4)
    else:
        return round(1.0 - score, 4)