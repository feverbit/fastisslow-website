#!/usr/bin/env python3
"""静态官网自检：正文量、应用名可检索性、链接与锚点完整性。

仅依赖标准库，可在仓库根目录直接运行：

    python3 tools/check-site.py

验收口径（对应 ValueInvestment-iOS#18 的验收标准）：
- 每个页面 <main> 内的可见文本（去除所有空白）≥ 800 字符；
- 每个页面 <title>、页头品牌名、<main> 首段都出现「快即是慢」；
- 每个页面都有版权声明（© 2026 feverbit）与联系方式入口；
- 站内相对链接、图片、样式表与锚点均可解析。
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent.parent
BRAND = "快即是慢"
MIN_CHARS = 800

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}
SKIP_TEXT = {"script", "style", "head", "title"}


def visible_text(html: str, *, inner_only: str | None = None) -> str:
    """提取可见文本；inner_only 给定时只取该标签内部的文本。"""
    parts: list[str] = []
    depth = 0
    skip_depth = 0
    capturing = inner_only is None
    for token in re.finditer(r"<[^>]+>|[^<]+", html):
        chunk = token.group(0)
        if chunk.startswith("<"):
            m = re.match(r"</?\s*([a-zA-Z0-9]+)", chunk)
            if not m:
                continue
            tag = m.group(1).lower()
            closing = chunk.startswith("</")
            if inner_only and tag == inner_only:
                capturing = closing
                continue
            if tag in SKIP_TEXT:
                skip_depth = max(0, skip_depth - 1) if closing else skip_depth + 1
                continue
            if tag in VOID:
                continue
            depth += -1 if closing else 1
            continue
        if skip_depth or not capturing:
            continue
        parts.append(chunk)
    return re.sub(r"\s+", "", "".join(parts))


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[dict[str, str]] = []
        self.ids: set[str] = set()
        self._in_main = 0
        self._main_started = False
        self.main_text: list[str] = []

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if "id" in attr:
            self.ids.add(attr["id"])
        for key in ("href", "src"):
            if key in attr:
                self.links.append({"tag": tag, key: attr[key]})
        if tag == "main":
            self._in_main += 1
            self._main_started = True
        if tag in SKIP_TEXT:
            self._in_main += 0

    def handle_endtag(self, tag):
        if tag == "main" and self._in_main:
            self._in_main -= 1

    def handle_data(self, data):
        if self._in_main:
            self.main_text.append(data)


def main() -> int:
    pages = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)
    if not pages:
        print("没有找到任何 HTML 页面")
        return 1

    anchors_by_file: dict[Path, set[str]] = {}
    parsed: dict[Path, LinkParser] = {}
    for page in pages:
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8"))
        parsed[page] = parser
        anchors_by_file[page] = parser.ids

    errors: list[str] = []
    print(f"{'页面':<24}{'正文':>8}  {'标题':<6}{'页头':<6}{'首段':<6}")
    for page in pages:
        rel = page.relative_to(ROOT).as_posix()
        html = page.read_text(encoding="utf-8")
        parser = parsed[page]

        main_chars = len(re.sub(r"\s+", "", "".join(parser.main_text)))
        title = re.search(r"<title>(.*?)</title>", html, re.S)
        title_ok = bool(title and BRAND in title.group(1))
        header = re.search(r"<header.*?</header>", html, re.S)
        header_ok = bool(header and BRAND in header.group(0))
        first_para = re.search(r"<main[^>]*>.*?(<p[^>]*>.*?</p>)", html, re.S)
        first_ok = bool(first_para and BRAND in first_para.group(1))
        body = visible_text(html, inner_only="main")

        print(f"{rel:<24}{main_chars:>8}  {title_ok!s:<6}{header_ok!s:<6}{first_ok!s:<6}")

        if main_chars < MIN_CHARS:
            errors.append(f"{rel}: <main> 正文仅 {main_chars} 字符，低于 {MIN_CHARS}")
        if not title_ok:
            errors.append(f"{rel}: <title> 缺少应用名「{BRAND}」")
        if not header_ok:
            errors.append(f"{rel}: 页头缺少应用名「{BRAND}」")
        if not first_ok:
            errors.append(f"{rel}: <main> 首段尚未出现应用名「{BRAND}」")
        if "© 2026 feverbit" not in html:
            errors.append(f"{rel}: 缺少版权声明「© 2026 feverbit」")
        if not re.search(r'href="[^"]*contact\.html"', html):
            errors.append(f"{rel}: 缺少联系方式页链接")
        if "网站备案" not in body:
            errors.append(f"{rel}: 正文/页脚缺少备案说明")

    checked = 0
    for page in pages:
        rel = page.relative_to(ROOT).as_posix()
        for link in parsed[page].links:
            raw = (link.get("href") or link.get("src") or "").strip()
            if not raw or raw.startswith(("http://", "https://", "mailto:", "tel:", "data:", "javascript:")):
                continue
            target, _, fragment = raw.partition("#")
            target = unquote(target.split("?")[0])
            dest = page if not target else (page.parent / target).resolve()
            checked += 1
            if dest.is_dir():
                dest = dest / "index.html"
            if not dest.exists():
                errors.append(f"{rel}: 指向不存在的文件 {raw}")
                continue
            if fragment and dest.suffix == ".html":
                ids = anchors_by_file.get(dest)
                if ids is None:
                    other = LinkParser()
                    other.feed(dest.read_text(encoding="utf-8"))
                    ids = anchors_by_file[dest] = other.ids
                if fragment not in ids:
                    errors.append(f"{rel}: 锚点不存在 {raw}")

    print(f"\n共检查 {len(pages)} 个页面、{checked} 处站内链接/资源引用。")
    if errors:
        print("\n未通过：")
        for err in errors:
            print(" - " + err)
        return 1
    print("全部通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
