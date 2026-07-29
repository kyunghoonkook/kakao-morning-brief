# -*- coding: utf-8 -*-
"""처음 한 번만 실행. 카카오 인가 코드를 리프레시 토큰으로 바꿔줍니다.

사용법:
    python get_token.py <REST_API_KEY> <REDIRECT_URI> <인가코드> [CLIENT_SECRET]
"""

import sys
import json
import urllib.parse

import requests

AUTH = "https://kauth.kakao.com/oauth/authorize"
TOKEN = "https://kauth.kakao.com/oauth/token"


def print_auth_url(key, redirect_uri):
    query = urllib.parse.urlencode({
        "client_id": key,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "talk_message",
    })
    print("1) 아래 주소를 브라우저에서 열고 동의하세요:\n")
    print(f"   {AUTH}?{query}\n")
    print("2) 이동된 주소창의 ?code=... 값을 복사해 다시 실행하세요:\n")
    print(f"   python get_token.py {key} {redirect_uri} <복사한코드>")


def exchange(key, redirect_uri, code, secret=None):
    payload = {
        "grant_type": "authorization_code",
        "client_id": key,
        "redirect_uri": redirect_uri,
        "code": code,
    }
    if secret:
        payload["client_secret"] = secret

    response = requests.post(TOKEN, data=payload, timeout=15)
    data = response.json()
    if response.status_code != 200:
        print(f"실패 ({response.status_code}): {json.dumps(data, ensure_ascii=False, indent=2)}")
        sys.exit(1)

    print("\n성공했습니다. 아래 값을 GitHub 시크릿에 넣으세요.\n")
    print(f"  KAKAO_REFRESH_TOKEN = {data['refresh_token']}")
    print(f"\n  (액세스 토큰은 {data.get('expires_in')}초 후 만료되므로 저장하지 않아도 됩니다.)")
    print(f"  (리프레시 토큰 유효기간: {data.get('refresh_token_expires_in')}초)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        print_auth_url(args[0], args[1])
    elif len(args) in (3, 4):
        exchange(args[0], args[1], args[2], args[3] if len(args) == 4 else None)
    else:
        print(__doc__)
        print("먼저 인자 2개(REST_API_KEY, REDIRECT_URI)로 실행해 동의 주소를 받으세요.")
