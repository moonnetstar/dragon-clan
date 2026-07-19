"""旅遊助理 App 核心模組。

提供 ItineraryGenerator：根據目的地與天數生成簡易行程，
並自動將非預設目的地加入 destinations 清單。
"""
from __future__ import annotations

import datetime
import random

# 預設支援的目的地
DEFAULT_DESTINATIONS = [
    "Tokyo, Japan",
    "Osaka, Japan",
    "Seoul, Korea",
    "Bangkok, Thailand",
]

# 每個目的地可安排的活動池
ACTIVITY_POOL = {
    "Tokyo, Japan": ["淺草寺參拜", "築地市場美食", "秋葉原巡禮", "東京鐵塔夜景"],
    "Osaka, Japan": ["大阪城遊覽", "道頓堀小吃", "環球影城", "黑門市場"],
    "Seoul, Korea": ["景福宮", "明洞購物", "漢江公園野餐", "南山塔"],
    "Bangkok, Thailand": ["大皇宮", "恰圖恰週末市集", "昭披耶河遊船", "四面佛"],
}


class ItineraryGenerator:
    """生成旅遊行程的核心類別。"""

    def __init__(self) -> None:
        self.destinations: list[str] = list(DEFAULT_DESTINATIONS)

    def add_destination(self, destination: str) -> None:
        """將新目的地加入清單（若尚未存在）。"""
        if destination and destination not in self.destinations:
            self.destinations.append(destination)

    def generate(self, destination: str, duration_days: int) -> dict:
        """生成行程。

        Args:
            destination: 目的地名稱。
            duration_days: 行程天數（必須為正整數）。

        Returns:
            包含 destination, duration_days, activities, generated_at 的 dict。
        """
        if not destination:
            raise ValueError("destination 不可為空")
        if duration_days <= 0:
            raise ValueError("duration_days 必須為正整數")

        # 非預設目的地自動加入
        self.add_destination(destination)

        pool = ACTIVITY_POOL.get(
            destination,
            ["城市觀光", "在地美食", "文化體驗", "自由活動"],
        )
        activities = []
        for day in range(1, duration_days + 1):
            activity = random.choice(pool)
            activities.append({"day": day, "activity": activity})

        return {
            "destination": destination,
            "duration_days": duration_days,
            "activities": activities,
            "generated_at": datetime.datetime.now().isoformat(),
        }


if __name__ == "__main__":
    gen = ItineraryGenerator()
    result = gen.generate("Taipei, Taiwan", 3)
    print(f"行程已生成：{result['destination']} / {result['duration_days']} 天")
    print(f"已自動加入目的地：{'Taipei, Taiwan' in gen.destinations}")
    for item in result["activities"]:
        print(f"  第 {item['day']} 天：{item['activity']}")
