@echo off
chcp 65001 >nul
title StandX Maker Bot - 安装依赖

echo ============================================
echo       StandX Maker Bot
echo       安装依赖
echo ============================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python
    echo.
    echo 请先安装 Python 3.10+
    echo 下载: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [√] Python 已安装
echo.
echo 正在安装依赖包...
echo --------------------

pip install -r requirements.txt -q

if errorlevel 1 (
    echo.
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo =====================
echo   安装完成!
echo =====================
echo.
echo 现在可以双击 start.bat 启动程序
echo.
pause
