@echo off
chcp 65001 >nul
title StandX Maker Bot

echo ============================================
echo       StandX Maker Bot
echo       自动化做市商交易机器人
echo ============================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 检查依赖...
pip show gradio >nul 2>&1
if errorlevel 1 (
    echo [2/3] 首次运行，正在安装依赖...
    pip install -r requirements.txt plotly -q
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo [√] 依赖已安装
)

echo.
echo [3/3] 启动 Web UI...
echo.
echo Bot 将在浏览器中自动打开
echo 按 Ctrl+C 停止运行
echo ============================================
echo.

python web_ui.py

pause
