param(
    [string]$User = "liuxianzzZZ",
    [string]$Repo = "MyAlarmApp",
    [string]$Token = $env:GITHUB_PAT
)

if (-not $Token -or $Token.Length -lt 8) {
    Write-Error "未检测到 GITHUB_PAT 环境变量，请先执行：`$env:GITHUB_PAT = '<你的GitHub令牌>'`"
    exit 1
}

$originWithToken = "https://$User:$Token@github.com/$User/$Repo.git"
$originClean = "https://github.com/$User/$Repo.git"

try {
    git init | Out-Null
    git config user.name "TraeBot"
    git config user.email "trae-bot@example.com"

    $remotes = git remote
    if ($remotes -match "origin") {
        git remote set-url origin $originWithToken
    } else {
        git remote add origin $originWithToken
    }

    git branch -M main
    git add .
    git commit -m "push: MyAlarmApp sources and workflow" | Out-Null

    try {
        git pull origin main --allow-unrelated-histories
    } catch {
        Write-Output "远端可能为空或不可拉取，继续推送"
    }

    git push -u origin main

    git remote set-url origin $originClean
    Write-Output "推送完成：$User/$Repo。请前往 GitHub → Actions 查看 'Build Android APK' 运行并在 Artifacts 下载 APK。"
} catch {
    Write-Error "推送失败：$($_.Exception.Message)"
    exit 1
}

