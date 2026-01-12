# 打包 Windows EXE 说明

## 方法一：使用 GitHub Actions（推荐，自动构建）

1. **将代码上传到 GitHub**
   - 创建一个新仓库
   - 上传所有代码

2. **运行构建**
   - 进入 GitHub 仓库页面
   - 点击 "Actions" 标签
   - 选择 "Build Windows EXE" workflow
   - 点击 "Run workflow" 按钮

3. **下载 EXE**
   - 构建完成后（约 2-3 分钟）
   - 在 Actions 页面找到构建记录
   - 下载 "StandXMakerBot-Windows" artifact
   - 解压后得到 `StandXMakerBot.exe`

## 方法二：在 Windows 上手动打包

1. 确保已安装 Python 3.10+
2. 双击运行 `build.bat`
3. 等待打包完成
4. 在 `dist` 文件夹中找到 `StandXMakerBot.exe`

## EXE 使用说明

- 双击 `StandXMakerBot.exe` 启动
- 浏览器会自动打开控制面板
- 配置参数后点击启动即可交易

## 注意事项

1. 首次运行可能需要 5-10 秒启动时间
2. Windows 可能会弹出安全警告，点击"仍要运行"即可
3. 杀毒软件可能会误报，需要添加信任
