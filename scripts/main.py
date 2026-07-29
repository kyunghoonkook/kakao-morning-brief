# -*- coding: utf-8 -*-
"""수집 → 요약 → 페이지 생성 → 카카오톡 발송."""

import os
import sys
import json
from datetime import datetime, timedelta, timezone

from collect import collect_all
from summarize import summarize
from render import render, write_pages, DOCS_DIR
import kakao

KST = timezone(timedelta(hours=9))
WEEKDAYS = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
DRY_RUN = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")


def main():
    now = datetime.now(KST)
    date_slug = now.strftime("%Y-%m-%d")
    date_label = f"{now.year}년 {now.month}월 {now.day}일 {WEEKDAYS[now.weekday()]}"

    print(f"=== {date_label} 브리핑 시작 ===")

    print("\n[1/4] 기사 수집")
    bundle = collect_all()

    print("\n[2/4] Claude로 브리핑 작성")
    data = summarize(bundle, date_label)

    print("\n[3/4] 페이지 생성")
    html = render(data, date_label, now.strftime("%H:%M"))
    write_pages(html, date_slug)
    with open(os.path.join(DOCS_DIR, f"{date_slug}.json"), "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)

    base = os.environ.get("PAGES_BASE_URL", "").rstrip("/")
    page_url = f"{base}/{date_slug}.html" if base else ""

    print("\n[4/4] 카카오톡 발송")
    message = kakao.build_message(data, page_url, date_label)
    print("---- 보낼 내용 ----")
    print(message)
    print(f"---- 링크: {page_url or '(PAGES_BASE_URL 미설정)'} ----")

    if DRY_RUN:
        print("DRY_RUN이므로 발송하지 않았습니다.")
        return
    if not page_url:
        raise RuntimeError("PAGES_BASE_URL이 설정되지 않았습니다. 카카오 링크를 만들 수 없습니다.")

    token = kakao.refresh_access_token()
    kakao.send_text(token, message, page_url)
    print("\n=== 완료 ===")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:                                   # noqa: BLE001
        print(f"\n실패: {exc}", file=sys.stderr)
        sys.exit(1)
