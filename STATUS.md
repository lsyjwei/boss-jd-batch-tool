# STATUS — BOSS直聘职位信息拉取小工具

**最后更新**：2026-06-17  
**当前阶段**：shipped（v0.2 扩展收集模式）

## v0.2 交付

- Chrome 扩展：`extension/` — 收集模式 + 批量导出 JSON
- CLI：`import-all` 支持 inbox/*.json
- 验收：扩展 JSON 样例导入通过；3 条真实 HTML JD 仍可用

## 用户使用（推荐）

1. 加载扩展 → 岗位页「＋ 收集 JD」→ 弹窗「批量导出」→ 存 `input/inbox/`
2. `python -m boss_jd_batch import-all`
3. `@output/manifest.json`

## 里程碑

| Milestone | 状态 |
|-----------|------|
| M1 HTML | done |
| M3 inbox | done |
| M4 ship | done |
| **M5 扩展收集模式** | **done** |
| M2 截图 OCR | deferred |
