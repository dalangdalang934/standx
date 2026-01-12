"""Build script to package StandX Maker Bot as Windows executable."""
import os
import sys
import subprocess

print("=" * 60)
print("  StandX Maker Bot - Windows EXE Builder")
print("=" * 60)
print()

# Check if running on Windows
if sys.platform != "win32":
    print("[警告] 这不是 Windows 系统")
    print("[建议] 请在 Windows 上运行此脚本以获得最佳兼容性")
    print()

# Install PyInstaller
print("[1/3] 安装 PyInstaller...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"])
print("[√] PyInstaller 已安装")
print()

# Build command
print("[2/3] 开始打包...")
print("这可能需要几分钟，请耐心等待...")
print()

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--name=StandXMakerBot",
    "--onefile",
    "--console",
    "--hidden-import=gradio",
    "--hidden-import=gradio.routes",
    "--hidden-import=gradio.templates",
    "--hidden-import=websockets",
    "--hidden-import=eth_account",
    "--hidden-import=nacl.signing",
    "--hidden-import=httpx",
    "--hidden-import=yaml",
    "--hidden-import=plotly",
    "web_ui.py",
]

try:
    subprocess.check_call(cmd)
    print()
    print("[3/3] 打包完成!")
    print()
    print("=" * 60)
    print("  可执行文件位置: dist/StandXMakerBot.exe")
    print("=" * 60)
    print()
    print("使用说明:")
    print("1. 双击 StandXMakerBot.exe 启动")
    print("2. 浏览器会自动打开控制面板")
    print("3. 配置参数后点击启动")
    print()
except subprocess.CalledProcessError as e:
    print()
    print(f"[错误] 打包失败: {e}")
    sys.exit(1)
