import os
import warnings
warnings.filterwarnings("ignore")

# 【大模型默认不加载开关】专门为你自己设定的专属开关
ENABLE_TEXT_AI = os.getenv("ENABLE_TEXT_AI", "False") == "True"

toxicity_pipe = None

# 【核心加固 1】：获取项目的绝对根目录（backend文件夹）
# 使用 __file__，无论你在哪个文件夹下敲启动命令，这个路径都绝对不会跑偏！
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


MODEL_FOLDER_NAME = "toxicity_model" 
model_path = os.path.join(BASE_DIR, "data", "weights", MODEL_FOLDER_NAME)

if ENABLE_TEXT_AI:
    print(f">> [文本模块] 准备从本地加载专属 AI 大脑...")
    print(f">> [文本模块] 正在寻找绝对路径: {model_path}")
    
    # 【核心加固 2】：强制断网检查
    # 如果路径不对或找不到你的文件夹，直接在这里主动报错拦住！绝对不让它去网上乱下载别的模型！
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"\n❌ 严重错误：找不到你的模型文件夹！\n请确认你是否把 [{MODEL_FOLDER_NAME}] 文件夹放到了 \n[{os.path.join(BASE_DIR, 'data', 'weights')}] 目录下！")
        
    try:
        from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
        
        # 【核心加固 3】：加上 local_files_only=True 
        # 这等于给模型加上了“断网锁”，彻底斩断它去抱 HuggingFace 大腿的念头，只准读你练好的本地文件！
        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)
        
        toxicity_pipe = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
        print(">> [文本模块] 🎉 游戏黑话模型加载成功！矩阵维度已对齐！")
    except Exception as e:
        print(f">> [文本模块] ❌ 加载失败，模型文件可能不完整: {e}")
else:
    print(">> [文本模块] 开发模式，未加载几百兆模型。开启真实 AI 请设置环境变量 ENABLE_TEXT_AI=True")

def get_toxicity_score(text: str) -> float:
    """
    【计算并返回 0-1 的毒性分数】
    """
    if not ENABLE_TEXT_AI or toxicity_pipe is None:
        return 0.88  # 没开 AI 时给个假分数，保证其他队友运行后端时不报错
        
    # 真实的 AI 算分逻辑
    result = toxicity_pipe(text[:512])[0]
    score = result['score']
    label = result['label']
    
    # 把模型的标签转化为 0-1 的毒性分数 
    # (如果你的模型把 1 当作正常，0 当作有毒，请把下面 if 和 else 里的 return 对调一下)
    if label == "LABEL_1" or str(label) == "1":
        return round(score, 4)
    else:
        return round(1.0 - score, 4)