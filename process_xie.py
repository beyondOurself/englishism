# -*- coding: utf-8 -*-
import html
import re
import shutil
from pathlib import Path
from urllib.parse import unquote, urlparse

import opencc

BASE = Path(r"C:\Users\admin\Desktop\书籍\英语语法\englishism")
FILES = [
    (1, BASE / "MinerU_markdown_谢孟媛《初级语法》第一册(共3册)初级文法视频课程讲义.pdf_8a415807-3e5c-40b8-93e5-ffe45c954310.md", r"^名詞，用來表示"),
    (2, BASE / "MinerU_markdown_谢孟媛《初级语法》第二册(共3册)初级文法视频课程讲义.pdf_5c5344f6-3980-49d2-b033-3f5fba31b262.md", r"^## 比較變化"),
    (3, BASE / "MinerU_markdown_谢孟媛《初级语法》第三册(共3册)初级文法视频课程讲义.pdf_03ad6bbe-fa8a-47d1-8f1d-f19136b26478.md", r"!\[\]\(file://"),
]
OUT = {
    1: BASE / "谢孟媛初级语法-第一册.md",
    2: BASE / "谢孟媛初级语法-第二册.md",
    3: BASE / "谢孟媛初级语法-第三册.md",
}
ASSETS = BASE / "assets" / "xie"
GITEE_RAW = "https://gitee.com/shencanlong/englishism/raw/main/assets/xie"
T2S = opencc.OpenCC("t2s")
FILE_IMG_RE = re.compile(r"!\[[^\]]*\]\((file://.+?\.(?:jpg|jpeg|png|gif|webp))\)", re.I)
JUNK = [r"^\[Unreadable\]$", r"^## \[Unreadable\]$", r"^## 无法识别$", r"^## 第\d+页$"]
TOC_LINE = re.compile(r"^## Unit\d+", re.I)


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def clean_latex_inline(s: str) -> str:
    s = re.sub(r"\\(left|right)[\\{\}\\.]", "", s)
    s = re.sub(r"\\begin\{array\}\{[^}]*\}", "", s)
    s = re.sub(r"\\end\{array\}", "", s)
    s = re.sub(r"\\mathrm\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\text\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\underline\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\frac\{([^}]*)\}\{([^}]*)\}", r"\1/\2", s)
    s = re.sub(r"\\\\", " / ", s)
    s = re.sub(r"\\[a-zA-Z]+\s*", " ", s)
    s = re.sub(r"[{}]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def clean_line(line: str) -> str:
    line = html.unescape(line)
    line = re.sub(r"<eq>\s*", "", line)
    line = re.sub(r"\s*</eq>", "", line)
    line = re.sub(r"\$\s*\\times\s*\$", "", line)
    line = re.sub(r"\$\s*([^$]+?)\s*\$", lambda m: clean_latex_inline(m.group(1)), line)
    line = re.sub(r"\$\s*\\mathbf\{([^}]+)\}\s*\$", r"\1", line)
    line = line.replace("\u00a0", " ")
    line = re.sub(r"[ \t]+$", "", line)
    return line


def find_content_start(lines: list[str], marker: str) -> int:
    pat = re.compile(marker)
    for i, line in enumerate(lines):
        if pat.search(line.strip()):
            return i
    raise RuntimeError(f"content start not found: {marker}")


def clean_text(lines: list[str], content_marker: str) -> str:
    start = find_content_start(lines, content_marker)
    lines = lines[start:]
    out: list[str] = []
    prev = None
    in_txt = False
    txt_buf: list[str] = []
    seen_unit6 = False

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
                txt_buf.append(clean_line(line))
            continue
        if any(re.match(p, line.strip()) for p in JUNK):
            continue
        cl = clean_line(line)
        if cl.strip() == "## Unit6 WH問句、祈使句、感嘆句":
            if seen_unit6:
                continue
            seen_unit6 = True
        if cl.strip() == prev and cl.startswith("## "):
            continue
        out.append(cl)
        prev = cl.strip()

    text = "\n".join(out)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip() + "\n"


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
    urls = set(FILE_IMG_RE.findall(text))
    mapping: dict[str, str] = {}
    ok = 0
    for url in sorted(urls):
        src = file_url_to_path(url)
        if not src:
            print(f"MISSING {url}")
            continue
        dest = ASSETS / src.name
        if not dest.exists() or dest.stat().st_size < 200:
            shutil.copy2(src, dest)
        mapping[url] = f"{GITEE_RAW}/{src.name}"
        ok += 1
    for old, new in mapping.items():
        text = text.replace(old, new)
    print(f"images: {ok}/{len(urls)}")
    return text


def to_simplified(text: str) -> str:
    return T2S.convert(text)


def main():
    for vol, src, marker in FILES:
        lines = read_lines(src)
        text = clean_text(lines, marker)
        text = migrate_images(text)
        text = to_simplified(text)
        OUT[vol].write_text(text, encoding="utf-8")
        print(f"vol{vol}: {OUT[vol].name} ({len(text.splitlines())} lines)")


if __name__ == "__main__":
    main()
