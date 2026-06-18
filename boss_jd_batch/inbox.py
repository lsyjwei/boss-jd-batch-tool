"""Inbox: drop saved HTML or link files, normalize to 「职位」_公司.html."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from boss_jd_batch.html_parser import parse_html_file

WIN_INVALID = re.compile(r'[\\/:*?"<>|]')
ZHIPIN_URL_RE = re.compile(
    r"https?://(?:www\.|m\.)?zhipin\.com/job_detail/[A-Za-z0-9_-]+\.html[^\s]*"
)
STANDARD_NAME_RE = re.compile(r"^「.+」_.+\.html$", re.UNICODE)


def sanitize_filename_part(text: str) -> str:
    cleaned = WIN_INVALID.sub("_", text.strip())
    return cleaned or "未知"


def standard_html_filename(title: str, company: str) -> str:
    title = sanitize_filename_part(title)
    company = sanitize_filename_part(company)
    return f"「{title}」_{company}.html"


def is_standard_filename(name: str) -> bool:
    return bool(STANDARD_NAME_RE.match(name))


def _unique_dest(dest: Path) -> Path:
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    for i in range(2, 100):
        candidate = dest.with_name(f"{stem}-{i}{suffix}")
        if not candidate.exists():
            return candidate
    return dest.with_name(f"{stem}-dup{suffix}")


def _rename_companion_files(html_path: Path, old_stem: str, new_stem: str) -> None:
    old_dir = html_path.parent / f"{old_stem}_files"
    if not old_dir.is_dir():
        return
    new_dir = html_path.parent / f"{new_stem}_files"
    if new_dir.exists() and new_dir != old_dir:
        shutil.rmtree(new_dir)
    if old_dir != new_dir:
        old_dir.rename(new_dir)


def _update_html_asset_refs(content: str, old_stem: str, new_stem: str) -> str:
    if old_stem == new_stem:
        return content
    content = content.replace(f"{old_stem}_files", f"{new_stem}_files")
    return content


def normalize_html_file(source: Path, html_dir: Path) -> Path:
    """Parse, rename to 「职位」_公司.html, move into html_dir."""
    record = parse_html_file(source)
    if not record.title:
        raise ValueError(f"无法解析职位名: {source.name}")

    new_name = standard_html_filename(record.title, record.company or "未知公司")
    dest = _unique_dest(html_dir / new_name)
    new_stem = dest.stem
    old_stem = source.stem

    content = source.read_text(encoding="utf-8", errors="replace")
    content = _update_html_asset_refs(content, old_stem, new_stem)

    if source.parent.resolve() == html_dir.resolve():
        if source.name == dest.name:
            return source
        temp = html_dir / f".__renaming_{source.name}"
        temp.write_text(content, encoding="utf-8")
        _rename_companion_files(source, old_stem, new_stem)
        source.unlink()
        temp.rename(dest)
        return dest

    html_dir.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    old_files = source.parent / f"{old_stem}_files"
    new_files = html_dir / f"{new_stem}_files"
    if old_files.is_dir():
        if new_files.exists():
            shutil.rmtree(new_files)
        shutil.move(str(old_files), str(new_files))
    source.unlink()
    return dest


def collect_inbox_html(inbox: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(inbox.rglob("*.html")):
        if "_files" in path.parts or path.name.startswith("saved_resource"):
            continue
        files.append(path)
    for path in sorted(inbox.rglob("*.htm")):
        if "_files" in path.parts:
            continue
        files.append(path)
    return files


def extract_urls_from_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return ZHIPIN_URL_RE.findall(text)


def append_links(links_path: Path, urls: list[str]) -> int:
    existing: set[str] = set()
    if links_path.is_file():
        existing = set(extract_urls_from_file(links_path))
    new_urls = [u.split("?")[0] if "?" in u else u for u in urls if u not in existing]
    if not new_urls:
        return 0
    links_path.parent.mkdir(parents=True, exist_ok=True)
    with links_path.open("a", encoding="utf-8") as f:
        for url in new_urls:
            f.write(url + "\n")
    return len(new_urls)


def process_inbox(
    inbox: Path | None = None,
    html_dir: Path | None = None,
    links_path: Path | None = None,
) -> tuple[list[Path], int]:
    """
    Process inbox:
    - .html/.htm -> parse, rename 「职位」_公司, move to html_dir
    - .txt/.url with zhipin links -> append to links.txt (reminder to save HTML)
    Returns (moved_html_paths, new_link_count)
    """
    root = inbox.parent if inbox else Path(".")
    inbox = inbox or root / "input" / "inbox"
    html_dir = html_dir or root / "input" / "html"
    links_path = links_path or root / "input" / "links.txt"

    if not inbox.is_dir():
        inbox.mkdir(parents=True, exist_ok=True)
        return [], 0

    moved: list[Path] = []
    for path in collect_inbox_html(inbox):
        try:
            dest = normalize_html_file(path, html_dir)
            action = "重命名" if path.parent.resolve() == html_dir.resolve() else "入库"
            print(f"{action}  {dest.name}")
            moved.append(dest)
        except Exception as exc:
            print(f"ERR {path.name}: {exc}")

    link_count = 0
    for pattern in ("*.txt", "*.url", "*.link"):
        for path in inbox.glob(pattern):
            urls = extract_urls_from_file(path)
            if not urls:
                continue
            n = append_links(links_path, urls)
            link_count += n
            if n:
                print(f"链接登记  {path.name} -> links.txt (+{n})")
            path.unlink()

    return moved, link_count
