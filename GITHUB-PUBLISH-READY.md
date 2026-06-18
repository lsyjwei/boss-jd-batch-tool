# boss-jd-batch-tool — GitHub 发布就绪清单

> 本地准备已完成。**push 需你明确授权后执行。**

## 已完成

- [x] `.gitignore`（排除 input/inbox、output、.env）
- [x] `LICENSE`（MIT）
- [x] `README.md`（含 clone 快速开始、免责声明）
- [x] `PROJECTS.md` GitHub=未发布、小红书=草稿
- [x] `发布日历.md` 已排期

## 你确认后执行（PowerShell）

将 `<your-user>` 换成你的 GitHub 用户名：

```powershell
cd "F:\01-工作\05-作品集\08-coding试验田\projects\boss-jd-batch-tool"
git init
git add .
git commit -m "Initial public release: BOSS JD batch tool for Cursor"
gh repo create boss-jd-batch-tool --public --source=. --remote=origin --push
gh release create v0.1.0 --title "v0.1.0 MVP" --notes "Chrome extension + JSON inbox + Cursor import"
```

## 发布后

1. 更新 `PROJECTS.md` GitHub 列为 repo URL
2. 更新 `发布日历.md` 状态为 published
3. 说 `@xiaohongshu-short boss-jd-batch-tool` 定稿小红书（或编辑 `笔记/内容运营/草稿/` 下已有草稿）

## 前置条件

- 已安装 [GitHub CLI](https://cli.github.com/) 且 `gh auth login`
- 可选：恢复 GitHub MCP（见 `笔记/Cursor配置说明.md` §九）
