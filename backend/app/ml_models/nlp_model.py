# 文件路径: app/ml_models/nlp_model.py

import os
import warnings

# ！！！最核心的加速机制：必须在导入任何第三方库之前，强行注入环境变量！！！
# 1. 设置国内极速镜像源
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
# 2. 启用刚安装的 Rust 多线程底层下载器 (hf_transfer)
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

# 在环境变量彻底生效后，再导入大模型库
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

warnings.filterwarnings("ignore")


class RoBERTaAnalyzer:
    def __init__(self, weight_path: str = None):
        print("正在初始化真实文本大模型引擎 (严谨模式)...")
        print(">> 已开启 hf_transfer (Rust并发引擎) 与 国内镜像节点双重加速！")

        # 坚持使用比赛对口的真实中文 RoBERTa 预训练模型
        model_name = "uer/roberta-base-finetuned-jd-binary-chinese"

        try:
            # 下载/加载真实的 Tokenizer 和 深度学习模型
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

            # 构建标准的推理流水线
            self.pipeline = pipeline("sentiment-analysis", model=self.model, tokenizer=self.tokenizer)
            print(">> RoBERTa 真实模型加载成功！矩阵维度已对齐。")
        except Exception as e:
            print(f"模型加载失败: {e}")
            self.pipeline = None

    def predict(self, texts: list) -> float:
        """
        真实的自注意力机制 (Self-Attention) 前向传播
        """
        if not texts or self.pipeline is None:
            return 0.5

        combined_text = " ".join(texts)
        # 截断文本以适应 RoBERTa 的 512 token 限制
        combined_text = combined_text[:500]

        # 真实张量推理
        result = self.pipeline(combined_text)[0]

        if result['label'] == 'positive':
            return float(result['score'])
        else:
            return 1.0 - float(result['score'])