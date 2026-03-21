# backend/app/services/credit_service.py
import random
import asyncio
from sqlalchemy.orm import Session
from app.models.behavior_model import CreditReportRecord

async def generate_cross_platform_credit(player_id: str, db: Session):
    """
    跨平台总信用分评估计算：结合实时抓取数据与本地历史报告记录
    """
    platforms = ["DOTA2", "LeagueOfLegends", "HonorOfKings"]
    tasks = [fetch_platform_data(p, player_id) for p in platforms]
    platform_results = await asyncio.gather(*tasks)

    base_score = 100.0
    total_penalty = 0
    radar_data = {"game_attitude": 100, "social_friendly": 100, "team_coop": 100}

    for res in platform_results:
        radar_data["game_attitude"] -= res["afk_rate"] * 100
        radar_data["social_friendly"] -= res["toxic_words_freq"] * 100
        radar_data["team_coop"] -= res["report_rate"] * 100
        total_penalty += (res["afk_rate"] * 30 + res["report_rate"] * 40 + res["toxic_words_freq"] * 30)

    # 计算当前实时得分
    realtime_score = base_score - (total_penalty / len(platforms))

    # --- 新增：引入历史报告权重 ---
    history_records = db.query(CreditReportRecord).filter(CreditReportRecord.player_id == player_id).all()
    if history_records:
        # 计算历史信用分的平均值
        avg_history_score = sum(r.final_credit_score for r in history_records) / len(history_records)
        # 实时表现占70%，历史信用占30%
        final_score = (realtime_score * 0.7) + (avg_history_score * 0.3)
    else:
        final_score = realtime_score

    radar_data = {k: max(0, int(v / len(platforms))) for k, v in radar_data.items()}

    return {
        "player_id": player_id,
        "cross_platform_credit_score": round(final_score, 1),
        "history_count": len(history_records), # 返回历史报告数量
        "credit_level": "优秀" if final_score > 85 else ("良好" if final_score > 70 else "极差"),
        "radar_chart": radar_data,
        "platform_details": platform_results
    }