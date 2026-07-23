# -*- coding: utf-8 -*-
import re
from pathlib import Path

BASE = Path(r"C:\Users\admin\Desktop\书籍\英语语法\englishism")
OUT = BASE / "xie-units"
BOOKS = {
    1: BASE / "谢孟媛初级语法-第一册.md",
    2: BASE / "谢孟媛初级语法-第二册.md",
    3: BASE / "谢孟媛初级语法-第三册.md",
}

UNITS = {
    1: [
        (1, "名词、冠词", None),
        (2, "be 动词 一般动词的现在式", r"^## be动词的现在式"),
        (3, "be 动词 一般动词的过去式", r"^## be动词的过去式"),
        (4, "代名词", r"^## 1\.人称代名词"),
        (5, "时态", r"^## 现代简单式"),
        (6, "WH问句、祈使句、感叹句", r"^## Unit6 WH问句"),
    ],
    2: [
        (1, "比较", r"^## 比较变化"),
        (2, "不定词(to V)", r"^## 不定词$"),
        (3, "动名词", r"^## 动名词$"),
        (4, "分词", r"^## 分词$"),
        (5, "形容词", r"^## 形容词$"),
        (6, "副词", r"^## 副词$"),
        (7, "动词", r"^动词$"),
    ],
    3: [
        (1, "现在完成式", None),
        (2, "附加问句", r"^## 附加问句的形式"),
        (3, "被动语态", r"^## 主动及被动"),
        (4, "关系代名词", r"^关系代名词的功用"),
        (5, "间接问句", r"^## 直接问句及间接问句"),
        (6, "连接词", r"^## 连接词的功能"),
        (7, "介系词", r"^## 介系词的功能"),
    ],
}

FNAME_OVERRIDE = {
    (2, 2): "b2-u2-Unit2-不定词-to-V.md",
    (1, 6): "b1-u6-Unit6-WH问句-祈使句-感叹句.md",
}


def slug(s: str) -> str:
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "-", s.strip())
    return re.sub(r"-+", "-", s).strip("-")[:60]


def unit_fname(book: int, num: int, title: str) -> str:
    key = (book, num)
    if key in FNAME_OVERRIDE:
        return FNAME_OVERRIDE[key]
    return f"b{book}-u{num}-Unit{num}-{slug(title)}.md"


def find_start(lines: list[str], pattern: str | None) -> int:
    if pattern is None:
        return 0
    pat = re.compile(pattern)
    for i, line in enumerate(lines):
        if pat.search(line.strip()):
            return i
    raise RuntimeError(f"start not found: {pattern}")


def split_units(book: int, lines: list[str]) -> list[tuple[int, str, str, list[str]]]:
    specs = UNITS[book]
    starts = [(n, title, find_start(lines, pat)) for n, title, pat in specs]
    out = []
    for idx, (num, title, start) in enumerate(starts):
        end = starts[idx + 1][2] if idx + 1 < len(starts) else len(lines)
        out.append((num, title, lines[start:end]))
    return out


def anchor_id(prefix: str, heading: str) -> str:
    h = re.sub(r"^#+\s*", "", heading).strip()
    h = re.sub(r"^[（(]\d+[）)]\s*", "", h)
    return f"{prefix}-{slug(h)}"


def inject_anchors(prefix: str, chunk: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    toc: list[tuple[str, str]] = []
    out: list[str] = []
    unit_pat = re.compile(r"^## Unit\d+", re.I)
    for line in chunk:
        m = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
        if m and not unit_pat.match(line.strip()):
            level, text = len(m.group(1)), m.group(2).strip()
            if level <= 2:
                aid = anchor_id(prefix, text)
                toc.append((text, aid))
                out.append(f'<a id="{aid}"></a>\n')
        out.append(line)
    return out, toc


def build_unit_body(book: int, num: int, title: str, chunk: list[str]) -> tuple[str, list[tuple[str, str]]]:
    prefix = f"b{book}-u{num}"
    unit_title = f"Unit{num} {title}"
    body, toc = inject_anchors(prefix, chunk)
    has_unit_header = any(re.match(rf"^## Unit{num}\b", ln.strip(), re.I) for ln in chunk)
    parts = [f'<a id="{prefix}"></a>', "", f"## {unit_title}", ""]
    if not has_unit_header:
        parts = [f'<a id="{prefix}"></a>', "", f"## {unit_title}", ""]
    else:
        parts = []
    parts.extend(body)
    return "\n".join(parts).strip() + "\n", [(unit_title, prefix)] + toc


def nav_line(files: list[tuple[str, str]], idx: int) -> str:
    parts = ["[📑 目录](00-目录.md#目录)"]
    if idx > 0:
        parts.insert(0, f"[← {files[idx - 1][1]}]({files[idx - 1][0]})")
    if idx < len(files) - 1:
        parts.append(f"[{files[idx + 1][1]} →]({files[idx + 1][0]})")
    return " · ".join(parts)


def write_units():
    OUT.mkdir(exist_ok=True)
    all_files: list[tuple[int, int, str, str, list[tuple[str, str]]]] = []

    for book in (1, 2, 3):
        lines = BOOKS[book].read_text(encoding="utf-8").splitlines()
        for num, title, chunk in split_units(book, lines):
            fname = unit_fname(book, num, title)
            prefix = f"b{book}-u{num}"
            content, toc = build_unit_body(book, num, title, chunk)
            all_files.append((book, num, fname, title, toc))
            (OUT / fname).write_text(content, encoding="utf-8")

    flat = [(f, f"Unit{num} {title}") for book, num, f, title, _ in all_files]
    for i, (book, num, fname, title, toc) in enumerate(all_files):
        nav = nav_line(flat, i)
        body = (OUT / fname).read_text(encoding="utf-8")
        local_toc = ["## 本章目录", ""]
        for text, aid in toc:
            indent = "  " if not text.startswith("Unit") else ""
            local_toc.append(f"{indent}- [{text}](#{aid})")
        header = f"{nav}\n\n---\n\n" + "\n".join(local_toc) + "\n\n---\n\n"
        (OUT / fname).write_text(header + body, encoding="utf-8")

    toc_lines = [
        "# 谢孟媛《初级语法》",
        "",
        "谢孟媛英语课程学习交流站 XieMengYuan.cn",
        "",
        "[📑 目录](#目录)",
        "",
        '<a id="目录"></a>',
        "",
        "## 目录",
        "",
    ]
    book_names = {1: "第一册", 2: "第二册", 3: "第三册"}
    for book in (1, 2, 3):
        toc_lines.append(f"### {book_names[book]}")
        for b, num, fname, title, sections in all_files:
            if b != book:
                continue
            prefix = f"b{book}-u{num}"
            toc_lines.append(f"- [Unit{num} {title}]({fname}#{prefix})")
            for text, aid in sections:
                if text.startswith("Unit"):
                    continue
                toc_lines.append(f"  - [{text}]({fname}#{aid})")
    toc_lines.extend(["", "---", ""])
    (OUT / "00-目录.md").write_text("\n".join(toc_lines), encoding="utf-8")
    print(f"units: {len(all_files)} -> {OUT}")


if __name__ == "__main__":
    write_units()
