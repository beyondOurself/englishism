# -*- coding: utf-8 -*-
import html
import re
from pathlib import Path

BASE = Path(r"C:\Users\admin\Desktop\书籍\英语语法\englishism")
FILE1 = BASE / "MinerU_markdown_剑桥初级英语语法：第3版._2079870553701728256.md"
FILE2 = BASE / "MinerU_markdown_剑桥初级英语语法：第3版._2079870697205649408.md"
OUT_MERGED = BASE / "剑桥初级英语语法-合并.md"
OUT_UNITS = BASE / "egiu-units"

UNIT_TITLES = {
    1: "am/is/are", 2: "am/is/are (疑问句)", 3: "I am doing (现在进行时)",
    4: "are you doing? (现在进行时的疑问式)", 5: "I do/work/like 等 (一般现在时)",
    6: "I don't ... (一般现在时的否定式)", 7: "Do you ...? (一般现在时的疑问式)",
    8: "I am doing 与 I do 比较", 9: "I have ... / I've got ...", 10: "was/were",
    11: "worked/got/went 等 (一般过去时)", 12: "I didn't ... Did you ...? (一般过去时否定与疑问)",
    13: "I was doing (过去进行时)", 14: "I was doing 与 I did 比较",
    15: "I have done (现在完成时 1)", 16: "I've just ... already ... yet (现在完成时 2)",
    17: "Have you ever ...? (现在完成时 3)", 18: "How long have you ...? (现在完成时 4)",
    19: "for since ago", 20: "I have done 与 I did 比较",
    21: "is done was done (被动语态 1)", 22: "is being done has been done (被动语态 2)",
    23: "现在时与过去时中的 be/have/do", 24: "规则动词与不规则动词",
    25: "What are you doing tomorrow?", 26: "I'm going to ...",
    27: "will/shall (1)", 28: "will/shall (2)", 29: "might", 30: "can 与 could 比较",
    31: "must mustn't don't need to", 32: "should", 33: "I have to ...",
    34: "Would you like ...? I'd like ...", 35: "Do this! Don't do that! Let's do this!",
    36: "I used to ...", 37: "there is there are", 38: "there was/were has/have been will be",
    39: "It ...", 40: "I am, I don't 等", 41: "have you? are you? don't you? 等",
    42: "too/either so am I / neither do I 等", 43: "isn't, haven't, don't 等 (否定句)",
    44: "is it ...? have you ...? do they ...? 等 (疑问句 1)",
    45: "Who saw you? Who did you see? (疑问句 2)",
    46: "Who is she talking to? What is it like? (疑问句 3)",
    47: "What ...? Which ...? How ...? (疑问句 4)", 48: "How long does it take ...?",
    49: "Do you know where ...? I don't know what ... 等",
    50: "She said that ... He told me that ...", 51: "telephone/email 等 (动词 + to ...)",
    52: "动词不定式与 -ing 形式比较", 53: "I want you to ... / I told you to ...",
    54: "I went to ... / I went on holiday ...", 55: "get to ... / get home / get to work",
    56: "do/doing/did/done 与 make/making/made", 57: "do/doing/did/done 与 make/making/made (2)",
    58: "have/have got/had", 59: "I/me he/him they/them 等", 60: "my/his/their 等",
    61: "Whose is this? It's mine/yours/hers 等", 62: "I/me/my/mine 复习",
    63: "myself/yourself/themselves 等", 64: "-'s (Kate's camera / my brother's car 等)",
    65: "a/an ...", 66: "train(s) bus(es) (单数与复数)", 67: "a bottle / some water (可数/不可数 1)",
    68: "a cake / some cake / some cakes (可数/不可数 2)", 69: "a/an 与 the 比较",
    70: "the ...", 71: "go to work go home go to the cinema", 72: "I like music I hate exams",
    73: "the ... (地名)", 74: "this/that/these/those", 75: "one/ones",
    76: "some 与 any 比较", 77: "not + any no none", 78: "not + anybody/anything/nothing",
    79: "somebody/anything/nowhere 等", 80: "every 与 all 比较", 81: "all most some any no/none",
    82: "both either neither", 83: "a lot much many", 84: "(a) little (a) few",
    85: "old/nice/interesting 等 (形容词)", 86: "quickly/badly/suddenly 等 (副词)",
    87: "old/older expensive / more expensive", 88: "older than ... more expensive than ...",
    89: "not as ... as", 90: "the oldest the most expensive", 91: "enough", 92: "too",
    93: "He speaks English very well. (词序 1)", 94: "always/usually/often 等 (词序 2)",
    95: "still yet already", 96: "Give me that book! Give it to me!", 97: "and but or so because",
    98: "when ...", 99: "if we go ... if you see ... 等", 100: "if I had ... if we went ... 等",
    101: "a person who ... (定语从句 1)", 102: "the people we met the hotel you stayed at (定语从句 2)",
    103: "at 8 o'clock on Monday in April", 104: "from ... to until since for",
    105: "before after during while", 106: "in at on (地点 1)", 107: "in at on (地点 2)",
    108: "to in at (地点 3)", 109: "under, behind, opposite 等", 110: "up, over, through 等",
    111: "on at by with about", 112: "afraid of ..., good at ... 等 + -ing",
    113: "listen to ..., look at ... 等 (动词 + 介词)", 114: "go in, fall off, run away 等 (短语动词 1)",
    115: "put on your shoes put your shoes on (短语动词 2)",
}

