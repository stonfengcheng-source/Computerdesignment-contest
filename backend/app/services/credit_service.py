# backend/app/services/credit_service.py
import random
import asyncio


async def fetch_platform_data(platform_name: str, player_id: str):
    """
    模拟去各平台开放API/爬虫抓取玩家历史违规行为。
    实际开发中，这里会调用 Requests 爬取特定平台战绩。
    """
    await asyncio.sleep(0.5)  # 模拟网络延迟

    # 模拟返回平台的负面行为特征 (0-1，越低越好)
    return {
        "platform": platform_name,
        "afk_rate": random.uniform(0, 0.15),  # 挂机率
        "report_rate": random.uniform(0, 0.2),  # 被举报率
        "toxic_words_freq": random.uniform(0, 0.3)  # 脏话黑话频率
    }


async def generate_cross_platform_credit(player_id: str):
    """
    跨平台总信用分评估计算
    """
    platforms = ["DOTA2", "LeagueOfLegends", "HonorOfKings"]

    # 1. 并发获取多平台数据
    tasks = [fetch_platform_data(p, player_id) for p in platforms]
    platform_results = await asyncio.gather(*tasks)

    # 2. 跨平台信用分计算规则 (满分100，根据违规率扣分)
    base_score = 100.0
    total_penalty = 0
    radar_data = {
        "game_attitude": 100,  # 游戏态度 (受挂机影响)
        "social_friendly": 100,  # 社交友好度 (受词汇影响)
        "team_coop": 100,  # 团队协作 (受举报率影响)
    }

    valid_platforms = 0
    for res in platform_results:
        valid_platforms += 1
        # 计算单平台扣分
        radar_data["game_attitude"] -= res["afk_rate"] * 100
        radar_data["social_friendly"] -= res["toxic_words_freq"] * 100
        radar_data["team_coop"] -= res["report_rate"] * 100

        total_penalty += (res["afk_rate"] * 30 + res["report_rate"] * 40 + res["toxic_words_freq"] * 30)

    # 归一化平均
    final_score = base_score - (total_penalty / valid_platforms)
    radar_data = {k: max(0, int(v / valid_platforms)) for k, v in radar_data.items()}

    return {
        "player_id": player_id,
        "cross_platform_credit_score": round(final_score, 1),
        "credit_level": "优秀" if final_score > 85 else ("良好" if final_score > 70 else "极差"),
        "radar_chart": radar_data,
        "platform_details": platform_results
    }