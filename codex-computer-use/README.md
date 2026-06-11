# Codex Computer Use

Windows 版 Codex Desktop **Computer Use / 电脑操控修复 Skill**。

这个仓库用于诊断和修复 Windows 上 Codex Desktop 的 Computer Use、Any App、内置浏览器、Google Chrome 控制、bundled plugin cache、native messaging host 等典型问题。它的目标不是盲目重装，而是让 Codex 按可验证的顺序定位问题，并在本机直接修好。

Keywords: Codex Desktop, Computer Use, Windows, Any App, Chrome control, browser use, native messaging, OpenAI Codex.

## 能解决什么

- Codex Desktop 里 **Computer Use / 电脑操控入口不可用**
- **Any App / 任意应用** 开关存在但实际不能控制桌面应用
- `openai-bundled` marketplace mirror 损坏或缺失
- `browser` / `chrome` / `computer-use` bundled plugin cache 缺失
- WindowsApps 包内文件带 `Application Protected`，导致 `robocopy`、`Copy-Item` 失败或卡住
- Chrome 扩展安装失败、显示未连接、native messaging host 缺失
- Chrome 扩展装到了错误 Profile，Codex 选中的 Profile 和实际安装 Profile 不一致
- Store/MSIX 包里的 `codex.exe`、`node.exe`、`node_repl.exe` 外部启动 `Access is denied`
- Windows sandbox 初始化失败，例如 elevation 相关的 `740` 错误

## 核心优点

- **诊断优先**：先验证 Codex 包、config、插件镜像、缓存、Chrome host、注册表、Profile，再决定修复动作
- **本地优先修复**：优先修 `~/.codex` 下的配置和缓存，不直接改 WindowsApps
- **能处理 WindowsApps 保护文件**：使用 byte-stream copy 复制受保护包资源，避开 `robocopy` / `Copy-Item` 在部分机器上的失败点
- **自动重建 bundled cache**：恢复 `openai-bundled` marketplace mirror，并补齐 `browser`、`chrome`、`computer-use` 缓存
- **自动修 Chrome 控制链路**：重建 native messaging manifest、HKCU registry、host runtime，并检测 Profile mismatch
- **保留兜底路径**：只有在本地修复无法解决时，才考虑 MSIX / ASAR patch

## 安装

在 PowerShell 中执行：

```powershell
$dest = Join-Path $env:USERPROFILE ".codex\skills\codex-computer-use"
if (Test-Path -LiteralPath $dest) {
  Remove-Item -LiteralPath $dest -Recurse -Force
}
git clone https://github.com/zhanyuyue7-dotcom/codex-computer-use.git $dest
```

安装后重启 Codex Desktop，或重新打开一个 Codex 会话。

## 使用

在 Codex 里直接说：

```text
使用 $codex-computer-use 检查并修复这台 Windows 电脑上的 Codex Computer Use / Chrome 控制问题
```

Codex 会按 Skill 里的流程自动检查：

1. 当前 Codex Desktop 包版本和安装方式
2. `~/.codex/config.toml` 的 Computer Use、plugin、sandbox 配置
3. bundled marketplace mirror 和 plugin cache
4. Browser / Chrome / Computer Use 插件是否完整
5. Chrome native messaging manifest、注册表、host runtime
6. Chrome Profile 是否和 Codex 设置一致
7. 是否需要最后兜底的 MSIX / ASAR patch

## 常用手动命令

只验证 Computer Use 本地链路：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\codex-computer-use\scripts\install-computer-use-local.ps1" -VerifyOnly
```

修复并验证 Computer Use 本地链路：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\codex-computer-use\scripts\install-computer-use-local.ps1"
```

修复 Chrome 控制链路：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\codex-computer-use\scripts\repair-chrome-control.ps1"
```

打开 Chrome 扩展安装页并检查 Profile：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\codex-computer-use\scripts\repair-chrome-control.ps1" -OpenExtensionPage
```

## 安全边界

- 不直接修改 `C:\Program Files\WindowsApps`
- 不默认卸载或重装 Codex Desktop
- 修改 `~/.codex/config.toml` 前会备份
- MSIX / ASAR patch 是最后兜底，不是默认路径
- 这是社区本地修复 Skill，不是 OpenAI 官方支持渠道

## 项目结构

```text
codex-computer-use/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   └── restriction-debug-cases.md
└── scripts/
    ├── install-computer-use-local.ps1
    ├── manage-codex-backups.ps1
    ├── patch_codex_fast_mode_windows_msix.ps1
    ├── repair-chrome-control.ps1
    └── repatch-codex-windows.ps1
```

