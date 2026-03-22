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

        # 【核心修复1】：真正使用本地训练好的权重路径！绝不硬编码！
        if weight_path is None:
            # 自动定位到您刚才训练脚本保存的默认路径
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            weight_path = os.path.join(base_dir, 'data', 'weights', 'toxicity_model')

        print(f">> 正在加载本地权重: {weight_path}")

        try:
            # 【核心修复2】：从本地路径加载 Tokenizer 和 模型
            self.tokenizer = AutoTokenizer.from_pretrained(weight_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(weight_path)

            # 【核心修复3】：将 pipeline 改为通用的 text-classification
            self.pipeline = pipeline("text-classification", model=self.model, tokenizer=self.tokenizer)
            print(">> 自定义 RoBERTa 模型加载成功！矩阵维度已对齐。")
        except Exception as e:
            print(f"模型加载失败，请检查权重路径是否正确: {e}")
            self.pipeline = None

    def predict(self, texts: list, topic: str = "游戏对局") -> float:
        """
        前向传播进行违规概率预测
        """
        if not texts or self.pipeline is None:
            return 0.5

        combined_text = " ".join(texts)

        # 【核心修复4】：推理时的输入格式必须与训练时（train_text_model.py）严格保持一致
        input_text = f"话题：{topic} 评论：{combined_text}"

        # 截断文本以适应 RoBERTa 的 512 token 限制
        input_text = input_text[:500]

        # 真实张量推理
        result = self.pipeline(input_text)[0]

        # HuggingFace 二分类默认输出 LABEL_0 和 LABEL_1
        # 假设训练时 1 代表违规/阴阳怪气，0 代表正常
        if result['label'] == 'LABEL_1':
            return float(result['score'])  # 违规的概率
        elif result['label'] == 'LABEL_0':
            return 1.0 - float(result['score'])  # 正常的概率取反即为违规概率
        else:
            # 兜底兼容
            return float(result['score'])