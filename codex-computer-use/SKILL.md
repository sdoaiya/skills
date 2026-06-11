---
name: codex-computer-use
description: Diagnose and repair Codex Desktop Computer Use, Any App, bundled plugin mirror/cache, in-app browser, and Google Chrome external browser control failures on Windows. Use when Computer Use is missing, Any App is unavailable, Chrome says extension not connected, browser/native-host install fails, WindowsApps copy hangs, or Codex Desktop Store updates break local plugin paths.
---

# Codex Windows Control Repair

Use this skill on Windows when Codex Desktop cannot use Computer Use, Any App, the in-app browser, or Google Chrome. Prefer local diagnosis and repair first. Treat MSIX/ASAR repatching as a last resort because it can stop, uninstall, reinstall, and relaunch Codex Desktop.

## Operating Rules

- Do not modify `C:\Program Files\WindowsApps` in place.
- Do not run full MSIX/ASAR repatch during an active Codex Desktop session unless the user explicitly accepts that Codex may be stopped and reinstalled.
- Do not assume `robocopy` works for Store package files. WindowsApps resources can be `Encrypted` / `Application Protected`; use scripts in this skill because they stream-copy bytes instead of preserving protected file attributes.
- Before changing `$env:USERPROFILE\.codex\config.toml`, create a timestamped backup. Bundled scripts do this automatically.
- If a script or dry run is interrupted, check for leftover `powershell`, `robocopy`, `asar`, `makeappx`, or `signtool` processes whose command lines match this repair before continuing. Stop only confirmed repair processes.
- Keep evidence explicit: package status, config values, plugin/cache paths, native-host manifest, registry key, selected Chrome profile, helper screenshot verification, and Codex Desktop UI status.

## Quick Triage

Run these first:

```powershell
Get-AppxPackage -Name OpenAI.Codex | Select-Object Name,PackageFullName,Version,SignatureKind,InstallLocation
[Environment]::GetEnvironmentVariable('CODEX_ELECTRON_ENABLE_WINDOWS_COMPUTER_USE','User')
Select-String -LiteralPath "$env:USERPROFILE\.codex\config.toml" -Pattern 'computer_use|openai-bundled|computer-use|\[windows\]|sandbox' -Context 0,2
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\codex-computer-use\scripts\install-workspace-dependencies-local.ps1" -VerifyOnly
```

Interpretation:

- `SignatureKind = Store` is fine. Local Computer Use repair does not require Developer-signed MSIX.
- Missing `[marketplaces.openai-bundled]`, missing `[plugins."computer-use@openai-bundled"]`, missing `CODEX_ELECTRON_ENABLE_WINDOWS_COMPUTER_USE=1`, or missing `features.computer_use = true` means run the Computer Use local repair.
- If the UI already shows `Any App` enabled but `Google Chrome` says install failed or extension not connected, skip MSIX work and repair Chrome control.

## Computer Use Local Repair

Back up state first:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\codex-computer-use\scripts\manage-codex-backups.ps1" -Action Backup
```

Verify without changing files:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\codex-computer-use\scripts\install-computer-use-local.ps1" -StrictVerifyOnly
```

If strict verify fails, repair and verify:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\codex-computer-use\scripts\install-computer-use-local.ps1" -VerifyOnly
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\codex-computer-use\scripts\install-computer-use-local.ps1" -StrictVerifyOnly
```

What the repair script handles:

- Syncs the installed `openai-bundled` marketplace to `%USERPROFILE%\.codex\.tmp\bundled-marketplaces\openai-bundled`.
- Uses byte-stream copying so `ERROR 6000 The specified file could not be encrypted` and WindowsApps `Application Protected` files do not break the copy.
- Skips invalid reparse points or unreadable package dependency remnants instead of hanging.
- Rebuilds stable cache copies for `browser`, `chrome`, and `computer-use`.
- Writes `[marketplaces.openai-bundled]`, `[plugins."computer-use@openai-bundled"]`, `[features] computer_use = true`, and `[windows] sandbox = "unelevated"`.
- Sets `CODEX_ELECTRON_ENABLE_WINDOWS_COMPUTER_USE=1`.
- Verifies the Computer Use helper can return screen info and a screenshot.

Success means:

- `-StrictVerifyOnly` prints `verification ok`.
- The helper test prints valid width/height and screenshot bytes.
- `install-workspace-dependencies-local.ps1 -VerifyOnly` prints `verification ok` and Settings can show the Workspace Dependencies bundle version.
- These files exist:
  - `%USERPROFILE%\.codex\.tmp\bundled-marketplaces\openai-bundled\.agents\plugins\marketplace.json`
  - `%USERPROFILE%\.codex\.tmp\bundled-marketplaces\openai-bundled\plugins\browser\.codex-plugin\plugin.json`
  - `%USERPROFILE%\.codex\.tmp\bundled-marketplaces\openai-bundled\plugins\chrome\.codex-plugin\plugin.json`
  - `%USERPROFILE%\.codex\.tmp\bundled-marketplaces\openai-bundled\plugins\computer-use\.codex-plugin\plugin.json`
  - `%USERPROFILE%\.codex\plugins\cache\openai-bundled\browser\latest\.codex-plugin\plugin.json`
  - `%USERPROFILE%\.codex\plugins\cache\openai-bundled\chrome\latest\.codex-plugin\plugin.json`
  - `%USERPROFILE%\.codex\plugins\cache\openai-bundled\computer-use\latest\.codex-plugin\plugin.json`

After success, fully quit and reopen Codex Desktop.

## Chrome Control Repair

Use this when the in-app browser works but `Computer Use > Google Chrome` says installation failed, extension not connected, or browser extension not connected.

Repair native messaging, registry, protected runtime files, and selected-profile detection:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\codex-computer-use\scripts\repair-chrome-control.ps1"
```

