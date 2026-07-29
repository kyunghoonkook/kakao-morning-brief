# -*- coding: utf-8 -*-
"""뉴스 소스 목록. 여기만 고치면 수집 대상이 바뀝니다."""

# 전세계 주요 뉴스
WORLD_FEEDS = [
    ("BBC World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("Reuters (via Google)", "https://news.google.com/rss/search?q=when:1d+site:reuters.com&hl=en-US&gl=US&ceid=US:en"),
    ("AP (via Google)", "https://news.google.com/rss/search?q=when:1d+site:apnews.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Guardian World", "https://www.theguardian.com/world/rss"),
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
    ("NPR World", "https://feeds.npr.org/1004/rss.xml"),
    ("연합뉴스", "https://www.yna.co.kr/rss/news.xml"),
]

# AI 관련 소식
AI_FEEDS = [
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("Ars Technica AI", "https://arstechnica.com/ai/feed/"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ("MIT Tech Review AI", "https://www.technologyreview.com/topic/artificial-intelligence/feed"),
    ("Hacker News (200+)", "https://hnrss.org/frontpage?points=200"),
    ("arXiv cs.AI", "https://rss.arxiv.org/rss/cs.AI"),
    ("AI 국내 (Google)", "https://news.google.com/rss/search?q=%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5+OR+AI+when:1d&hl=ko&gl=KR&ceid=KR:ko"),
]

# 이 단어가 제목에 있으면 버립니다 (스폰서/구독 유도 글 걸러내기)
TITLE_BLOCKLIST = [
    "sponsored", "advertisement", "subscribe", "newsletter signup",
    "deals of the day", "best deals",
]
