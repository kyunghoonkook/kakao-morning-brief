# -*- coding: utf-8 -*-
"""카카오톡 '나에게 보내기'. 리프레시 토큰으로 액세스 토큰을 받아 메시지를 보냅니다."""

import os
import json

import requests

TOKEN_URL = "https://kauth.kakao.com/oauth/token"
SEND_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
TEXT_LIMIT = 200          # 카카오 text 템플릿 본문 제한
NEW_TOKEN_FILE = ".new_refresh_token"


def refresh_access_token():
    """액세스 토큰을 발급받습니다. 리프레시 토큰이 새로 나오면 파일로 남깁니다."""
    payload = {
        "grant_type": "refresh_token",
        "client_id": os.environ["KAKAO_REST_API_KEY"],
        "refresh_token": os.environ["KAKAO_REFRESH_TOKEN"],
    }
    secret = os.environ.get("KAKAO_CLIENT_SECRET")
    if secret:
        payload["client_secret"] = secret

    response = requests.post(TOKEN_URL, data=payload, timeout=15)
    if response.status_code != 200:
        try:
            error_code = response.json().get("error_code")
        except (ValueError, AttributeError):
            error_code = None

        if error_code == "KOE322":
            raise RuntimeError(
                "카카오 리프레시 토큰이 만료되었거나 폐기되었습니다 (KOE322).\n"
                "README의 '리프레시 토큰 받기'를 다시 진행하고, 새 값을 "
                "GitHub Secret KAKAO_REFRESH_TOKEN에 등록하세요."
            )
        raise RuntimeError(
            f"카카오 토큰 갱신 실패 ({response.status_code}): {response.text}\n"
            "REST API 키와 Client Secret 설정을 확인하세요."
        )

    data = response.json()
    if data.get("refresh_token"):
        with open(NEW_TOKEN_FILE, "w", encoding="utf-8") as handle:
            handle.write(data["refresh_token"])
        print("  리프레시 토큰이 갱신되었습니다 (시크릿 자동 업데이트 대상)")
    return data["access_token"]


def send_text(access_token, text, link_url, button_title="브리핑 열기"):
    """텍스트 템플릿 한 건 발송. 200자를 넘으면 잘라냅니다."""
    body = text if len(text) <= TEXT_LIMIT else text[:TEXT_LIMIT - 1] + "…"
    template = {
        "object_type": "text",
        "text": body,
        "link": {"web_url": link_url, "mobile_web_url": link_url},
        "button_title": button_title,
    }
    response = requests.post(
        SEND_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        data={"template_object": json.dumps(template, ensure_ascii=False)},
        timeout=15,
    )
    if response.status_code != 200:
        raise RuntimeError(f"카카오톡 발송 실패 ({response.status_code}): {response.text}")
    print("  카카오톡 발송 완료")


def build_message(data, page_url, date_label):
    """알림용 문구. 링크는 버튼으로 붙으니 본문에는 넣지 않습니다."""
    lines = [f"☀️ {date_label} 아침 브리핑", "", data["kakao_text"]]

    headlines = []
    for item in (data.get("world") or [])[:2]:
        headlines.append(f"· {item.get('headline', '')}")
    for item in (data.get("ai") or [])[:2]:
        headlines.append(f"· {item.get('headline', '')}")

    draft = "\n".join(lines)
    for line in headlines:
        candidate = draft + "\n" + line
        if len(candidate) > TEXT_LIMIT - 2:
            break
        draft = candidate
    return draft
