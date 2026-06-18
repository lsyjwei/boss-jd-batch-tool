"""CLI for BOSS JD batch import."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from boss_jd_batch.extension_import import (
    import_extension_exports,
    rebuild_manifest_from_output,
)
from boss_jd_batch.html_parser import (
    build_manifest,
    find_html_inputs,
    parse_html_file,
    write_outputs,
)
from boss_jd_batch.inbox import process_inbox
from boss_jd_batch.links import cmd_import_links


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def cmd_import_html(input_dir: Path | None, output_dir: Path | None) -> list:
    root = _project_root()
    input_dir = input_dir or root / "input" / "html"
    output_dir = output_dir or root / "output" / "jobs"

    if not input_dir.is_dir():
        print(f"HTML 目录不存在: {input_dir}", file=sys.stderr)
        return []

    html_files = find_html_inputs(input_dir)
    if not html_files:
        print("无 HTML 文件可解析")
        return []

    records = []
    for path in html_files:
        try:
            record = parse_html_file(path)
            write_outputs(record, output_dir)
            records.append(record)
            print(f"OK  {record.title} @ {record.company} -> {record.id}")
        except Exception as exc:
            print(f"ERR {path.name}: {exc}", file=sys.stderr)
    return records


def cmd_import_extension() -> int:
    root = _project_root()
    print("=== 导入扩展 JSON ===")
    records = import_extension_exports(
        inbox=root / "input" / "inbox",
        output_dir=root / "output" / "jobs",
    )
    if not records:
        print("inbox 中无 .json 文件")
        return 0
    rebuild_manifest_from_output(root / "output" / "jobs", root / "output" / "manifest.json")
    print(f"\nmanifest 已更新: {root / 'output' / 'manifest.json'}")
    return 0


def cmd_process_inbox() -> int:
    root = _project_root()
    print("=== 处理 inbox HTML（重命名为 「职位」_公司） ===")
    moved, link_count = process_inbox(
        inbox=root / "input" / "inbox",
        html_dir=root / "input" / "html",
        links_path=root / "input" / "links.txt",
    )
    if not moved and not link_count:
        print("inbox 无新 HTML")
    if link_count:
        cmd_import_links(root / "input" / "links.txt", root / "output" / "pending-links.json")
    return 0


def cmd_import_all() -> int:
    root = _project_root()
    output_dir = root / "output" / "jobs"
    manifest_path = root / "output" / "manifest.json"

    print("=== Step 1/3: inbox HTML 入库 ===")
    process_inbox(
        inbox=root / "input" / "inbox",
        html_dir=root / "input" / "html",
        links_path=root / "input" / "links.txt",
    )

    print("\n=== Step 2/3: 扩展 JSON 导入 ===")
    import_extension_exports(
        inbox=root / "input" / "inbox",
        output_dir=output_dir,
    )

    print("\n=== Step 3/3: HTML 解析 ===")
    cmd_import_html(None, output_dir)

    records = rebuild_manifest_from_output(output_dir, manifest_path)
    if not records:
        print("\n未生成任何 JD，请检查 input/inbox 或 input/html", file=sys.stderr)
        return 1

    print(f"\n完成: {len(records)} 条 -> {output_dir}")
    print(f"索引: {manifest_path}")
    print("Cursor 可 @ output/manifest.json 或 output/jobs/*.md")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BOSS 直聘 JD 批量导入工具")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("process-inbox", help="inbox HTML 入库并重命名")
    sub.add_parser("import-all", help="inbox + 扩展 JSON + HTML（推荐）")
    sub.add_parser("import-extension", help="仅导入 inbox/*.json（扩展导出）")

    html_cmd = sub.add_parser("import-html", help="批量解析 input/html/")
    html_cmd.add_argument("--input", type=Path, default=None)
    html_cmd.add_argument("--output", type=Path, default=None)

    links_cmd = sub.add_parser("import-links", help="登记 links.txt")
    links_cmd.add_argument("--file", type=Path, default=None)

    args = parser.parse_args(argv)
    root = _project_root()

    if args.command == "process-inbox":
        return cmd_process_inbox()
    if args.command == "import-all":
        return cmd_import_all()
    if args.command == "import-extension":
        return cmd_import_extension()
    if args.command == "import-html":
        records = cmd_import_html(args.input, args.output)
        if not records:
            return 1
        build_manifest(records, root / "output" / "manifest.json")
        return 0
    if args.command == "import-links":
        links = args.file or root / "input" / "links.txt"
        return cmd_import_links(links, root / "output" / "pending-links.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
