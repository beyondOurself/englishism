# -*- coding: utf-8 -*-
import hashlib
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(__file__).resolve().parent
GITHUB_REPO = "beyondOurself/englishism"
GITHUB_BRANCH = "main"
ASSETS_DIR = BASE / "assets" / "egiu"
TARGET_DIRS = [BASE / "egiu-units"]
TARGET_FILES = [BASE / "剑桥初级英语语法-合并.md"]

URL_PATTERNS = [
    re.compile(r"!\[[^\]]*\]\((https?://[^\)]+)\)"),
    re.compile(r"""<img[^>]+src=["'](https?://[^"']+)["']""", re.I),
]

RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/assets/egiu"


def collect_md_files() -> list[Path]:
    files: list[Path] = []
    for d in TARGET_DIRS:
        if d.is_dir():
            files.extend(sorted(d.glob("*.md")))
    for f in TARGET_FILES:
        if f.exists() and f not in files:
            files.append(f)
    return files


def extract_urls(text: str) -> set[str]:
    urls: set[str] = set()
    for pat in URL_PATTERNS:
        urls.update(pat.findall(text))
    return urls


def ext_from_url(url: str) -> str:
    path = urlparse(url).path
    suffix = Path(path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}:
        return suffix
    return ".jpg"


def local_name(url: str) -> str:
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    return h + ext_from_url(url)


def download(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 500:
        return True
    last_err = None
    for _ in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            if len(data) < 200:
                raise RuntimeError("too small")
            dest.write_bytes(data)
            return True
        except Exception as e:
            last_err = e
            time.sleep(1)
    print(f"FAIL {url} -> {last_err}")
    return False


def replace_urls(text: str, mapping: dict[str, str]) -> str:
    for old, new in mapping.items():
        text = text.replace(old, new)
    return text


def main():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    md_files = collect_md_files()
    all_urls: set[str] = set()
    for f in md_files:
        all_urls.update(extract_urls(f.read_text(encoding="utf-8")))

    remote_urls = sorted(u for u in all_urls if u.startswith("http"))
    print(f"md files: {len(md_files)}")
    print(f"unique remote urls: {len(remote_urls)}")

    mapping: dict[str, str] = {}
    ok = 0
    for i, url in enumerate(remote_urls, 1):
        fname = local_name(url)
        dest = ASSETS_DIR / fname
        if download(url, dest):
            mapping[url] = f"{RAW_BASE}/{fname}"
            ok += 1
        if i % 20 == 0:
            print(f"downloaded {i}/{len(remote_urls)}")

    print(f"downloaded ok: {ok}/{len(remote_urls)}")

    changed = 0
    for f in md_files:
        text = f.read_text(encoding="utf-8")
        new_text = replace_urls(text, mapping)
        if new_text != text:
            f.write_text(new_text, encoding="utf-8")
            changed += 1

    print(f"updated md files: {changed}")
    print(f"assets dir: {ASSETS_DIR}")


if __name__ == "__main__":
    main()
