# -*- coding: utf-8 -*-
import html
import re
import shutil
from pathlib import Path
from urllib.parse import unquote, urlparse

BASE = Path(r"C:\Users\admin\Desktop\书籍\英语语法\englishism")
FILE1 = BASE / "MinerU_markdown_赖氏经典英语语法新版.pdf_ac140e98-4e36-4dd0-ae46-ba63b075b194.md"
FILE2 = BASE / "MinerU_markdown_赖氏经典英语语法新版.pdf_304efc52-3fd2-4928-b30b-7aa62fe99816.md"
FILE3 = BASE / "MinerU_markdown_赖氏经典英语语法新版.pdf_a9a286a6-8aba-44ea-accd-d5b459344a5c.md"
OUT_MERGED = BASE / "赖氏经典英语语法-合并.md"
OUT_UNITS = BASE / "lai-units"
ASSETS = BASE / "assets" / "lai"
GITEE_RAW = "https://gitee.com/shencanlong/englishism/raw/main/assets/lai"

CN_CHAPTER = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
    "十": 10, "十一": 11, "十二": 12, "十三": 13, "十四": 14,
}

CHAPTER_TITLES = {
    1: "句子的形成", 2: "两句的连接方法", 3: "关系词", 4: "非谓语动词",
    5: "助动词及易用错的动词", 6: "时态及语态", 7: "虚拟语气", 8: "副词",
    9: "倒装结构", 10: "比较结构", 11: "代词", 12: "复合形容词",
    13: "介词用法", 14: "反意疑问句",
}

CHAPTER_RE = re.compile(r"^#{1,2}\s*(第(?:十[一二三四]|十|[一二三四五六七八九])章)\s+(.+?)\s*$")
FILE_IMG_RE = re.compile(r"!\[[^\]]*\]\((file://[^\)]+)\)")
HTML_IMG_RE = re.compile(r"""<img[^>]+src=["'](file://[^"']+)["']""", re.I)
JUNK = [r"^\[Unreadable\]$", r"^## \[Unreadable\]$", r"^## 无法识别$", r"^## 第\d+页$"]


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def clean_line(line: str) -> str:
    line = html.unescape(line)
    line = re.sub(r"\$\s*\\mathbf\{([^}]+)\}\s*\$", r"\1", line)
    line = re.sub(r"\$\s*([^$]+?)\s*\$", r"\1", line)
    line = line.replace("\u00a0", " ")
    return re.sub(r"[ \t]+$", "", line)


def clean_text(text: str) -> str:
    lines = [clean_line(x) for x in text.splitlines()]
    out: list[str] = []
    prev = None
    in_txt = False
    txt_buf: list[str] = []
    seen_title = False

    for line in lines:
        if line.strip().startswith("```txt"):
            in_txt = True
            txt_buf = []
            continue
        if in_txt:
            if line.strip() == "```":
                if txt_buf:
                    if out and out[-1] != "":
                        out.append("")
                    out.extend(txt_buf)
                    out.append("")
                in_txt = False
            else:
                txt_buf.append(line)
            continue
        if any(re.match(p, line.strip()) for p in JUNK):
            continue
        if line.strip() in ("# 赖氏经典英语语法", "# 赖氏经典英语语法 新版"):
            if seen_title:
                continue
            seen_title = True
        if line.strip() == prev and line.startswith("## "):
            continue
        out.append(line)
        prev = line.strip()

    text = "\n".join(out)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip() + "\n"


def merge_sources() -> str:
    l1, l2, l3 = read_lines(FILE1), read_lines(FILE2), read_lines(FILE3)
    front = "\n".join(l1[:49])
    body1 = "\n".join(l1[581:])
    body = f"{front}\n\n---\n\n{body1}\n\n---\n\n" + "\n".join(l2) + "\n\n---\n\n" + "\n".join(l3)
    return clean_text(body)


def file_url_to_path(url: str) -> Path | None:
    parsed = urlparse(url)
    if parsed.scheme != "file":
        return None
    path = unquote(parsed.path)
    if path.startswith("/") and len(path) > 2 and path[2] == ":":
        path = path[1:]
    p = Path(path)
    return p if p.exists() else None


