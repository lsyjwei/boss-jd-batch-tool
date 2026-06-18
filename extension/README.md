# Chrome 扩展 — BOSS JD 收集器

## 安装（Edge / Chrome，约 1 分钟）

1. 打开浏览器扩展管理页  
   - Chrome: `chrome://extensions/`  
   - Edge: `edge://extensions/`
2. 开启 **开发者模式**
3. 点击 **加载已解压的扩展程序**
4. 选择本目录：  
   `projects/boss-jd-batch-tool/extension`

## 使用流程

### 收集模式

1. 登录 [BOSS 直聘](https://www.zhipin.com)，打开任意 **岗位详情页**
2. 点击页面右下角 **「＋ 收集 JD」**（或多次浏览不同岗位各点一次）
3. 点击浏览器工具栏上的扩展图标，查看已收集列表
4. 攒够后点击 **「批量导出 JSON」**
5. 在保存对话框中，选择项目的 **`input/inbox/`** 目录保存

### 导入 Cursor 工具

```powershell
cd projects/boss-jd-batch-tool
python -m boss_jd_batch import-all
```

6. 在 Cursor 中 `@output/manifest.json`

## 功能说明

| 功能 | 说明 |
|------|------|
| ＋ 收集 JD | 当前页加入列表（重复岗位自动跳过） |
| 批量导出 JSON | 一次导出全部，格式兼容 CLI |
| 清空列表 | 导出后可清空，开始下一轮 |
| 角标数字 | 工具栏图标显示已收集数量 |

## 导出文件格式

```json
{
  "exported_at": "2026-06-17T...",
  "source": "boss-jd-extension",
  "count": 3,
  "jobs": [
    {
      "job_id": "...",
      "title": "产品经理",
      "company": "某某公司",
      "salary": "20-30K",
      "jd_body": "职位描述...",
      "source_url": "https://www.zhipin.com/job_detail/....html"
    }
  ]
}
```

## 与反爬的关系

扩展在 **你已登录的浏览器** 内读取页面 DOM，不发起匿名爬取，因此不受 BOSS 直链抓取限制。

## 故障排查

- **看不到「＋ 收集 JD」**：确认 URL 含 `/job_detail/`，刷新页面
- **JD 正文为空**：页面未加载完，等 2 秒再点收集
- **导出后 Cursor 无数据**：确认 JSON 保存在 `input/inbox/`，并运行 `import-all`
