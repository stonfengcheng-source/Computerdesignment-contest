# backend/scripts/train_text_model.py
import os
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import Trainer, TrainingArguments
from datasets import Dataset
import pandas as pd


def train_and_save_model():
    print("开始加载基础预训练模型...")
    # 1. 采用学术界常用的中文 BERT 预训练模型作为基座
    model_name = "bert-base-chinese"
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)  # 2分类：正常(0) / 违规(1)

    # 2. 准备你的真实训练数据集 (你需要准备一个包含 'text' 和 'label' 的 CSV)
    # 这里是加载数据的范例，请替换为你自己的数据文件路径
    # df = pd.read_csv('../data/game_chat_dataset.csv')

    # 【严谨测试】：如果你暂时没有海量数据，我们可以先用一个极小的数据集让训练跑通
    mock_data = {
        "text": ["兄弟们稳住，能赢", "你这操作像个傻子", "一起推中路", "菜狗别送了"],
        "label": [0, 1, 0, 1]  # 0代表正常，1代表毒性/阴阳怪气
    }
    df = pd.DataFrame(mock_data)

    # 将 Pandas DataFrame 转为 HuggingFace Dataset
    dataset = Dataset.from_pandas(df)

    # 分词处理函数
    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=64)

    tokenized_datasets = dataset.map(tokenize_function, batched=True)

    # 3. 设置真实的训练超参数
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,  # 迭代次数
        per_device_train_batch_size=8,  # 批次大小
        learning_rate=2e-5,  # 学习率
        logging_steps=10,
    )

    # 4. 启动 Trainer 进行真实梯度下降和权重更新
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets,
    )

    print("🚀 开始真实训练 (反向传播更新权重)...")
    trainer.train()

    # 5. 【核心步骤】：把训练好的真实权重保存到报错提示的那个目录里！
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_path = os.path.join(BASE_DIR, 'data', 'weights', 'toxicity_model')
    os.makedirs(save_path, exist_ok=True)

    model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)

    print(f"✅ 学术模型训练完成！真实权重已成功保存至：{save_path}")
    print("现在你可以启动 main.py，系统将加载真实的 AI 参数！")


if __name__ == "__main__":
    train_and_save_model()