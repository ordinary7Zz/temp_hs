## HS

### 开发

1. 创建虚拟环境

安装miniconda

进入虚拟环境

```powershell
conda create -n hs python=3.12
conda activate hs
```

2. 安装依赖

```powershell
pip install -r ./requirements.txt
```

### 构建可执行文件PyInstaller

生产版本：

- 输出到项目目录下的`out`文件夹中，`out/dist/main`为最终交付文件夹，`out/_build`为构建时临时文件夹。

```powershell
pyinstaller `
  --onedir --contents-directory "." `
  --icon UIstyles\images\app_logo.ico `
  --exclude-module tests --exclude-module pytest `
  --add-data "UIstyles:UIstyles" `
  --collect-data PyQt6 `
  --collect-data reportlab `
  --collect-data openpyxl `
  --version-file version_info.txt `
  --distpath "out/dist" --workpath "out/_build" `
  --clean --noconfirm -F --windowed -y main.py
```

DEBUG版本：

- 开启终端显示运行日志。
- 输出目录为`debug_out`

```powershell
pyinstaller `
  --onedir --contents-directory "." `
  --console `
  --icon UIstyles\images\app_logo.ico `
  --exclude-module tests --exclude-module pytest `
  --add-data "UIstyles:UIstyles" `
  --collect-data PyQt6 `
  --collect-data reportlab `
  --collect-data openpyxl `
  --version-file version_info.txt `
  --distpath "debug_out/dist" --workpath "debug_out/_build" `
  -y main.py
```

### 安装包构建

将最终交付文件夹`out/dist/main`打包为安装向导。

下载Inno Setup：https://jrsoftware.org/isdl.php

安装的时候勾选，关联iss格式。

在文件管理器explorer中打开项目文件夹，直接双击运行`build-setup.iss`