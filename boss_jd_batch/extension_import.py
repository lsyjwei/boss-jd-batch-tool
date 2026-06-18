"""Import JSON exported by the Chrome extension."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from boss_jd_batch.html_parser import JobRecord, _slugify, write_outputs


def job_record_from_extension(job: dict, source_file: str) -> JobRecord:
    title = job.get("title", "").strip()
    if not title:
        raise ValueError("缺少 title")

    raw_id = job.get("job_id") or _slugify(title)
    record_id = f"job-{_slugify(raw_id or title)}"

    return JobRecord(
        id=record_id,
        title=title,
        company=job.get("company", ""),
        salary=job.get("salary", ""),
        jd_body=job.get("jd_body", ""),
        source_url=job.get("source_url", ""),
        source_type="extension",
        source_file=source_file,
        location=job.get("location", ""),
        experience=job.get("experience", ""),
        degree=job.get("degree", ""),
        fetched_at=job.get("collected_at")
        or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    )


def _load_jobs_from_json(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "jobs" in data:
        return data["jobs"]
    if isinstance(data, dict) and data.get("title"):
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError(f"无法识别 JSON 格式: {path.name}")


def find_extension_exports(inbox: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(inbox.glob("*.json")):
        if path.parent.name == "processed":
            continue
        files.append(path)
    return files


def import_extension_file(path: Path, output_dir: Path, processed_dir: Path) -> list[JobRecord]:
    jobs = _load_jobs_from_json(path)
    records: list[JobRecord] = []
    source_ref = str(path.as_posix())

    for job in jobs:
        record = job_record_from_extension(job, source_ref)
        write_outputs(record, output_dir)
        records.append(record)

    processed_dir.mkdir(parents=True, exist_ok=True)
    dest = processed_dir / path.name
    if dest.exists():
        dest = processed_dir / f"{path.stem}-{int(datetime.now().timestamp())}{path.suffix}"
    shutil.move(str(path), str(dest))
    return records


def import_extension_exports(
    inbox: Path | None = None,
    output_dir: Path | None = None,
    processed_dir: Path | None = None,
) -> list[JobRecord]:
    inbox = inbox or Path("input/inbox")
    output_dir = output_dir or Path("output/jobs")
    processed_dir = processed_dir or inbox / "processed"

    if not inbox.is_dir():
        return []

    all_records: list[JobRecord] = []
    for path in find_extension_exports(inbox):
        try:
            records = import_extension_file(path, output_dir, processed_dir)
            all_records.extend(records)
            print(f"扩展 JSON  {path.name} -> {len(records)} 条")
            for r in records:
                print(f"  OK  {r.title} @ {r.company} -> {r.id}")
        except Exception as exc:
            print(f"  ERR {path.name}: {exc}")
    return all_records


def rebuild_manifest_from_output(output_dir: Path, manifest_path: Path) -> list[JobRecord]:
    records: list[JobRecord] = []
    for path in sorted(output_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        records.append(
            JobRecord(
                id=data["id"],
                title=data.get("title", ""),
                company=data.get("company", ""),
                salary=data.get("salary", ""),
                jd_body=data.get("jd_body", ""),
                source_url=data.get("source_url", ""),
                source_type=data.get("source_type", ""),
                source_file=data.get("source_file", ""),
                location=data.get("location", ""),
                experience=data.get("experience", ""),
                degree=data.get("degree", ""),
                fetched_at=data.get("fetched_at", ""),
            )
        )

    from boss_jd_batch.html_parser import build_manifest

    if records:
        build_manifest(records, manifest_path)
    return records
