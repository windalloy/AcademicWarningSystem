# GitHub 推送指南

## 一、GitHub 支持 Mermaid

✅ **是的，GitHub 原生支持 Mermaid 语法！**

在 GitHub 上查看 `ER图.md` 时，Mermaid 代码块会自动渲染为图形，无需任何插件。

## 二、推送代码到 GitHub

### 步骤1：初始化 Git 仓库

打开命令提示符或 PowerShell，进入项目目录：

```bash
cd D:\py\gradeanal
```

初始化 Git 仓库：

```bash
git init
```

### 步骤2：添加所有文件

```bash
git add .
```

### 步骤3：提交代码

```bash
git commit -m "初始提交：大学生学业预警与成绩分析系统"
```

### 步骤4：添加远程仓库

```bash
git remote add origin https://github.com/windalloy/AcademicWarningSystem.git
```

### 步骤5：推送代码

```bash
git branch -M main
git push -u origin main
```

## 三、如果遇到问题

### 问题1：需要身份验证

如果提示需要登录，可以使用：

**方法1：使用 Personal Access Token**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 生成新 token，勾选 `repo` 权限
3. 推送时使用 token 作为密码

**方法2：使用 GitHub CLI**
```bash
gh auth login
```

### 问题2：远程仓库已有内容

如果远程仓库不是空的，需要先拉取：

```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### 问题3：推送被拒绝

如果提示需要先拉取：

```bash
git pull origin main --rebase
git push -u origin main
```

## 四、后续更新代码

每次修改后：

```bash
git add .
git commit -m "描述你的修改"
git push
```

## 五、验证推送成功

访问 https://github.com/windalloy/AcademicWarningSystem 查看：
- ✅ 所有文件都已上传
- ✅ `ER图.md` 中的 Mermaid 图形会自动渲染
- ✅ README.md 正常显示

## 六、项目文件说明

推送的文件包括：
- ✅ Python 源代码（`main.py`, `database/`, `gui/`）
- ✅ SQL 脚本（`AcademicWarningSystem.sql`）
- ✅ 配置文件（`requirements.txt`）
- ✅ 文档（`README.md`, `ER图.md`, 各种说明文档）
- ✅ 批处理文件（`启动程序.bat`, `安装依赖.bat`）

不会推送的文件（已在 `.gitignore` 中）：
- ❌ `__pycache__/`（Python 缓存）
- ❌ `*.doc`（Word 文档）
- ❌ 虚拟环境文件夹

## 七、快速命令（一键推送）

如果已经配置好 Git，可以使用：

```bash
cd D:\py\gradeanal
git init
git add .
git commit -m "初始提交：大学生学业预警与成绩分析系统"
git remote add origin https://github.com/windalloy/AcademicWarningSystem.git
git branch -M main
git push -u origin main
```

