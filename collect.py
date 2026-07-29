# -*- coding: utf-8 -*-
"""RSS를 읽어 최근 기사 목록을 만듭니다. 피드 하나가 죽어도 전체는 계속 돕니다."""

import re
import sys
import html
import time
import calendar
from datetime import datetime, timedelta, timezone

import feedparser

from feeds import WORLD_FEEDS, AI_FEEDS, TITLE_BLOCKLIST

KST = timezone(timedelta(hours=9))
LOOKBACK_HOURS = 30          # 어제 아침 이후 기사만
PER_FEED_LIMIT = 12          # 피드당 최대 기사 수
TAG_RE = re.compile(r"<[^>]+>")


def _clean(text, limit=420):
    if not text:
        return ""
    text = html.unescape(TAG_RE.sub(" ", text))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def _published(entry):
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            return datetime.fromtimestamp(calendar.timegm(parsed), tz=timezone.utc)
    return None


def _norm_title(title):
    return re.sub(r"[^0-9a-z가-힣]", "", title.lower())[:60]


def _blocked(title):
    low = title.lower()
    return any(word in low for word in TITLE_BLOCKLIST)


def fetch(feed_list, label):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    items, seen = [], set()

    for source, url in feed_list:
        try:
            parsed = feedparser.parse(url, agent="kakao-morning-brief/1.0")
        except Exception as exc:                              # noqa: BLE001
            print(f"  [건너뜀] {source}: {exc}", file=sys.stderr)
            continue

        if parsed.bozo and not parsed.entries:
            print(f"  [건너뜀] {source}: 피드를 읽지 못했습니다", file=sys.stderr)
            continue

        taken = 0
        for entry in parsed.entries:
            title = _clean(entry.get("title", ""), 200)
            link = entry.get("link", "")
            if not title or not link or _blocked(title):
                continue

            when = _published(entry)
            if when and when < cutoff:
                continue

            key = _norm_title(title)
            if key in seen:
                continue
            seen.add(key)

            items.append({
                "source": source,
                "title": title,
                "url": link,
                "summary": _clean(entry.get("summary", "") or entry.get("description", "")),
                "published": when.astimezone(KST).strftime("%m-%d %H:%M") if when else "",
            })
            taken += 1
            if taken >= PER_FEED_LIMIT:
                break

        print(f"  {source}: {taken}건")
        time.sleep(0.3)

    print(f"[{label}] 총 {len(items)}건 수집")
    return items


def collect_all():
    print("세계 뉴스 수집")
    world = fetch(WORLD_FEEDS, "세계")
    print("AI 뉴스 수집")
    ai = fetch(AI_FEEDS, "AI")
    if not world and not ai:
        raise RuntimeError("모든 피드가 실패했습니다. 네트워크나 피드 주소를 확인하세요.")
    return {"world": world, "ai": ai}
