# 安卓 APK 打包指南

## 方法一：WSL 2 + Buildozer（推荐）

### 1. 安装 WSL 2

**右键** 点击开始菜单 → **Windows PowerShell (管理员)**，运行：

```powershell
wsl --install -d Ubuntu
```

等待安装完成，重启电脑。首次启动 Ubuntu 时设置用户名和密码。

### 2. 在 WSL 2 中安装 Buildozer

启动 Ubuntu 终端，运行：

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Buildozer 依赖
sudo apt install -y python3-pip python3-dev python3-venv
sudo apt install -y git zip unzip openjdk-11-jdk
sudo apt install -y autoconf libtool pkg-config zlib1g-dev
sudo apt install -y libncurses5-dev libncursesw5-dev libtinfo5
sudo apt install -y cmake libffi-dev libssl-dev

# 安装 Buildozer
pip3 install --user buildozer
```

### 3. 复制项目到 WSL 2

在 Ubuntu 终端中：

```bash
# 挂载 Windows D 盘（WSL 自动挂载到 /mnt/d/）
cd /mnt/d/ai/手机力量举

# 验证文件存在
ls -la
```

### 4. 打包 APK

```bash
# 初始化 buildozer（第一次运行）
buildozer init

# 开始打包（首次会下载 SDK/NDK，约 2-5GB，需耐心等待）
buildozer android debug

# 打包完成后 APK 在 bin/ 目录下
ls -la bin/
```

### 5. 获取 APK

APK 文件在 `D:\ai\手机力量举\bin\PowerLifting-1.0.0-arm64-v8a-debug.apk`
用数据线传到手机安装即可。

---

## 方法二：GitHub Actions 远程打包（不需要本地环境）

> 如果您不想装 WSL，可以把代码上传到 GitHub，用 Actions 免费打包。

步骤：
1. 在 GitHub 创建仓库
2. 推送代码
3. 在仓库根目录创建 `.github/workflows/build.yml`（内容见下方）
4. Actions 会自动打包，完成后下载 APK

```yaml
# .github/workflows/build.yml
name: Build APK
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          sudo apt update
          sudo apt install -y git zip unzip openjdk-11-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
          pip3 install --user buildozer
      - name: Build APK
        run: |
          buildozer android debug
      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: PowerLifting-APK
          path: bin/*.apk
```

---

## 常见问题

**Q: 第一次打包很慢？**
A: 正常，Buildozer 会下载 Android SDK (~1GB)、NDK (~1.5GB) 等工具，仅首次需要。

**Q: C 盘空间不够？**
A: WSL 2 默认安装在 C 盘。如需迁移到 D 盘：
```powershell
# 在 Windows PowerShell 中（管理员）：
wsl --export Ubuntu D:\wsl\ubuntu.tar
wsl --unregister Ubuntu
wsl --import Ubuntu D:\wsl\ubuntu\ D:\wsl\ubuntu.tar
```

**Q: 如何在手机上测试？**
A: 把 APK 传到手机，打开"允许安装未知来源应用"，点击 APK 安装即可。
