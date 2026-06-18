# 新岗位入口

## 推荐：Chrome 扩展（收集模式）

1. 安装 `extension/` 扩展（见 extension/README.md）
2. BOSS 岗位页点 **「＋ 收集 JD」**，攒够后 **批量导出 JSON**
3. 导出文件保存到 **本目录** `input/inbox/`
4. 运行 `python -m boss_jd_batch import-all`

## 备选：HTML 另存为

Ctrl+S 另存为 → 拖入本目录 → `import-all`

已处理的扩展 JSON 会移到 `inbox/processed/`。
