#!/usr/bin/env python3
"""Build the site into public/.  Usage: python3 build.py"""
import html, re, shutil
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
OUT = ROOT / "public"
NAME, SUBTITLE = "Luke", "writing + music"   # <- edit me

esc = html.escape

def safe_url(url):
    """Only allow https:// and mailto: links (blocks javascript:, data:, http:, etc.)."""
    url = url.strip()
    if urlparse(url).scheme not in ("https", "mailto"):
        raise SystemExit(f"Refusing unsafe link: {url!r}")
    return esc(url, quote=True)

def page(title, body):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{esc(title)}</title>
<link rel="stylesheet" href="/style.css">
</head><body>
{body}
</body></html>"""

def ext_link(label, url):
    return f'<a href="{safe_url(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'

def inline(text):
    """Escape text, then allow *italic* and [label](https://url)."""
    t = esc(text)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: ext_link(html.unescape(m[1]), html.unescape(m[2])), t)
    return re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)

def load_posts():
    posts = []
    for f in sorted((ROOT / "writings").glob("*.md"), reverse=True):
        date, slug = f.stem[:10], f.stem[11:]          # 2026-11-08-my-title.md
        lines = f.read_text(encoding="utf-8").strip().splitlines()
        title = lines[0].lstrip("# ").strip()
        paras = "\n".join(lines[1:]).strip().split("\n\n")
        body = "\n".join(f"<p>{inline(p).replace(chr(10), '<br>')}</p>" for p in paras if p.strip())
        posts.append(dict(date=date, slug=slug, title=title, body=body))
    return posts

def main():
    shutil.rmtree(OUT, ignore_errors=True)
    (OUT / "writings").mkdir(parents=True)
    shutil.copy(ROOT / "static/style.css", OUT / "style.css")

    links = [l.split("|", 1) for l in (ROOT / "links.txt").read_text(encoding="utf-8").splitlines()
             if "|" in l and not l.startswith("#")]
    posts = load_posts()
    art = esc((ROOT / "art.txt").read_text(encoding="utf-8"))

    items = '<li><a href="/writings/">writings</a></li>\n' + "\n".join(
        f"<li>{ext_link(label.strip(), url)}</li>" for label, url in links)
    (OUT / "index.html").write_text(page(NAME, f"""
<p><b>{esc(NAME)}</b><br>{esc(SUBTITLE)}</p><hr>
<ul>{items}</ul><hr>
<pre aria-hidden="true">{art}</pre>"""), encoding="utf-8")

    listing = "\n".join(f'<li><span class="d">{p["date"]}</span> <a href="/writings/{p["slug"]}.html">{esc(p["title"])}</a></li>' for p in posts)
    (OUT / "writings/index.html").write_text(page(f"Writings | {NAME}",
        f'<p><a href="/">&larr; home</a></p><hr><h1>writings</h1><ul>{listing}</ul>'), encoding="utf-8")

    for p in posts:
        (OUT / f"writings/{p['slug']}.html").write_text(page(f"{p['title']} | {NAME}",
            f'<p><a href="/writings/">&larr; writings</a></p><hr><h1>{esc(p["title"])}</h1>'
            f'<p class="d">{p["date"]}</p>\n{p["body"]}'), encoding="utf-8")
    print(f"Built {len(posts)} writing(s) into {OUT}")

if __name__ == "__main__":
    main()
