@echo off
chcp 65001 >nul
echo ========================================
echo 检查 MySQL 服务状态
echo ========================================
echo.

echo [检查 MySQL 服务...]
echo.

sc query MySQL80 >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ 找到 MySQL80 服务
    sc query MySQL80 | findstr "STATE"
    echo.
    echo 如果状态显示 "RUNNING"，说明服务正在运行
    echo 如果状态显示 "STOPPED"，需要启动服务
) else (
    sc query MySQL >nul 2>&1
    if %errorlevel% == 0 (
        echo ✅ 找到 MySQL 服务
        sc query MySQL | findstr "STATE"
        echo.
        echo 如果状态显示 "RUNNING"，说明服务正在运行
        echo 如果状态显示 "STOPPED"，需要启动服务
    ) else (
        echo ❌ 未找到 MySQL 服务
        echo.
        echo 可能的原因：
        echo 1. MySQL 未安装
        echo 2. 服务名称不同
        echo.
        echo 请检查服务管理器（services.msc）中的 MySQL 相关服务
    )
)

echo.
echo ========================================
echo 提示：
echo ========================================
echo 1. 如果服务未运行，可以：
echo    - 在服务管理器中右键点击 MySQL 服务 → 启动
echo    - 或运行命令：net start MySQL80
echo.
echo 2. 如果忘记密码，请参考下面的重置密码步骤
echo.
pause

