import os
from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
# 引入原生算分函数
from app.ml_models.text_model import get_toxicity_score

router = APIRouter()

# 🚨 前置黑名单词库
BLACK_LIST = [
    "乡里人", "乡巴佬", "偷井盖", "南蛮", "白完", "东百",
    "小日本", "漂亮国", "弯弯", "西八"
]


@router.post("/analyze_text")
async def analyze_game_text(
        chat_text: str = Form(...),
        db: Session = Depends(get_db)
):
    try:
        # 1. 调用原生模型！拿到完整的五维数组结构
        analysis_result = get_toxicity_score(chat_text)

        # 2. 规则引擎拦截，强制覆盖五维数组里的分值
        for bad_word in BLACK_LIST:
            if bad_word in chat_text:
                print(f"🚨 [规则引擎拦截]: 检测到恶劣歧视词汇【{bad_word}】！已强行修正雷达图！")
                analysis_result["toxicity_score"] = 0.90
                analysis_result["toxic_type"] = "严重地域歧视/违规"
                # 💡 核心修复：前端要用 .join()，这里必须是【列表】而不是字符串！
                analysis_result["target_groups"] = ["特定地域群体"]
                analysis_result["expression"] = "直接恶毒攻击"
                break

        # 3. 安全提取 target_groups，确保它永远是个列表
        target_groups = analysis_result.get("target_groups", [])
        if isinstance(target_groups, str):
            target_groups = [target_groups]

        # 4. 彻底解除封印，向前端输出格式完美对齐的 JSON！
        return {
            "status": "success",
            "chat_text": chat_text,
            "toxicity_score": float(analysis_result.get("toxicity_score", 0.0)),
            "is_jargon": float(analysis_result.get("is_jargon", 0.0)),
            "toxic_type": str(analysis_result.get("toxic_type", "正常")),
            "expression": str(analysis_result.get("expression", "无")),
            "target_groups": target_groups  # 保持为列表，防止前端 .join() 崩溃！
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}