UNIT_PATTERNS: dict[int, list[str]] = {
    1: [r"^## am/is/are$"],
    2: [r"^## am/is/are（疑问句）"],
    3: [r"^## I am doing（现在进行时）"],
    4: [r"^## are you doing"],
    5: [r"^## I do/work/like"],
    6: [r"^# I don't \.\.\.", r"^## I don't \.\.\."],
    7: [r"^# Do you \.\.\.", r"^## Do you \.\.\."],
    8: [r"^## 8\.2 ", r"^8\.1 根据图片"],
    9: [r"^## I have \.\.\.", r"I've got"],
    10: [r"^## was/were$", r"^## was/were "],
    11: [r"^## worked/got/went"],
    12: [r"I didn't \.\.\..*Did you", r"一般过去时的否定式与疑问式"],
    13: [r"^## Unit 13", r"^## I was doing（过去进行时）$"],
    14: [r"I was doing.*与 I did", r"过去进行时.*一般过去时.*比较"],
    15: [r"^## Unit 15", r"^## I have done \(现在完成时 1\)"],
    16: [r"^## Unit 16", r"I've just \.\.\..*already"],
    17: [r"^## Have you ever"],
    18: [r"^## How long have you"],
    19: [r"^## for since ago"],
    20: [r"I have done.*与 I did", r"现在完成时.*一般过去时.*比较"],
    21: [r"^## is done", r"被动语态 1"],
    22: [r"is being done", r"has been done", r"被动语态 2"],
    23: [r"^## Unit 23", r"现在时与过去时中的 be/have/do"],
    24: [r"规则动词与不规则动词"],
    25: [r"^## What are you doing tomorrow"],
    26: [r"^## I'm going to \.\.\.", r"^## I'm going to do something"],
    27: [r"^## will/shall \(1\)", r"will/shall \(1\)"],
    28: [r"^## will/shall \(2\)", r"will/shall \(2\)"],
    29: [r"^## might \+", r"^## might$"],
    30: [r"can 与 could 比较"],
    31: [r"^## must mustn't", r"mustn't don't need to"],
    32: [r"^## should \+", r"^## should$"],
    33: [r"^## I have to \.\.\."],
    34: [r"^## Would you like", r"^## 34\.1 ", r"^34\.1 "],
    35: [r"^35\.1 ", r"come/look/go/wait/do/be 等可用来命令", r"let's \.\.\. 可用来提议"],
    36: [r"^## I used to \.\.\."],
    37: [r"^## there is there are", r"^## there is$"],
    38: [r"^## Unit 38", r"there was/were"],
    39: [r"^## Unit 39", r"^## It \.\.\."],
    40: [r"^## I am, I don't 等", r"^## I am, I don't"],
    41: [r"^## Unit 41", r"have you\? / is it\?", r"have you\?.*are you\?"],
    42: [r"too 与 either 比较", r"so am I / neither do I"],
    43: [r"^## isn't, haven't, don't 等", r"isn't, haven't, don't 等（否定句）"],
    44: [r"is it \.\.\.\? have you \.\.\.\?", r"疑问句 1"],
    45: [r"^## Unit 45", r"^## Who saw you"],
    46: [r"Who is she talking to", r"What is it like", r"疑问句 3"],
    47: [r"^## Unit 47", r"What \.\.\.\? Which \.\.\.\? How"],
    48: [r"^## How long does it take"],
    49: [r"^# Do you know where", r"Do you know where \.\.\.\?"],
    50: [r"^## She said that \.\.\.", r"^50\.1 "],
    51: [r"^## 51\.1 ", r"^51\.1 ", r"phone Paul", r"to phone Paul"],
    52: [r"动词不定式.*-ing 形式", r"I want to do.*I enjoy doing"],
    53: [r"I want you to \.\.\.", r"I told you to \.\.\."],
    54: [r"^## Unit 54", r"I went to \.\.\.", r"I went on holiday"],
    55: [r"^## Unit 55", r"get to \.\.\.", r"get home", r"get to work"],
    56: [r"make/making/made 或 do/doing", r"go, get, do, make 与 have"],
    57: [r"^## Unit 57"],
    58: [r"^## Unit 58", r"have/have got/had"],
    59: [r"I/me he/him they/them", r"^## I/me "],
    60: [r"^## my/his/their", r"my/his/their 等"],
    61: [r"^## Unit 61", r"Whose is this", r"It's mine/yours/hers"],
    62: [r"^## I/me/my/mine 复习", r"^## 62\.1"],
    63: [r"^## myself/yourself", r"myself/yourself/themselves"],
    64: [r"Kate's camera", r"my brother's car", r"-'s \("],
    65: [r"^## a/an \.\.\.", r"^## a/an "],
    66: [r"^## Unit 66", r"train\(s\) bus\(es\)", r"单数与复数"],
    67: [r"^## Unit 67", r"a bottle / some water", r"可数名词/不可数名词 1"],
    68: [r"a cake / some cake", r"可数名词/不可数名词 2"],
    69: [r"a/an 与 the 比较"],
    70: [r"^## Unit 70", r"^## the \.\.\.$"],
    71: [r"^## go to work go home", r"go to work go home go to the cinema"],
    72: [r"^## Unit 72", r"I like music I hate exams"],
    73: [r"the \.\.\. \(地名\)", r"^## the \.\.\. \(地名\)"],
    74: [r"^## this/that/these/those"],
    75: [r"^## one/ones$"],
    76: [r"some 与 any 比较"],
    77: [r"not \+ any no none", r"not \+ any"],
    78: [r"not \+ anybody/anything", r"nobody/no-one/nothing"],
    79: [r"somebody/anything/nowhere"],
    80: [r"^## every$", r"^80\.1 ", r"^## 请比较 every 与 all"],
    81: [r"^all$", r"most/some 等 \+ 名词", r"^81\.1 "],
    82: [r"both either neither"],
    83: [r"a lot much many"],
    84: [r"\(a\) little \(a\) few", r"a little \(a\) few"],
    85: [r"old/nice/interesting 等 \(形容词\)", r"^## old/nice"],
    86: [r"quickly/badly/suddenly 等 \(副词\)", r"^## quickly/badly"],
    87: [r"old/older expensive", r"more expensive"],
    88: [r"older than \.\.\.", r"more expensive than"],
    89: [r"^## not as \.\.\. as"],
    90: [r"the oldest the most expensive", r"比较级.*最高级"],
    91: [r"^## enough$"],
    92: [r"<td>Unit 92</td>", r"^## too$"],
    93: [r"^## He speaks English very well", r"词序 1"],
    94: [r"always/usually/often 等 \(词序 2\)", r"词序 2"],
    95: [r"^## still yet already"],
    96: [r"^## Give me that book", r"Give it to me"],
    97: [r"^## and but or so because", r"and but or so because"],
    98: [r"^## when \.\.\."],
    99: [r"if we go \.\.\.", r"if you see \.\.\."],
    100: [r"if I had \.\.\.", r"if we went \.\.\."],
    101: [r"a person who \.\.\.", r"定语从句 1"],
    102: [r"the people we met", r"定语从句 2"],
    103: [r"at 8 o'clock on Monday", r"^## at 8 o'clock"],
    104: [r"^## from \.\.\. to \.\.\.", r"from \.\.\. to until since for"],
    105: [r"^## before after during while"],
    106: [r"in at on \(地点 1\)", r"^## in at on \(地点 1\)"],
    107: [r"^107\.1 ", r"^## Unit 107", r"in at on \(地点 2\)"],
    108: [r"^## arrive 与 get 比较", r"^## 108\.2 ", r"^108\.1 ", r"to in at \(地点 3\)"],
    109: [r"under, behind, opposite"],
    110: [r"^## Unit 110", r"up, over, through"],
    111: [r"^## Unit 111", r"on at by with about"],
    112: [r"afraid of \.\.\., good at", r"介词.*\+ -ing"],
    113: [r"^## listen to \.\.\.", r"listen to \.\.\., look at"],
    114: [r"go in, fall off, run away", r"短语动词 1"],
    115: [r"^## Unit 115", r"put on your shoes", r"短语动词 2"],
}

