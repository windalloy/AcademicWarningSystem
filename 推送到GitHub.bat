@echo off
chcp 65001 >nul
echo ========================================
echo 推送到 GitHub 仓库
echo ========================================
echo.
echo 目标仓库: https://github.com/windalloy/AcademicWarningSystem
echo.

REM 检查是否已初始化Git
if exist .git (
    echo [信息] Git 仓库已存在
    git status
    echo.
    echo 是否继续推送？(Y/N)
    set /p choice=
    if /i not "%choice%"=="Y" (
        echo 已取消
        pause
        exit /b
    )
) else (
    echo [步骤1] 初始化 Git 仓库...
    git init
    if errorlevel 1 (
        echo [错误] Git 初始化失败，请确保已安装 Git
        pause
        exit /b
    )
    echo [成功] Git 仓库初始化完成
    echo.
)

echo [步骤2] 添加所有文件...
git add .
if errorlevel 1 (
    echo [错误] 添加文件失败
    pause
    exit /b
)
echo [成功] 文件已添加到暂存区
echo.

echo [步骤3] 提交代码...
git commit -m "初始提交：大学生学业预警与成绩分析系统"
if errorlevel 1 (
    echo [警告] 提交失败，可能是没有更改或已提交
)
echo.

echo [步骤4] 检查远程仓库...
git remote -v | findstr "origin" >nul
if errorlevel 1 (
    echo [信息] 添加远程仓库...
    git remote add origin https://github.com/windalloy/AcademicWarningSystem.git
    if errorlevel 1 (
        echo [错误] 添加远程仓库失败
        pause
        exit /b
    )
    echo [成功] 远程仓库已添加
) else (
    echo [信息] 远程仓库已存在
    git remote set-url origin https://github.com/windalloy/AcademicWarningSystem.git
)
echo.

echo [步骤5] 设置主分支...
git branch -M main
echo.

echo [步骤6] 推送到 GitHub...
echo.
echo ⚠️  注意：如果这是第一次推送，可能需要身份验证
echo     - 如果提示输入用户名，输入您的 GitHub 用户名
echo     - 如果提示输入密码，使用 Personal Access Token（不是GitHub密码）
echo.
echo 生成 Token 的方法：
echo 1. 访问 https://github.com/settings/tokens
echo 2. 点击 "Generate new token (classic)"
echo 3. 勾选 "repo" 权限
echo 4. 生成后复制 token，作为密码使用
echo.
pause

git push -u origin main

if errorlevel 1 (
    echo.
    echo [错误] 推送失败
    echo.
    echo 可能的原因：
    echo 1. 需要身份验证（使用 Personal Access Token）
    echo 2. 远程仓库已有内容，需要先拉取
    echo 3. 网络连接问题
    echo.
    echo 如果远程仓库已有内容，请运行：
    echo   git pull origin main --allow-unrelated-histories
    echo   git push -u origin main
    echo.
) else (
    echo.
    echo ========================================
    echo [成功] 代码已推送到 GitHub！
    echo ========================================
    echo.
    echo 访问以下地址查看：
    echo https://github.com/windalloy/AcademicWarningSystem
    echo.
    echo 注意：ER图.md 中的 Mermaid 图形会自动渲染显示
    echo.
)

pause