If the script says manual Chrome extension install is required, open the selected profile's install page:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\codex-computer-use\scripts\repair-chrome-control.ps1" -OpenExtensionPage
```

What the Chrome repair script handles:

- Creates `%LOCALAPPDATA%\OpenAI\extension\com.openai.codexextension.json`.
- Writes `HKCU\Software\Google\Chrome\NativeMessagingHosts\com.openai.codexextension`.
- Copies `codex.exe`, `node.exe`, and `node_repl.exe` from the Store package to `%USERPROFILE%\.codex\.tmp\codex-desktop-runtime\<version>\` using byte-stream copy, because Store package executables may be `Access is denied` when launched directly from WindowsApps.
- Points `extension-host-config.json` at the copied runtime executables.
- Runs the bundled `check-native-host-manifest.js --json` and requires `correct = true`.
- Runs `check-extension-installed.js --json` and detects when the extension is installed in one Chrome profile but Codex selected another.

If profile mismatch is reported:

- Example: extension installed in `Profile 7`, selected profile is `Profile 9`.
- Install the extension in the selected profile shown by the script.
- Do not force Chrome enterprise policy unless the user explicitly wants managed-policy behavior.

Success means:

- `check-native-host-manifest.js --json` reports `correct: true`.
- `check-extension-installed.js --json` exits `0`.
- Codex Desktop shows `Google Chrome` as connected.

## Symptom Matrix

- `Computer Use 插件不可用`: run Computer Use local repair, then strict verify.
- `Any App` visible and toggled on, but Chrome row says extension not connected: run Chrome control repair.
- Browser settings page works, but Chrome install fails: repair native messaging and selected Chrome profile; do not repatch MSIX first.
- `robocopy` hangs or logs `The specified file could not be encrypted`: use the stream-copy scripts here; do not retry raw `robocopy`.
- Store package `resources\codex.exe`, `node.exe`, or `node_repl.exe` says `Access is denied`: copy runtime to `.codex\.tmp\codex-desktop-runtime\<version>` and point Chrome native host config there.
- `windows sandbox failed: spawn setup refresh` or OS error `740`: set `[windows] sandbox = "unelevated"` and rerun Computer Use repair.
- `codex plugin list` fails because a local marketplace has only root `marketplace.json`: copy it to `.agents\plugins\marketplace.json` or restore the marketplace from backup.

## MSIX/ASAR Repatch Last Resort

Only use this when local repair succeeds but the Desktop UI gate remains hidden or disabled, such as:

- `Any App` / `任意应用` is still blocked by organization or region after restart.
- Desktop logs show feature availability still `statsig-disabled`.
- Fast Mode, locale, plugin UI, or browser availability gates must be patched inside the shipped Electron bundle.

Dry-run target matching:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\codex-computer-use\scripts\repatch-codex-windows.ps1" -DryRun -SkipFastVerify
```

Full repatch:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\codex-computer-use\scripts\repatch-codex-windows.ps1"
```

Before full repatch, tell the user it can stop Codex Desktop, remove the Store package, install a locally signed package, and change `SignatureKind` to `Developer`.

## Advanced Cases

If the main workflow does not explain the failure, read `references/restriction-debug-cases.md`. It covers Fast Mode wire validation, UI gate target drift, browser availability logs, sandbox error 740, Codex mobile auth-loop behavior, and ASAR cleanup edge cases.

## Backup Management

Create snapshot:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\codex-computer-use\scripts\manage-codex-backups.ps1" -Action Backup
```

List or restore snapshots:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\codex-computer-use\scripts\manage-codex-backups.ps1" -Action List
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\skills\codex-computer-use\scripts\manage-codex-backups.ps1" -Action Restore -BackupPath "<backup path>"
```
