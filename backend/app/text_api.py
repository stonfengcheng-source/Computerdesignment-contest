from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
# 引入算分函数
from app.ml_models.text_model import get_toxicity_score

# 创建专属路由，绝不和队友的代码搅合在一起
router = APIRouter()

@router.post("/analyze_text")
async def analyze_game_text(
    chat_text: str = Form(...),
    db: Session = Depends(get_db) # 【使用自带的 sqlite】
):
    # 1. AI 全维度算分 (现在返回的是包含了 5 个维度的字典)
    analysis_result = get_toxicity_score(chat_text)
    
    # 2. 存入 SQLite 数据库 (这里假设你们主程序有 Record 这种表，根据你们实际表名修改)
    # new_record = Record(text=chat_text, score=analysis_result["toxicity_score"])
    # db.add(new_record)
    # db.commit()
    
    # 3. 彻底解除封印，向前端输出完整的五维分析报告！
    return {
        "status": "success",
        "chat_text": chat_text,
        "toxicity_score": analysis_result["toxicity_score"],
        "is_jargon": analysis_result["is_jargon"],
        "toxic_type": analysis_result["toxic_type"],
        "expression": analysis_result["expression"],
        "target_groups": analysis_result["target_groups"]
    }