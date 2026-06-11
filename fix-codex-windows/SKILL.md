---
name: fix-codex-windows
description: 修复或验证 Windows 上 Codex Desktop Electron 窗口最大化、全屏时的透明区域、黑块、圆角残留、mica 背景和标题栏透明问题。Use when Codex window is transparent, has black blocks, keeps rounded corners, or needs ASAR window-surface repatching after an upgrade.
---

# Codex 窗口修复

用于 Windows 10/11 上 Codex Desktop 最大化或全屏后出现透明溢出、黑色块、白色圆角面板、标题栏黑底或圆角残留的问题。

## 操作规则

- 先做只读诊断和 `-DryRun`，不要直接修改 `C:\Program Files\WindowsApps`。
- 每次修复前记录当前 `Get-AppxPackage -Name OpenAI.Codex` 的版本、签名类型和安装路径。
- 先备份原始 `app.asar`，再对解包副本打补丁。
- 如果当前版本已经没有某个旧补丁点，把它标记为 `already fixed` 或 `not matched`，不要强行改相似代码。
- 全量替换 MSIX、卸载/重装 Codex、或改 Developer 签名必须得到用户明确同意。
- 如果同时出现 Computer Use、Any App、Chrome 控制或插件缺失，先用 `$codex-computer-use`；本 skill 只处理 Electron 窗口外观补丁。

## 快速验证

运行只读环境检查：

```powershell
Get-AppxPackage -Name OpenAI.Codex | Select-Object Name,PackageFullName,Version,SignatureKind,InstallLocation
node --version
npx --version
```

运行 dry run：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\fix-codex-windows\scripts\patch-codex-window-asar.ps1" -DryRun
```

判断：

- `asar` 路径应自动解析到 `resources\app.asar` 或 `app\resources\app.asar`。
- `main js` 应能找到 `.vite\build\main-*.js`。
- `mica fallback` 或 `transparent background const` 命中时，说明该版本仍需要窗口补丁。
- `resize listener` 和 `app-shell tint` 显示 already fixed 是正常现象，表示上游版本已包含部分修复。

## 生成补丁 asar

只在临时目录里解包、修改、重新打包：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\fix-codex-windows\scripts\patch-codex-window-asar.ps1" -ApplyToExtractedAsar
```

输出会包含：

- 原始 `app.asar` 路径
- 解包目录
- 新生成的 patched `app.asar`
- 每个补丁点的命中数量

此脚本不会自动替换 WindowsApps 里的文件，也不会卸载或重装 Codex。

## 补丁点

主进程 JS：

- 把透明背景常量从 `#00000000` 改为 `#1f1f1f`。
- 把 Windows fallback 的 `backgroundMaterial:\`mica\`` 改为 `backgroundMaterial:\`none\``，并使用深浅主题不透明背景。
- 如果旧版本仍把 `move/resize` 监听限制在 `darwin`，改成全平台监听。
- 把标题栏 overlay 的透明 `color` 改成深浅主题不透明颜色。

Web shell：

- 如果 `webview/assets/app-shell-*.css` 仍使用透明标题栏 tint，改为 `var(--color-background-surface-under)`。
- 如果 `webview/index.html` 启动背景仍是透明，改为 `#1f1f1f`。

## 替换安装包

当用户明确要求实际替换安装包时：

1. 停止 Codex Desktop。
2. 备份原始 MSIX 或原始 `app.asar`。
3. 用生成的 patched `app.asar` 替换解包副本中的 `app\resources\app.asar`。
4. 使用可信的既有 MSIX repatch 流程重新打包、签名和安装。
5. 重启 Codex 后最大化、全屏、深浅主题各检查一次。

详细判断见 `references/window-patch-notes.md`。
