"""Register BOSS links (no live fetch)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from boss_jd_batch.inbox import append_links, extract_urls_from_file


def cmd_import_links(links_path: Path, pending_path: Path) -> int:
    if not links_path.is_file():
        print(f"无链接文件: {links_path}")
        return 0

    urls = extract_urls_from_file(links_path)
    if not urls:
        print("links.txt 无有效链接")
        return 0

    pending_path.parent.mkdir(parents=True, exist_ok=True)
    existing_pending: set[str] = set()
    if pending_path.is_file():
        import json as _json

        try:
            data = _json.loads(pending_path.read_text(encoding="utf-8"))
            existing_pending = {item["url"] for item in data.get("links", [])}
        except Exception:
            pass

    unique = list(dict.fromkeys(urls))
    if existing_pending >= set(unique):
        return 0
    payload = {
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "note": "以下链接需浏览器另存为 HTML 后放入 input/inbox/，再运行 import-all",
        "links": [{"url": u, "status": "pending_html"} for u in dict.fromkeys(urls)],
    }
    pending_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已登记 {len(payload['links'])} 条链接 -> {pending_path}")
    print("请打开链接 → Ctrl+S 另存为 → 放入 input/inbox/")
    return 0
