# Codex Windows Window Patch Notes

## 当前验证结论

在 `OpenAI.Codex_26.602.4764.0_x64__2p2nqsd0c76g0` 上，`app.asar` 位于：

```text
C:\Program Files\WindowsApps\OpenAI.Codex_26.602.4764.0_x64__2p2nqsd0c76g0\app\resources\app.asar
```

该版本的 `.vite\build\main-*.js` 仍包含 Windows `backgroundMaterial:\`mica\`` fallback 和透明背景常量，但 resize 监听已经是全平台，`webview/assets/app-shell-*.css` 的标题栏 tint 也已不是旧的 transparent 回退。

因此，原始方案方向可行，但不能硬编码旧变量名 `Q0` 或旧路径 `resources\app.asar`。脚本必须先探测路径、文件名和补丁点。

## 风险边界

- 直接改 WindowsApps 中的文件通常会遇到权限、签名或应用完整性问题。
- Store 升级会替换安装目录，补丁需要重新 dry run。
- 当前脚本只生成 patched asar；真正安装 patched MSIX 应复用已有的 Windows repatch 流程。
- 如果补丁点不命中，不要猜测 minified 代码含义，先抽取文件并人工检查相关片段。

## 成功检查

修复后至少检查：

- 最大化窗口左侧和顶部不再透明。
- 全屏时内容背景铺满，没有居中白色圆角面板。
- 右上角窗口控制按钮后方没有黑色矩形。
- 深色和浅色主题下标题栏背景都不透明。
- 退出并重新打开 Codex 后问题不复现。
