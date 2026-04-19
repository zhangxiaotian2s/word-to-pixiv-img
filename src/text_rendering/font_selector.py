"""
Font selector that automatically selects appropriate font based on text context/mood.

Includes several font categories for different styles:
- sans: Modern, clean, neutral (default for most cases)
- serif: Literary, traditional, elegant
- handwritten: Casual, artistic, personal
- bold: Strong, impactful, headline
- rounded: Friendly, soft, cute

Free commercial fonts are provided in the fonts/ directory.
"""

import re
from typing import Optional, Dict, List, Tuple

from src.utils.logging import logger


class FontCategory:
    """Font category with mood keywords and font paths."""

    def __init__(
        self,
        name: str,
        description: str,
        keywords: List[str],
        font_filename: str,
    ):
        self.name = name
        self.description = description
        self.keywords = [kw.lower() for kw in keywords]
        self.font_filename = font_filename


# Predefined font categories with mood matching keywords
DEFAULT_FONT_CATEGORIES = [
    FontCategory(
        name="bold",
        description="粗黑有力 - 适合标题、标语、力量感文字",
        keywords=[
            "力量", "勇气", "坚持", "奋斗", "加油", "拼搏", "梦想",
            "未来", "希望", "信念", "坚定", "霸气", "强大", "震撼",
            "口号", "标语", "标题", "封面", "斜杠", "青春", "热血",
            "bold", "power", "strong", "title", "headline",
        ],
        font_filename="zcool_hiantian_bold.ttf",
    ),
    FontCategory(
        name="serif",
        description="文艺复古 - 适合抒情、诗文、感悟",
        keywords=[
            "诗", "文", "歌", "词", "散文", "感悟", "人生", "岁月",
            "时光", "记忆", "思念", "等待", "温柔", "安静", "美好",
            "文艺", "复古", "优雅", "古典", "书香", "墨香", "情感",
            "serif", "literary", "poem", "elegant", "classic",
        ],
        font_filename="noto_serif_cjk_sc_regular.ttf",
    ),
    FontCategory(
        name="handwritten",
        description="清新手写 - 适合随笔、日记、心情、寄语",
        keywords=[
            "日记", "心情", "随笔", "手写", "寄语", "祝福", "生日快乐",
            "早安", "晚安", "你好", "再见", "情书", "告白", "温暖",
            "治愈", "清新", "自然", "简单", "朴素", "手写体", "钢笔",
            "handwritten", "note", "diary", "cursive", "warm",
        ],
        font_filename="zcool_xiaowei.ttf",
    ),
    FontCategory(
        name="rounded",
        description="可爱圆润 - 适合萌系、甜美、可爱内容",
        keywords=[
            "可爱", "萌", "甜", "少女", "猫", "狗", "宠物", "开心",
            "快乐", "糖果", "蛋糕", "奶茶", "夏天", "粉色", "甜美",
            "软萌", "治愈", "可爱风", "二次元", "动漫", "卡通",
            "rounded", "cute", "sweet", "soft", "kawaii",
        ],
        font_filename="zcool_qingke_huangyou.ttf",
    ),
    FontCategory(
        name="sans",
        description="现代干净 - 通用默认，适合大多数场景",
        keywords=[
            "现代", "干净", "简约", "简洁", "科技", "城市", "风景",
            "背景", "空间", "设计", "极简", "通用", "日常",
            "sans", "modern", "clean", "neutral", "default",
        ],
        font_filename="noto_sans_cjk_sc_regular.ttf",
    ),
]


class AutoFontSelector:
    """Automatically select the best font based on text content and mood."""

    def __init__(self, categories: List[FontCategory] = None):
        self.categories = categories or DEFAULT_FONT_CATEGORIES
        logger.info(f"AutoFontSelector initialized with {len(self.categories)} font categories")

    def analyze_mood(self, text: str) -> Tuple[FontCategory, float]:
        """Analyze text mood and return best matching font category.

        Returns:
            (best_category, confidence_score)
        """
        text_lower = text.lower()
        scores: List[Tuple[float, FontCategory]] = []

        for category in self.categories:
            score = 0
            for keyword in category.keywords:
                if keyword in text_lower:
                    # Longer keywords give more weight
                    score += len(keyword)
            scores.append((score, category))

        # Sort by score descending
        scores.sort(reverse=True, key=lambda x: x[0])

        best_score, best_category = scores[0]

        # If no specific matches, use default sans
        if best_score == 0:
            for category in self.categories:
                if category.name == "sans":
                    logger.debug(f"No specific mood detected, using default sans font for: {text[:30]}...")
                    return category, 1.0

        logger.debug(f"Mood analysis for '{text[:30]}...': {best_category.name} (score: {best_score})")
        return best_category, best_score

    def get_font_filename(self, text: str) -> str:
        """Get the best matching font filename for given text."""
        category, _ = self.analyze_mood(text)
        return category.font_filename

    def list_available_fonts(self) -> Dict[str, str]:
        """List all available fonts with descriptions."""
        return {
            cat.name: cat.description
            for cat in self.categories
        }
