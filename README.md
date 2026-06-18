# BOSS 直聘 JD 批量导入

将 BOSS 岗位批量导入 Cursor，支持 **Chrome 扩展收集模式**（推荐）和 HTML 另存为两种入口。

> 转行作品集工具 · 配合 Cursor Agent 做 JD 对比分析

## 环境

- Python 3.10+：`pip install -r requirements.txt`
- Chrome / Edge 浏览器

## 快速开始

```powershell
git clone https://github.com/<your-user>/boss-jd-batch-tool.git
cd boss-jd-batch-tool
pip install -r requirements.txt
```

---

## 推荐：扩展收集模式（v0.2）

### 1. 安装扩展（一次性）

1. 打开 `chrome://extensions/` 或 `edge://extensions/`
2. 开启 **开发者模式** → **加载已解压的扩展程序**
3. 选择目录：`projects/boss-jd-batch-tool/extension`

详细说明见 [extension/README.md](extension/README.md)

### 2. 收集岗位

1. 登录 BOSS 直聘，逐个打开岗位详情页
2. 每页点击右下角 **「＋ 收集 JD」**
3. 点击扩展图标 → **批量导出 JSON** → 保存到 **`input/inbox/`**

### 3. 导入 Cursor

```powershell
cd projects/boss-jd-batch-tool
python -m boss_jd_batch import-all
```

```
@output/manifest.json 帮我对比这几个岗位
```

---

## 备选：HTML 另存为

1. Ctrl+S 另存为 → 拖入 `input/inbox/`
2. `python -m boss_jd_batch import-all`（自动重命名为 `「职位」_公司.html`）

---

## 命令

| 命令 | 作用 |
|------|------|
| `import-all` | **推荐**：inbox（JSON/HTML）+ 解析 + manifest |
| `import-extension` | 仅导入 inbox/*.json |
| `import-html` | 仅解析 html/ |
| `process-inbox` | 仅 HTML 重命名入库 |

---

## 目录

```
boss-jd-batch-tool/
├── extension/          # Chrome 扩展（收集模式）
├── input/inbox/        # 扩展导出的 JSON 或 HTML 入口
├── input/html/         # 规范命名存档
├── output/manifest.json
└── output/jobs/
```

---

## 版本

- **v0.2** — Chrome 扩展收集模式 + 批量导出 JSON（2026-06-17）
- v0.1 — HTML inbox + 解析

## License

MIT — 见 [LICENSE](LICENSE)

## 免责声明

本工具仅供个人学习与求职整理使用。请遵守 BOSS 直聘服务条款，勿用于爬取或商业用途。