def migrate_images(text: str) -> str:
    ASSETS.mkdir(parents=True, exist_ok=True)
    urls = set(FILE_IMG_RE.findall(text)) | set(HTML_IMG_RE.findall(text))
    mapping: dict[str, str] = {}
    ok = 0
    for url in sorted(urls):
        src = file_url_to_path(url)
        if not src:
            print(f"MISSING {url}")
            continue
        dest_name = src.name
        dest = ASSETS / dest_name
        if not dest.exists() or dest.stat().st_size < 200:
            shutil.copy2(src, dest)
        mapping[url] = f"{GITEE_RAW}/{dest_name}"
        ok += 1
    new_text = text
    for old, new in mapping.items():
        new_text = new_text.replace(old, new)
    print(f"images: {ok}/{len(urls)}")
    return new_text


def parse_chapter(line: str) -> tuple[int, str] | None:
    m = CHAPTER_RE.match(line.strip())
    if not m:
        return None
    cn, title = m.group(1), m.group(2).strip()
    cn_key = cn.replace("第", "").replace("章", "")
    num = CN_CHAPTER.get(cn_key)
    if not num:
        return None
    return num, title


def slugify(title: str) -> str:
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "-", title.lower(), flags=re.UNICODE)
    return re.sub(r"-+", "-", s).strip("-")[:50] or "chapter"


def split_chapters(text: str) -> tuple[str, dict[int, str]]:
    lines = text.splitlines()
    starts: list[tuple[int, int, str]] = []
    for i, line in enumerate(lines):
        parsed = parse_chapter(line)
        if parsed:
            n, title = parsed
            if not starts or starts[-1][0] != n:
                starts.append((n, i, title))

    if not starts:
        raise RuntimeError("未找到章节")

    front = clean_text("\n".join(lines[: starts[0][1]]))
    chapters: dict[int, str] = {}
    for idx, (n, start, title) in enumerate(starts):
        end = starts[idx + 1][1] if idx + 1 < len(starts) else len(lines)
        chunk = clean_text("\n".join(lines[start:end]))
        chapters[n] = f"# 第{cn_chapter(n)}章 {title}\n\n{chunk}"
    return front, chapters


def cn_chapter(n: int) -> str:
    for k, v in CN_CHAPTER.items():
        if v == n:
            return k
    return str(n)


def write_units(chapters: dict[int, str]):
    OUT_UNITS.mkdir(exist_ok=True)
    toc = ["# 赖氏经典英语语法 · 章节目录", ""]
    files: list[tuple[int, str, str]] = []

    for n in sorted(chapters):
        title = CHAPTER_TITLES.get(n, cn_chapter(n))
        fname = f"chapter-{n:02d}-{slugify(title)}.md"
        files.append((n, fname, title))
        (OUT_UNITS / fname).write_text(chapters[n], encoding="utf-8")

    for i, (n, fname, title) in enumerate(files):
        nav_prev = f"[← 第{n-1}章]({files[i-1][1]})" if i else "[← 目录](00-目录.md)"
        nav_next = f"[第{n+1}章 →]({files[i+1][1]})" if i < len(files) - 1 else "[合并版 →](../赖氏经典英语语法-合并.md)"
        nav = f"{nav_prev} · [目录](00-目录.md) · {nav_next}"
        body = (OUT_UNITS / fname).read_text(encoding="utf-8")
        (OUT_UNITS / fname).write_text(f"{nav}\n\n---\n\n{body}", encoding="utf-8")
        toc.append(f"- [第{cn_chapter(n)}章 {title}]({fname})")

    (OUT_UNITS / "00-目录.md").write_text("\n".join(toc) + "\n", encoding="utf-8")


def main():
    merged = merge_sources()
    merged = migrate_images(merged)
    OUT_MERGED.write_text(merged, encoding="utf-8")

    lines = merged.splitlines()
    front, chapters = split_chapters(merged)
    write_units(chapters)

    print(f"merged: {OUT_MERGED} ({len(lines)} lines)")
    print(f"chapters: {len(chapters)} -> {OUT_UNITS}")
    for n in [1, 4, 7, 10, 14]:
        if n in chapters:
            print(f"  ch {n}: {len(chapters[n])} chars")


if __name__ == "__main__":
    main()
