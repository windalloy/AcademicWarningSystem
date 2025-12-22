@echo off
chcp 65001 >nul
echo ========================================
echo 安装 Python 依赖包
echo ========================================
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo 安装失败！请检查网络连接或使用国内镜像：
    echo pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo.
) else (
    echo.
    echo 安装成功！
    echo.
)

pause

