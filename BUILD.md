# 打包成 Windows .exe

TH 版打包有三条路，按你手头的环境选：

---

## 路线 A：GitHub Actions 云端打包（推荐）

不需要 Windows 机器，5 分钟出包，免费。

### 一次设置

1. 在你的 GitHub 账号下建一个新仓库（公开或私有都行）
2. 把 `tk-th-converter/` 下所有文件 push 上去（看 `.gitignore`，别把 `config.json` 和 `.DS_Store` 推上去）
3. 确认 `.github/workflows/build-windows.yml` 在仓库里

### 触发打包

任意一次 `git push` 到 `main` 分支就触发 Actions。

### 拿产物

1. GitHub → 你的仓库 → **Actions** 页面
2. 点最新的成功 run（绿色对勾）
3. 滚到页面底部 **Artifacts** 区
4. 下载 `TK-TH-Converter-windows.zip`
5. 解压 → `TK-TH-Converter.exe` + `assets/`

把这两个文件一起发给客户即可，客户**不需要装任何运行时**。

### 自定义名字

- exe 名 → 改 `TK-TH-Converter.spec` 里的 `APP_NAME`
- zip 名 → 改 `.github/workflows/build-windows.yml` 里 `artifact name` 一行

---

## 路线 B：本地 Windows 机器打包

适合你有 Windows 电脑 + 不依赖 GitHub 的情况。

### 准备

1. 装 **Python 3.11+**（[python.org](https://www.python.org/downloads/)）
   - 安装时**勾选** `tcl/tk and IDLE`
   - 安装时**勾选** `Add python.exe to PATH`
2. 把 `tk-th-converter/` 整个文件夹拷到 Windows 上
   - 路径**不要含中文或空格**，例如放 `C:\tools\tk-th-converter\`

### 跑脚本

双击 `build_windows.bat`。

脚本会做：
1. 项目下创建 `.venv\`（隔离 Python 环境）
2. 装 `requirements.txt` 依赖 + `pyinstaller`
3. 跑 `pyinstaller --noconfirm TK-TH-Converter.spec`
4. 把 `assets\` 复制到 `dist\` 旁边
5. 弹窗显示构建完成

### 产物

`dist\TK-TH-Converter.exe`（约 12 MB 单文件）+ `dist\assets\`。

> ⚠️ 如果 exe 启动报「找不到模板」，说明第 4 步复制失败。手动把项目里的 `assets\` 整个拷到 `dist\` 旁边即可。

---

## 路线 C：开发模式直接跑（不出 exe）

开发时本地测试用：

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
python -m app.main
```

`requirements.txt` 只有 `openpyxl` 一个硬依赖；`tkinter` 随 Python 自带；`tkinterdnd2` 可选（装了支持文件拖放，没装自动降级到点击选文件）。

---

## 常见坑

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| Actions run 失败：`tags` 解析报错 | yaml 把 `on:` 当 bool 了 | 已修：用 `"on":` 加双引号 |
| exe 启动崩 `convert_source() got an unexpected keyword argument 'log'` | worker 注入 callback 但函数没接 | 已修：`convert_source(log=None, ...)` |
| 改了设置不生效 | 旧 config.json 没刷新 | 删掉 exe 同目录的 `config.json` 重启 |
| exe 启动找不到 `assets/` | `datas=` 没加或路径错 | `TK-TH-Converter.spec` 已配好 |
| 模板报错「missing Template sheet」 | 模板损坏或被替换 | 重新下载 TH V5.0.2 模板覆盖 `assets/batch-product-source.xlsx` |
| exe 启动卡白屏 | Windows Defender 误报 | 给 exe 加白名单或申请代码签名证书 |

---

## 文件名速查

| 用途 | 文件 |
| --- | --- |
| PyInstaller 打包配置 | `TK-TH-Converter.spec` |
| 本地 Windows 一键脚本 | `build_windows.bat` |
| 云端打包 | `.github/workflows/build-windows.yml` |
| 依赖清单 | `requirements.txt` |
| 用户设置（首次运行生成） | `config.json` |
| TH 卖家中心模板 | `assets/batch-product-source.xlsx` |
| 默认尺码图 | `assets/default_size_chart.png` |