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
    # 1.  AI 算分
    toxic_score = get_toxicity_score(chat_text)
    
    # 2. 存入 SQLite 数据库 (这里假设你们主程序有 Record 这种表，根据你们实际表名修改)
    # new_record = Record(text=chat_text, score=toxic_score)
    # db.add(new_record)
    # db.commit()
    
    return {
        "status": "success",
        "chat_text": chat_text,
        "toxicity_score": toxic_score
    }