# PLAN — BOSS直聘职位信息拉取小工具

> 由子项目负责人维护。每个 milestone 须有可验证的完成标准。

## 技术路线（规划决策）

| 输入 | MVP 方案 | 说明 |
|------|----------|------|
| 用户保存的 HTML | BeautifulSoup 解析 BOSS 岗位页 DOM | 合规、不依赖登录；用户浏览器「另存为网页」放入 `input/html/` |
| 批量截图 | OCR（pytesseract 或 easyocr）+ 字段启发式提取 | 用户将截图放入 `input/screenshots/` |
| 链接列表 | `input/links.txt` 批量登记 | 不登录爬取；生成 manifest + 提示用户补 HTML/截图；可选尝试公开 GET（失败则跳过） |

**输出**：`output/jobs/<id>.md` + `output/jobs/<id>.json` + `output/manifest.json`（汇总索引，便于 Cursor `@output/manifest.json`）

**栈**：Python 3 + CLI（`python -m boss_jd_batch` 或 `python batch_import.py`），无 Web UI。

## 里程碑

### M1 — HTML 批量解析管道

- **目标**：从 `input/html/` 批量读取用户保存的 BOSS 岗位页，输出结构化 Markdown/JSON
- **验收**：
  - 放置 ≥2 个样例 HTML 可一次跑通
  - 每条含：标题、公司、薪资（若有）、JD 正文、来源（文件名或 meta）
  - 生成 `output/manifest.json`
- **Subagent 分工**：
  - explore：quick 调研 BOSS 岗位页 DOM 结构（样例 HTML 或公开文档）
  - generalPurpose：实现解析模块 + CLI 子命令 `import-html`
  - shell：跑通 CLI 并验证输出
- **状态**：done

### M2 — 截图批量 OCR

- **目标**：从 `input/screenshots/` 批量 OCR，提取同样字段写入 `output/jobs/`
- **验收**：
  - ≥2 张截图批量处理
  - 字段与 M1 输出 schema 一致
  - CLI 子命令 `import-screenshots`
- **Subagent 分工**：
  - generalPurpose：OCR 集成 + 字段提取
  - shell：安装 OCR 依赖并验证
- **状态**：pending

### M3 — inbox 工作流 + import-all

- **目标**：`input/inbox/` 入库并重命名；`import-all` 统一处理
- **验收**：
  - [x] inbox 内任意文件名 HTML → `「职位」_公司.html`
  - [x] 链接 `.txt` 登记至 `links.txt` / `pending-links.json`
  - [x] `import-all` 一键 inbox + 解析
- **状态**：done

### M4 — README 与 ship 审查

- **目标**：README（用法、目录约定、输入输出示例）；对照 BRIEF 验收
- **验收**：
  - README 含 copy-paste 示例命令
  - Cursor `@output/manifest.json` 可读性说明
  - Lead 审查 ship / iterate
- **Subagent 分工**：
  - generalPurpose：README
  - bugbot（可选）：脚本审查
- **状态**：done

## 任务 backlog

- [x] HTML 解析器 + CLI
- [x] inbox 工作流 + import-all
- [x] README + ship 审查
- [ ] M2 截图 OCR（迭代）

## 风险与决策

| 项 | 说明 | 决策 |
|----|------|------|
| BOSS 反爬 / 登录 | 直链抓取不可靠 | **不登录爬取**；链接仅 manifest；内容来自 HTML/截图 |
| OCR 精度 | 截图排版复杂 | MVP 先全文 OCR + 正则/关键词抽字段；不够再迭代 |
| DOM 变更 | BOSS 改版 | 解析器模块化；样例 HTML 放 `fixtures/` |
| 依赖重量 | easyocr 较大 | 优先 pytesseract；Windows 需用户装 Tesseract |

## 输出 Schema（草案）

```json
{
  "id": "job-001",
  "title": "产品经理",
  "company": "某某科技",
  "salary": "15-25K",
  "jd_body": "...",
  "source_url": "https://www.zhipin.com/job_detail/...",
  "source_type": "html|screenshot|link",
  "source_file": "input/html/xxx.html",
  "fetched_at": "2026-06-17T12:00:00"
}
```
