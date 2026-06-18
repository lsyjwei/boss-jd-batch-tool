"""BOSS 直聘 saved HTML parser."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

SAVED_URL_RE = re.compile(
    r"<!--\s*saved from url=\(\d+\)(https?://[^\s]+)\s*-->", re.IGNORECASE
)
JOB_INFO_RE = re.compile(
    r"var\s+_jobInfo\s*=\s*\{([^}]+)\}", re.DOTALL
)
JOB_FIELD_RE = re.compile(
    r"(job_name|job_salary|company|job_id)\s*:\s*['\"]([^'\"]*)['\"]"
)


@dataclass
class JobRecord:
    id: str
    title: str
    company: str
    salary: str
    jd_body: str
    source_url: str
    source_type: str
    source_file: str
    location: str = ""
    experience: str = ""
    degree: str = ""
    fetched_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _slugify(text: str, max_len: int = 40) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text.strip(), flags=re.UNICODE)
    slug = re.sub(r"-+", "-", slug).strip("-").lower()
    return (slug[:max_len] or "job").strip("-")


def _extract_saved_url(html: str) -> str:
    match = SAVED_URL_RE.search(html)
    if match:
        return match.group(1).split("?")[0] if "?" in match.group(1) else match.group(1)
    return ""


def _extract_job_info(html: str) -> dict[str, str]:
    info: dict[str, str] = {}
    block = JOB_INFO_RE.search(html)
    if not block:
        return info
    for key, value in JOB_FIELD_RE.findall(block.group(1)):
        info[key] = value
    return info


def _br_to_newlines(element) -> str:
    for br in element.find_all("br"):
        br.replace_with("\n")
    text = element.get_text("\n", strip=True)
    return re.sub(r"\n{3,}", "\n\n", text)


def _extract_jd_body(soup: BeautifulSoup) -> str:
    for section in soup.select(".job-detail-section"):
        if section.select_one(".job-detail-company, .more-job-section, .security-box"):
            continue
        text_el = section.select_one(".job-sec-text")
        if not text_el:
            continue
        text = _br_to_newlines(text_el)
        if "职位描述" in text or len(text) > 80:
            return text
    return ""


def _extract_meta_fields(soup: BeautifulSoup) -> tuple[str, str, str]:
    location = experience = degree = ""
    city = soup.select_one(".text-city")
    if city:
        location = city.get_text(strip=True)
    exp = soup.select_one(".text-experiece, .text-experience")
    if exp:
        experience = exp.get_text(strip=True)
    deg = soup.select_one(".text-degree")
    if deg:
        degree = deg.get_text(strip=True)
    return location, experience, degree


def parse_html_file(path: Path) -> JobRecord:
    html = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")

    info = _extract_job_info(html)
    source_url = _extract_saved_url(html)
    if not source_url:
        canonical = soup.find("link", rel="canonical")
        if canonical and canonical.get("href"):
            source_url = canonical["href"]

    title = info.get("job_name", "")
    if not title:
        h1 = soup.select_one(".name h1, h1[title]")
        title = (h1.get("title") or h1.get_text(strip=True)) if h1 else ""

    salary = info.get("job_salary", "")
    if not salary:
        sal = soup.select_one(".name .salary, span.salary")
        salary = sal.get_text(strip=True) if sal else ""

    company = info.get("company", "")
    if not company:
        comp = soup.select_one(".sider-company a[title], .detail-op .info")
        if comp:
            company = comp.get("title") or comp.get_text(strip=True).split("\n")[0]

    jd_body = _extract_jd_body(soup)
    location, experience, degree = _extract_meta_fields(soup)

    job_id = info.get("job_id") or _slugify(title)
    record_id = f"job-{_slugify(job_id or title)}"

    return JobRecord(
        id=record_id,
        title=title,
        company=company,
        salary=salary,
        jd_body=jd_body,
        source_url=source_url,
        source_type="html",
        source_file=str(path.as_posix()),
        location=location,
        experience=experience,
        degree=degree,
        fetched_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    )


def find_html_inputs(input_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(input_dir.rglob("*.html")):
        if "_files" in path.parts:
            continue
        if path.name.startswith("saved_resource"):
            continue
        files.append(path)
    return files


def record_to_markdown(record: JobRecord) -> str:
    lines = [
        f"# {record.title}",
        "",
        f"- **公司**：{record.company or '—'}",
        f"- **薪资**：{record.salary or '—'}",
        f"- **地点**：{record.location or '—'}",
        f"- **经验**：{record.experience or '—'}",
        f"- **学历**：{record.degree or '—'}",
        f"- **来源**：[{record.source_url or '本地 HTML'}]({record.source_url})" if record.source_url else "- **来源**：本地 HTML",
        f"- **源文件**：`{record.source_file}`",
        "",
        "## 职位描述",
        "",
        record.jd_body or "（未能解析 JD 正文）",
    ]
    return "\n".join(lines)


def write_outputs(record: JobRecord, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{record.id}.json"
    md_path = output_dir / f"{record.id}.md"
    json_path.write_text(
        json.dumps(record.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    md_path.write_text(record_to_markdown(record), encoding="utf-8")


def build_manifest(records: list[JobRecord], manifest_path: Path) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "count": len(records),
        "jobs": [
            {
                "id": r.id,
                "title": r.title,
                "company": r.company,
                "salary": r.salary,
                "source_url": r.source_url,
                "md_file": f"output/jobs/{r.id}.md",
                "json_file": f"output/jobs/{r.id}.json",
            }
            for r in records
        ],
    }
    manifest_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
