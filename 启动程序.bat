@echo off
chcp 65001 >nul
echo ========================================
echo 大学生学业预警与成绩分析系统
echo ========================================
echo.
echo 正在启动程序...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo 程序运行出错！
    echo 请检查：
    echo 1. 是否已安装 Python 3.7 或更高版本
    echo 2. 是否已安装依赖：pip install -r requirements.txt
    echo 3. MySQL 服务是否已启动
    echo.
    pause
)