JUNK_LINE_PATTERNS = [
    r"^\[Unreadable\]$", r"^## \[Unreadable\]$", r"^## 无法识别$", r"^## 第\d+页$",
]


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def clean_line(line: str) -> str:
    line = html.unescape(line)
    line = re.sub(r"\$\s*\\mathbf\{([^}]+)\}\s*\$", r"\1", line)
    line = re.sub(r"\$\s*([^$]+?)\s*\$", r"\1", line)
    line = re.sub(r"\\rightarrow", "→", line)
    line = line.replace("\u00a0", " ")
    line = re.sub(r"[ \t]+$", "", line)
    return line


def clean_text(text: str) -> str:
    lines = [clean_line(x) for x in text.splitlines()]
    out: list[str] = []
    prev = None
    in_txt = False
    txt_buf: list[str] = []
    seen_main_title = False

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
        if any(re.match(p, line.strip()) for p in JUNK_LINE_PATTERNS):
            continue
        if line.strip() == "# 剑桥初级 英语语法":
            if seen_main_title:
                continue
            seen_main_title = True
        if line.strip() == prev and line.startswith("## "):
            continue
        out.append(line)
        prev = line.strip()

    text = "\n".join(out)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip() + "\n"


def build_front_matter(lines1: list[str]) -> str:
    chunks = ["\n".join(lines1[0:98]), "\n".join(lines1[98:370]), "\n".join(lines1[809:999])]
    text = clean_text("\n\n".join(chunks))
    text = re.sub(r"\n## 目录\n\n如不确定.*?(?=\n## 语法知识|\n## Thanks|\Z)", "\n", text, flags=re.S)
    text = re.sub(r"\n## 索引\n\nIF YOU ARE NOT SURE.*?(?=\n## 语法知识|\Z)", "\n", text, flags=re.S)
    return clean_text(text)


