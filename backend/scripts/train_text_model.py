# backend/scripts/train_text_model.py
import os
import json
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import Trainer, TrainingArguments
from datasets import Dataset


def load_json_dataset(json_path):
    """加载 json 格式的隐式阴阳怪气数据集"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    # 核心：构造带有语境的输入格式
    df['combined_text'] = "话题：" + df['topic'].astype(str) + " 评论：" + df['text'].astype(str)
    df['label'] = df['label'].astype(int)
    return df[['combined_text', 'label']]


def load_csv_dataset(csv_path):
    """加载 ToxiCN 显式攻击数据集进行数据增强"""
    df = pd.read_csv(csv_path)
    df = df[['topic', 'content', 'toxic']].dropna()
    df['combined_text'] = "话题：" + df['topic'].astype(str) + " 评论：" + df['content'].astype(str)
    df.rename(columns={'toxic': 'label'}, inplace=True)
    return df[['combined_text', 'label']]


def train_and_save_model():
    print("1. 开始加载 RoBERTa 预训练基座模型...")
    model_name = "hfl/chinese-roberta-wwm-ext"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    # 2分类：正常(0) / 违规或阴阳怪气(1)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

    print("2. 加载与融合真实数据集...")
    # 请确保以下路径下的文件存在
    data_dir = r"D:\PythonProject\Computerdesignment-contest\backend\data\datasets"

    train_df = load_json_dataset(os.path.join(data_dir, "train.json"))
    dev_df = load_json_dataset(os.path.join(data_dir, "dev.json"))

    # 抽取部分 ToxiCN 数据混合训练，提升模型对直接脏话的拦截能力
    toxicn_df = load_csv_dataset(os.path.join(data_dir, "ToxiCN_1.0.csv"))
    # 混合训练集并打乱
    combined_train_df = pd.concat([train_df, toxicn_df.sample(frac=0.3, random_state=42)]).sample(frac=1).reset_index(
        drop=True)

    train_dataset = Dataset.from_pandas(combined_train_df)
    dev_dataset = Dataset.from_pandas(dev_df)

    def tokenize_function(examples):
        # 截断长度设为128，平衡性能和显存
        return tokenizer(examples["combined_text"], padding="max_length", truncation=True, max_length=128)

    print("3. 数据分词处理 (Tokenization)...")
    tokenized_train = train_dataset.map(tokenize_function, batched=True)
    tokenized_dev = dev_dataset.map(tokenize_function, batched=True)

    # 4. 设置指定的保存路径
    save_path = r"D:\PythonProject\Computerdesignment-contest\backend\data\weights\toxicity_model"
    os.makedirs(save_path, exist_ok=True)

    print("4. 设置训练超参数...")
    training_args = TrainingArguments(
        output_dir=save_path,
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        learning_rate=2e-5,
        logging_steps=50,
        eval_strategy="epoch",  # ❗修复点：修改为新版本的 eval_strategy
        save_strategy="epoch",
        load_best_model_at_end=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_dev,
    )

    print("🚀 开始真实训练 (反向传播更新权重)...")
    trainer.train()

    print("5. 保存最终模型权重...")
    model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)
    print(f"✅ 模型训练完成！真实权重已成功保存至：{save_path}")


if __name__ == "__main__":
    train_and_save_model()