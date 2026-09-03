# 아침 브리핑 → 카카오톡

매일 아침 9시(KST)에 전세계 주요 뉴스와 AI 소식을 모아 해설까지 붙인 브리핑을 만들고,
카카오톡 "나에게 보내기"로 알림을 보냅니다.

```
GitHub Actions cron (00:00 UTC = 09:00 KST)
   └─ RSS 15개 수집 (Reuters·AP·BBC·Guardian·연합 / TechCrunch·Verge·Ars·arXiv 등)
       └─ Claude API로 한국어 브리핑 작성 (세계 5건 + AI 5건 + 한 줄 소식)
           └─ GitHub Pages에 읽기용 페이지 발행
               └─ 카카오톡으로 요약 + 링크 버튼 발송
```

카카오톡 텍스트 메시지는 200자 제한이 있어서, 톡으로는 요약과 헤드라인만 오고
전문은 버튼을 눌러 페이지에서 봅니다.

---

## 1. 저장소 만들기

GitHub에 새 저장소를 만들고 이 폴더의 파일을 그대로 올립니다. (공개 저장소면 Actions가 무료입니다.)

```bash
git init
git add .
git commit -m "아침 브리핑 루틴"
git branch -M main
git remote add origin https://github.com/<사용자명>/<저장소명>.git
git push -u origin main
```

## 2. GitHub Pages 켜기

**Settings → Pages** → Source를 `Deploy from a branch`, 브랜치 `main`, 폴더 `/docs`로 지정합니다.

발행 주소는 `https://<사용자명>.github.io/<저장소명>` 입니다. 이 주소를 적어두세요.

## 3. 카카오 개발자 앱 설정

[developers.kakao.com](https://developers.kakao.com) → **내 애플리케이션 → 애플리케이션 추가**

| 위치 | 할 일 |
|---|---|
| 앱 키 | **REST API 키** 복사 |
| 플랫폼 → Web | 사이트 도메인에 `https://<사용자명>.github.io` 등록 |
| 카카오 로그인 | 활성화 **ON** |
| 카카오 로그인 → Redirect URI | `https://<사용자명>.github.io/<저장소명>/` 등록 |
| 카카오 로그인 → 동의항목 | **카카오톡 메시지 전송(`talk_message`)** 을 "이용 중 동의"로 설정 |
| 보안 (선택) | Client Secret을 쓰면 그 값도 복사 |

> 사이트 도메인을 등록하지 않으면 메시지는 가지만 **링크 버튼이 동작하지 않습니다.**
> `talk_message` 동의항목을 켜지 않으면 `insufficient scopes` (code -402) 오류가 납니다.

## 4. 리프레시 토큰 받기 (처음 또는 만료 시)

```bash
pip install -r requirements.txt

# ① 동의 주소 만들기
python scripts/get_token.py <REST_API_키> https://<사용자명>.github.io/<저장소명>/

# ② 출력된 주소를 브라우저에서 열고 동의 → 이동된 주소의 ?code=... 값 복사

# ③ 토큰 교환
python scripts/get_token.py <REST_API_키> https://<사용자명>.github.io/<저장소명>/ <복사한코드>
```

출력된 `KAKAO_REFRESH_TOKEN`을 GitHub Secret에 저장합니다. 인가 코드는 몇 분 안에 만료되니 바로 ③을 실행하세요.

## 5. 시크릿과 변수 등록

**Settings → Secrets and variables → Actions**

Secrets 탭:

| 이름 | 값 |
|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com)에서 발급 |
| `KAKAO_REST_API_KEY` | 3단계에서 복사한 REST API 키 |
| `KAKAO_REFRESH_TOKEN` | 4단계 결과 |
| `KAKAO_CLIENT_SECRET` | Client Secret을 켰을 때만 |
| `GH_PAT` | 필수. 카카오 리프레시 토큰 자동 갱신용 (아래 참고) |

Variables 탭:

| 이름 | 값 |
|---|---|
| `PAGES_BASE_URL` | `https://<사용자명>.github.io/<저장소명>` |
| `BRIEF_MODEL` | 선택. 기본 `claude-sonnet-5`, 더 깊은 해설은 `claude-opus-5` |

## 6. 테스트

**Actions → 아침 브리핑 → Run workflow** → `dry_run`을 체크하고 실행하면
카카오톡 발송 없이 브리핑 내용과 보낼 문구를 로그에서 확인할 수 있습니다.

문제가 없으면 체크를 풀고 한 번 더 실행해 실제 발송을 확인하세요.
그 다음부터는 매일 아침 알아서 옵니다.

---

## 시간에 대해

`cron: "0 0 * * *"` 은 00:00 UTC = 09:00 KST입니다.
다만 GitHub의 예약 실행은 혼잡할 때 **몇 분에서 수십 분까지 늦을 수 있습니다.**
9시에 정확히 받아야 한다면 `cron`을 `"40 23 * * *"`(08:40 KST)로 당겨두는 편이 낫습니다.

## 리프레시 토큰 만료

카카오 리프레시 토큰은 약 2개월짜리입니다. 만료가 한 달 안으로 들어오면 갱신 요청 때 새 토큰이 발급되고 기존 토큰은 폐기됩니다.
따라서 `GH_PAT`(저장소의 Secrets 쓰기 권한을 가진 Fine-grained PAT)를 반드시 등록해야 합니다.
워크플로는 새 토큰을 받는 즉시 `KAKAO_REFRESH_TOKEN` 시크릿을 자동으로 교체합니다.

`GH_PAT`가 없으면 실제 발송 실행은 토큰 갱신 전에 중단됩니다. 이미 `KOE322`가 발생했다면 4단계를 다시 진행해
`KAKAO_REFRESH_TOKEN`을 교체하고 `GH_PAT`도 등록한 다음, Actions에서 `dry_run`을 끄고 새 워크플로를 실행하세요.

## 바꾸고 싶을 때

| 원하는 것 | 고칠 곳 |
|---|---|
| 뉴스 소스 추가·삭제 | `scripts/feeds.py` |
| 뉴스 개수 | 워크플로 env에 `WORLD_COUNT`, `AI_COUNT` 추가 |
| 문체·구성 | `scripts/summarize.py`의 `SYSTEM`, `SCHEMA` |
| 페이지 디자인 | `scripts/render.py`의 `CSS` |
| 톡 메시지 문구 | `scripts/kakao.py`의 `build_message` |
| 수집 기간 | `scripts/collect.py`의 `LOOKBACK_HOURS` |

## 문제 해결

| 증상 | 원인 |
|---|---|
| `insufficient scopes` (-402) | 동의항목에서 `talk_message` 미설정, 또는 동의를 다시 받아야 함 |
| 토큰 갱신 400 / `KOE322` | 리프레시 토큰 만료 또는 폐기 → 4단계 재실행 |
| 메시지는 오는데 버튼이 안 열림 | 플랫폼 → Web 사이트 도메인 미등록 |
| 페이지가 404 | Pages 설정이 `/docs`인지 확인, 첫 커밋 후 1~2분 대기 |
| 피드 일부 실패 | 정상 동작입니다. 실패한 피드는 건너뛰고 나머지로 브리핑을 만듭니다 |
| 비용 | 하루 한 번 호출이라 크지 않습니다. 실제 사용량은 Anthropic 콘솔에서 확인하세요 |

## 참고

- 브리핑 본문은 AI가 쓴 요약입니다. 투자·업무 판단은 원문을 확인하세요.
- 수집한 기사 본문에 지시문처럼 보이는 문장이 있어도 내용의 일부로만 취급하도록 프롬프트에 명시해 두었습니다.
- 카카오 "나에게 보내기"는 본인에게만 발송됩니다. 다른 사람에게 보내려면 친구 목록 권한 심사가 필요합니다.