def slugify(title: str) -> str:
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "-", title.lower(), flags=re.UNICODE)
    return re.sub(r"-+", "-", s).strip("-")[:60] or "unit"


def find_content_start(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        if line.strip() != "## am/is/are":
            continue
        if "## 肯定式" in "\n".join(lines[i : i + 20]):
            return i
    raise RuntimeError("找不到 Unit 1")


def find_appendix_start(lines: list[str], content_start: int) -> int:
    for i in range(content_start + 5000, len(lines)):
        if re.match(r"^## 附录\s*1\b", lines[i].strip()):
            return i
    raise RuntimeError("找不到附录")


def is_cross_ref(line: str) -> bool:
    return bool(re.search(r"(?:参见|→)\s*Unit\s+\d", line))


def scan_back_to_unit_start(lines: list[str], ex_line: int, content_start: int) -> int:
    for j in range(ex_line - 1, max(content_start, ex_line - 300), -1):
        prev = lines[j].strip()
        if not prev or prev == "## Exercises":
            continue
        if re.match(r"^##? ?\d+\.\d+", prev):
            continue
        if re.match(r"^\d+\.\d+", prev):
            continue
        if prev.startswith("#") or prev.startswith("##"):
            return j
        if "<table>" in prev or prev.startswith("<table"):
            return j
    return ex_line


def find_unit_starts(lines: list[str], content_start: int, content_end: int) -> dict[int, int]:
    candidates: dict[int, list[int]] = {n: [] for n in range(1, 116)}

    for i in range(content_start, content_end):
        line = lines[i]
        if is_cross_ref(line):
            continue
        m = re.match(r"^## Unit (\d+)\s*$", line, re.I)
        if m:
            candidates[int(m.group(1))].append(i)
        for m in re.finditer(r"<td>Unit (\d+)</td>", line, re.I):
            candidates[int(m.group(1))].append(i)
        m = re.match(r"^##? ?(\d+)\.1(?:\s|$)", line)
        if not m:
            m = re.match(r"^(\d+)\.1(?:\s|$)", line)
        if m and not m.group(1).startswith("0"):
            n = int(m.group(1))
            if 1 <= n <= 115:
                candidates[n].append(scan_back_to_unit_start(lines, i, content_start))

    for n, patterns in UNIT_PATTERNS.items():
        for i in range(content_start, content_end):
            line = lines[i]
            if is_cross_ref(line):
                continue
            for pat in patterns:
                if pat.startswith("^"):
                    if re.match(pat, line):
                        candidates[n].append(i)
                        break
                elif line.lstrip().startswith("#") and re.search(pat, line):
                    candidates[n].append(i)
                    break
                elif re.match(pat, line.strip()):
                    candidates[n].append(i)
                    break

    starts: dict[int, int] = {}
    prev = content_start
    for n in range(1, 116):
        opts = [x for x in candidates[n] if x >= prev]
        if opts:
            starts[n] = min(opts)
        elif n - 1 in starts:
            starts[n] = starts[n - 1] + 1
        else:
            starts[n] = prev
        prev = starts[n] + 1
    return starts


def split_units(lines: list[str]) -> tuple[str, dict[int, str], str]:
    content_start = find_content_start(lines)
    appendix_start = find_appendix_start(lines, content_start)
    front = clean_text("\n".join(lines[:content_start]))
    back = clean_text("\n".join(lines[appendix_start:]))
    starts = find_unit_starts(lines, content_start, appendix_start)

    units: dict[int, str] = {}
    nums = sorted(starts)
    for idx, n in enumerate(nums):
        end = starts[nums[idx + 1]] if idx + 1 < len(nums) else appendix_start
        chunk = clean_text("\n".join(lines[starts[n]:end]))
        title = UNIT_TITLES[n]
        units[n] = f"# Unit {n} {title}\n\n{chunk}"
    return front, units, back


def write_units(units: dict[int, str]):
    OUT_UNITS.mkdir(exist_ok=True)
    toc_lines = ["# 剑桥初级英语语法 · 单元目录", ""]
    files: list[tuple[int, str, str]] = []

    for n in sorted(units):
        title = UNIT_TITLES[n]
        fname = f"unit-{n:03d}-{slugify(title)}.md"
        files.append((n, fname, title))
        (OUT_UNITS / fname).write_text(units[n], encoding="utf-8")

    for i, (n, fname, title) in enumerate(files):
        nav_prev = f"[← Unit {n-1}]({files[i-1][1]})" if i else "[← 目录](00-目录.md)"
        nav_next = f"[Unit {n+1} →]({files[i+1][1]})" if i < len(files) - 1 else "[附录 →](../剑桥初级英语语法-合并.md#附录)"
        nav = f"{nav_prev} · [目录](00-目录.md) · {nav_next}"
        body = (OUT_UNITS / fname).read_text(encoding="utf-8")
        (OUT_UNITS / fname).write_text(f"{nav}\n\n---\n\n{body}", encoding="utf-8")
        toc_lines.append(f"- [Unit {n} {title}]({fname})")

    (OUT_UNITS / "00-目录.md").write_text("\n".join(toc_lines) + "\n", encoding="utf-8")


def main():
    lines1 = read_lines(FILE1)
    lines2 = read_lines(FILE2)
    appendix2 = next(i for i, line in enumerate(lines2) if re.match(r"^## 附录\s*1\b", line.strip()))
    merged = clean_text(
        f"{build_front_matter(lines1)}\n\n---\n\n"
        f"{clean_text(chr(10).join(lines1[999:]))}\n\n"
        f"{clean_text(chr(10).join(lines2[:appendix2]))}\n\n---\n\n"
        f"{clean_text(chr(10).join(lines2[appendix2:]))}\n"
    )
    OUT_MERGED.write_text(merged, encoding="utf-8")

    lines = merged.splitlines()
    _, units, _ = split_units(lines)
    write_units(units)

    sizes = [(n, len(units[n])) for n in [1, 7, 50, 91, 115]]
    print(f"merged: {OUT_MERGED} ({len(lines)} lines)")
    print(f"units: {len(units)} files -> {OUT_UNITS}")
    for n, sz in sizes:
        print(f"  unit {n}: {sz} chars")


if __name__ == "__main__":
    main()
