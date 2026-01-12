@echo off
chcp 65001 >nul
title StandX Maker Bot - 打包 EXE

echo ============================================
echo       StandX Maker Bot
echo       打包成 Windows EXE
echo ============================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python
    pause
    exit /b 1
)

echo [1/2] 安装 PyInstaller...
pip install pyinstaller -q
if errorlevel 1 (
    echo [错误] PyInstaller 安装失败
    pause
    exit /b 1
)

echo.
echo [2/2] 开始打包...
echo 这可能需要几分钟...
echo.

pyinstaller --name=StandXMakerBot --onefile --console ^
    --hidden-import=gradio ^
    --hidden-import=gradio.routes ^
    --hidden-import=websockets ^
    --hidden-import=eth_account ^
    --hidden-import=nacl.signing ^
    --hidden-import=httpx ^
    --hidden-import=yaml ^
    --hidden-import=plotly ^
    web_ui.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo =====================
echo   打包完成!
echo =====================
echo.
echo 可执行文件: dist\StandXMakerBot.exe
echo.
pause
