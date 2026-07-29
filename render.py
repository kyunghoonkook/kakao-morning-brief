# -*- coding: utf-8 -*-
"""브리핑 JSON을 읽기용 HTML 페이지로 만듭니다."""

import os
from html import escape

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")

CSS = """
:root{
  --paper:#EDEFF2; --card:#F6F7F9; --ink:#16181D; --soft:#59606A;
  --rule:#D2D7DE; --accent:#1F5C5A; --aside:#E2E8E7;
}
@media (prefers-color-scheme:dark){
  :root{
    --paper:#13161A; --card:#191D22; --ink:#E6E9EC; --soft:#98A1AA;
    --rule:#2A3037; --accent:#7FC6BC; --aside:#1A2124;
  }
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",Pretendard,
    "Malgun Gothic","Noto Sans KR",sans-serif;
  font-size:17px; line-height:1.72; letter-spacing:-.01em;
  word-break:keep-all; overflow-wrap:break-word;
}
.wrap{max-width:44rem; margin:0 auto; padding:3.5rem 1.5rem 6rem}
.mono{
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  font-size:.68rem; letter-spacing:.16em; text-transform:uppercase;
}
.stamp{display:flex; justify-content:space-between; gap:1rem;
  color:var(--soft); padding-bottom:.6rem; border-bottom:1px solid var(--ink)}
.lede{
  font-size:clamp(1.55rem,5.2vw,2.15rem); font-weight:750; line-height:1.42;
  letter-spacing:-.03em; margin:1.8rem 0 0;
}
h2{
  display:flex; align-items:baseline; gap:.75rem; margin:4rem 0 0;
  padding-bottom:.5rem; border-bottom:1px solid var(--rule);
  font-size:1.02rem; font-weight:700; letter-spacing:-.01em;
}
h2 .note{color:var(--soft); font-weight:400; margin-left:auto}
.item{display:grid; grid-template-columns:2.6rem 1fr; gap:0 .9rem;
  padding:2rem 0; border-bottom:1px solid var(--rule)}
.rank{grid-row:1/span 4; color:var(--accent); padding-top:.45rem}
.headline{margin:0; font-size:1.16rem; font-weight:700; line-height:1.5; letter-spacing:-.02em}
.body{margin:.55rem 0 0; color:var(--ink)}
.why{
  margin:1rem 0 0; padding:.85rem 1rem; background:var(--aside);
  border-left:2px solid var(--accent); border-radius:0 3px 3px 0;
}
.why .mono{display:block; color:var(--accent); margin-bottom:.3rem}
.why p{margin:0; color:var(--ink)}
.src{margin:.8rem 0 0}
.src a{color:var(--soft); text-decoration:none; border-bottom:1px solid var(--rule)}
.src a:hover,.src a:focus{color:var(--accent); border-color:var(--accent)}
a:focus-visible{outline:2px solid var(--accent); outline-offset:3px}
ul.quick{list-style:none; margin:1.4rem 0 0; padding:0}
ul.quick li{position:relative; padding:.4rem 0 .4rem 1.1rem; color:var(--soft)}
ul.quick li::before{content:"—"; position:absolute; left:0; color:var(--accent)}
footer{margin-top:4rem; padding-top:1rem; border-top:1px solid var(--rule); color:var(--soft)}
@media (max-width:34rem){
  .wrap{padding:2.5rem 1.15rem 4rem}
  .item{grid-template-columns:1fr; gap:0}
  .rank{grid-row:auto; padding:0 0 .45rem}
}
"""


def _item_html(index, item):
    headline = escape(item.get("headline", ""))
    summary = escape(item.get("summary", ""))
    why = escape(item.get("why", ""))
    source = escape(item.get("source", "출처"))
    url = escape(item.get("url", ""), quote=True)
    link = (f'<p class="src"><a href="{url}" target="_blank" rel="noopener noreferrer">'
            f'{source}에서 원문 보기</a></p>') if url.startswith("http") else ""
    return f"""      <article class="item">
        <div class="rank mono">{index:02d}</div>
        <h3 class="headline">{headline}</h3>
        <p class="body">{summary}</p>
        <div class="why"><span class="mono">왜 중요한가</span><p>{why}</p></div>
        {link}
      </article>"""


def _section(title, note, items):
    if not items:
        return ""
    body = "\n".join(_item_html(i, it) for i, it in enumerate(items, 1))
    return f"""      <h2>{escape(title)}<span class="note mono">{escape(note)}</span></h2>
{body}"""


def render(data, date_label, generated_at):
    world = _section("전세계", f"중요도 순 · {len(data.get('world', []))}건", data.get("world", []))
    ai = _section("AI", f"중요도 순 · {len(data.get('ai', []))}건", data.get("ai", []))

    quick = data.get("quick") or []
    quick_html = ""
    if quick:
        rows = "\n".join(f"        <li>{escape(str(q))}</li>" for q in quick)
        quick_html = f"""      <h2>한 줄로<span class="note mono">넘겨도 되는 소식</span></h2>
      <ul class="quick">
{rows}
      </ul>"""

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{escape(date_label)} 아침 브리핑</title>
<style>{CSS}</style>
</head>
<body>
  <main class="wrap">
    <div class="stamp mono"><span>아침 브리핑</span><span>{escape(date_label)}</span></div>
    <p class="lede">{escape(data.get('lede', ''))}</p>
{world}
{ai}
{quick_html}
    <footer class="mono">{escape(generated_at)} KST 생성 · 기사 요약은 AI가 작성했습니다. 중요한 판단은 원문을 확인하세요.</footer>
  </main>
</body>
</html>
"""


def write_pages(html, date_slug):
    os.makedirs(DOCS_DIR, exist_ok=True)
    dated = os.path.join(DOCS_DIR, f"{date_slug}.html")
    latest = os.path.join(DOCS_DIR, "index.html")
    for path in (dated, latest):
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(html)
    print(f"  {dated} / {latest} 작성")
    return dated
