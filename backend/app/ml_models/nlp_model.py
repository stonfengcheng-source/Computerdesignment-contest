# 文件路径: app/ml_models/nlp_model.py

import os
import warnings

# 环境变量设置保持不变
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

warnings.filterwarnings("ignore")


class RoBERTaAnalyzer:
    def __init__(self, weight_path: str = None):
        print("正在初始化 阴阳怪气/违规检测 本地模型...")
        print(">> 已开启 hf_transfer (Rust并发引擎) 与 国内镜像节点双重加速！")

        if weight_path is None:
            # 自动定位到您刚才训练脚本保存的默认路径
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            weight_path = os.path.join(base_dir, 'data', 'weights', 'toxicity_model')

        print(f">> 正在加载本地权重: {weight_path}")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(weight_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(weight_path)

            self.pipeline = pipeline("text-classification", model=self.model, tokenizer=self.tokenizer)
            print(">> 自定义 RoBERTa 模型加载成功！矩阵维度已对齐。")
        except Exception as e:
            print(f"模型加载失败，请检查权重路径是否正确: {e}")
            self.pipeline = None

        # 💡 核心改进：添加前置“规则引擎”词库！
        # 只要碰到这些词，根本不需要经过大模型算力，直接判死刑！
        self.black_list = [
            "乡里人", "乡巴佬", "偷井盖", "南蛮", "白完", "东百",
            "小日本", "漂亮国", "弯弯", "西八"
        ]

    def predict(self, texts: list, topic: str = "游戏对局") -> float:
        """
        前向传播进行违规概率预测
        """
        if not texts:
            return 0.0  # 没输入文本，绝对安全

        combined_text = " ".join(texts)

        # 🚀 绝杀拦截逻辑：在大模型预测之前，先过一遍黑名单词库
        for bad_word in self.black_list:
            if bad_word in combined_text:
                print(f"🚨 [规则引擎拦截]: 检测到恶劣歧视词汇【{bad_word}】！")
                return 0.95

        # 💣 严苛逻辑：如果模型没加载成功，直接抛出异常阻断程序！绝不妥协返回 0.5！
        if self.pipeline is None:
            raise RuntimeError("🚨 致命错误：RoBERTa 文本大模型未成功加载！请检查权重路径！")

        input_text = f"话题：{topic} 评论：{combined_text}"
        input_text = input_text[:500]

        result = self.pipeline(input_text)[0]

        if result['label'] == 'LABEL_1':
            return float(result['score'])
        elif result['label'] == 'LABEL_0':
            return 1.0 - float(result['score'])
        else:
            return float(result['score'])