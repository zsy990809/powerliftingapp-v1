# WSL 2 + Ubuntu 安装指南（详细图文版）

## 准备工作：检查虚拟化是否开启 ✅

您的电脑已通过检查（AMD Ryzen 5 3600，虚拟化已开启）。
如果以后换电脑，进 BIOS 开启 **SVM（AMD）/ VT-x（Intel）** 即可。

---

## 方法一：命令行安装（推荐，2 分钟）

### 第 1 步：以管理员身份打开 PowerShell

> 一定要点"以管理员身份运行"，否则命令没反应

1. 点击 **开始** 按钮（Windows 图标）
2. 输入 **PowerShell**
3. 右键点击 **Windows PowerShell** → **以管理员身份运行**
4. 弹出 UAC 窗口，点击 **是**

![示意图：右键 PowerShell → 以管理员身份运行](https://learn.microsoft.com/zh-cn/windows/wsl/media/command-line-icons.png)

### 第 2 步：在管理员 PowerShell 中输入以下命令

```powershell
wsl --install -d Ubuntu
```

然后按 **回车**。

### 第 3 步：等待安装

- 会看到进度提示："正在安装: 虚拟机平台" → "正在安装: 适用于 Linux 的 Windows 子系统" → "正在下载: Ubuntu"
- **全程不要关闭窗口**
- 如果提示"需要重新启动"，输入 `y` 回车重启

### 第 4 步：重启后设置 Ubuntu

1. 重启后 Ubuntu 会自动启动（或手动搜索"Ubuntu"打开）
2. 第一次启动会等待解压，**稍等 1-2 分钟**
3. 提示输入 **用户名**（比如 `powerlifter`）
4. 提示输入 **密码**（输入时不显示字符，输完回车即可）
5. 完成！

---

## 方法二：图形界面安装（如果命令行没反应）

### 第 1 步：启用 WSL 功能

1. 按 `Win + R`，输入 `control` 回车 → 打开控制面板
2. 点击 **程序和功能**
3. 点击左侧 **启用或关闭 Windows 功能**
4. 在弹出的列表里，**往下翻**，找到：
   - ✅ **适用于 Linux 的 Windows 子系统**
   - ✅ **虚拟机平台**
5. **把这两个都打勾**，点击确定
6. 等待安装完成，**重启电脑**

### 第 2 步：安装 Ubuntu

1. 重启后，打开 **Microsoft Store**
2. 搜索 **Ubuntu**
3. 选择 **Ubuntu 24.04 LTS**（或最新的 LTS 版本）
4. 点击 **获取** → **安装**
5. 安装完成后，点击 **启动**
6. 第一次启动会等待几分钟，然后设置用户名和密码

---

## 第 5 步：验证安装是否成功

打开 **普通 PowerShell**（不用管理员），运行：

```powershell
wsl -l -v
```

如果看到类似输出：
```
  NAME      STATE           VERSION
* Ubuntu    Running         2
```

说明安装成功！✅

---

## 第 6 步：在 Ubuntu 中安装 Buildozer 并打包 APK

### 进入 Ubuntu 环境

在 PowerShell 中运行：

```powershell
wsl
```

看到提示符变成 `你的用户名@电脑名:~$` 就说明进入 Ubuntu 了。

### 一键安装 Buildozer

复制粘贴下面这一整段到 Ubuntu 终端，按回车：

```bash
cd /mnt/d/ai/手机力量举 && \
sudo apt update && \
sudo apt install -y python3-pip python3-dev git zip unzip openjdk-11-jdk \
autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev \
libtinfo5 cmake libffi-dev libssl-dev && \
pip3 install --user buildozer
```

**过程约 3-5 分钟**，会自动下载安装所有依赖。

### 开始打包 APK

```bash
buildozer android debug
```

**过程约 20-40 分钟**（首次需下载 Android SDK 约 1GB + NDK 约 1.5GB，之后打包只需 5 分钟）。

### 获取 APK

打包完成后：

```bash
ls -la bin/
```

APK 文件在 `bin/` 目录下，文件名类似 `PowerLifting-1.0.0-arm64-v8a-debug.apk`

在 Windows 中也能看到：`D:\ai\手机力量举\bin\PowerLifting-1.0.0-arm64-v8a-debug.apk`

---

## 常见问题

**Q: 安装时说"无法解析服务器的名称或地址"？**
A: 网络问题。换个网络，或者用手机热点试试。

**Q: buildozer 报错找不到 SDK？**
A: 第一次运行会下载 SDK，确保网络通畅，不要中断。

**Q: C 盘空间不够？**
A: WSL 默认安装到 C 盘。如果有需要：
```powershell
# 管理员 PowerShell 中运行：
wsl --export Ubuntu D:\wsl\ubuntu.tar
wsl --unregister Ubuntu
wsl --import Ubuntu D:\wsl\ubuntu\ D:\wsl\ubuntu.tar
```
