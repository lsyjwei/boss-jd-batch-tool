# boss-jd-batch-tool 公开发布脚本
# 前置：在 PowerShell 执行一次 gh auth login

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "检查 gh 登录状态..."
gh auth status
if ($LASTEXITCODE -ne 0) {
    Write-Host "请先运行: gh auth login"
    exit 1
}

$owner = (gh api user -q .login)
Write-Host "将以用户 $owner 创建公开仓库 boss-jd-batch-tool"

$hasOrigin = git remote 2>$null | Select-String -Pattern '^origin$' -Quiet
if ($hasOrigin) {
    Write-Host "remote origin 已存在，跳过 gh repo create"
    git push -u origin master
} else {
    gh repo create boss-jd-batch-tool --public --source=. --remote=origin --push --description "BOSS JD batch collector for Cursor"
}

gh release create v0.1.0 --title "v0.1.0 MVP" --notes "Chrome extension + JSON inbox + Cursor import"

$repoUrl = "https://github.com/$owner/boss-jd-batch-tool"
Write-Host ""
Write-Host "发布完成: $repoUrl"
Write-Host "请更新 PROJECTS.md GitHub 列与 发布日历.md"
