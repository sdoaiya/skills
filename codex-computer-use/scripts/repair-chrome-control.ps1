[CmdletBinding()]
param(
  [string]$CodexHome = (Join-Path $env:USERPROFILE '.codex'),
  [switch]$OpenExtensionPage,
  [switch]$StrictVerifyOnly
)

$ErrorActionPreference = 'Stop'
$LogPrefix = '[codex-chrome-control-repair]'

function Write-Log {
  param([string]$Message)
  Write-Host "$LogPrefix $Message"
}

function Resolve-ExistingFile {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
    throw "missing required file: $Path"
  }
  return (Resolve-Path -LiteralPath $Path).Path
}

function Resolve-ExistingDirectory {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
    throw "missing required directory: $Path"
  }
  return (Resolve-Path -LiteralPath $Path).Path
}

function Write-Utf8NoBom {
  param(
    [string]$Path,
    [string]$Content
  )
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Path) | Out-Null
  $encoding = [System.Text.UTF8Encoding]::new($false)
  [System.IO.File]::WriteAllText($Path, $Content, $encoding)
}

function Copy-FileContentByStream {
  param(
    [string]$Source,
    [string]$Destination
  )

  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
  $inputStream = [System.IO.File]::Open(
    $Source,
    [System.IO.FileMode]::Open,
    [System.IO.FileAccess]::Read,
    [System.IO.FileShare]::ReadWrite
  )
  try {
    $outputStream = [System.IO.File]::Open(
      $Destination,
      [System.IO.FileMode]::Create,
      [System.IO.FileAccess]::Write,
      [System.IO.FileShare]::None
    )
    try {
      $inputStream.CopyTo($outputStream)
    } finally {
      $outputStream.Dispose()
    }
  } finally {
    $inputStream.Dispose()
  }

  $sourceItem = Get-Item -LiteralPath $Source -Force
  $destinationItem = Get-Item -LiteralPath $Destination -Force
  $destinationItem.LastWriteTimeUtc = $sourceItem.LastWriteTimeUtc
}

function Copy-IfMissingOrDifferentLength {
  param(
    [string]$Source,
    [string]$Destination
  )

  $sourceItem = Get-Item -LiteralPath $Source -Force
  if (Test-Path -LiteralPath $Destination -PathType Leaf) {
    $destinationItem = Get-Item -LiteralPath $Destination -Force
    if ($destinationItem.Length -eq $sourceItem.Length) {
      return
    }
  }

  Write-Log "copying protected runtime file: $Source -> $Destination"
  Copy-FileContentByStream $Source $Destination
}

function Test-Executable {
  param(
    [string]$Path,
    [string[]]$Arguments,
    [string]$Name
  )

  $output = & $Path @Arguments 2>&1
  if ($LASTEXITCODE -ne 0) {
    throw "$Name failed to run: $($output -join ' ')"
  }
  if ($output) {
    $firstLine = @($output)[0]
    Write-Log "$Name ok: $firstLine"
  } else {
    Write-Log "$Name ok"
  }
}

function Get-CodexPackage {
  $pkg = Get-AppxPackage -Name OpenAI.Codex -ErrorAction SilentlyContinue |
    Sort-Object Version -Descending |
    Select-Object -First 1
  if (-not $pkg) {
    throw 'OpenAI.Codex package is not installed'
  }
  return $pkg
}

function Install-DesktopRuntimeCopy {
  param(
    [object]$Package,
    [string]$CodexHomeRoot
  )

  $resourcesRoot = Join-Path $Package.InstallLocation 'app\resources'
  $runtimeRoot = Join-Path $CodexHomeRoot ('.tmp\codex-desktop-runtime\' + [string]$Package.Version)
  New-Item -ItemType Directory -Force -Path $runtimeRoot | Out-Null

  foreach ($name in @('codex.exe', 'node.exe', 'node_repl.exe')) {
    $source = Resolve-ExistingFile (Join-Path $resourcesRoot $name)
    $destination = Join-Path $runtimeRoot $name
    Copy-IfMissingOrDifferentLength $source $destination
  }

  $codex = Resolve-ExistingFile (Join-Path $runtimeRoot 'codex.exe')
  $node = Resolve-ExistingFile (Join-Path $runtimeRoot 'node.exe')
  $nodeRepl = Resolve-ExistingFile (Join-Path $runtimeRoot 'node_repl.exe')

  Test-Executable $node @('--version') 'node.exe'
  Test-Executable $codex @('--version') 'codex.exe'
  Test-Executable $nodeRepl @('--help') 'node_repl.exe'

  return [pscustomobject]@{
    Root = $runtimeRoot
    CodexCliPath = $codex
    NodePath = $node
    NodeReplPath = $nodeRepl
  }
}

function Get-ChromeCacheRoot {
  param([string]$CodexHomeRoot)
  $root = Join-Path $CodexHomeRoot 'plugins\cache\openai-bundled\chrome\latest'
  Resolve-ExistingDirectory $root | Out-Null
  Resolve-ExistingFile (Join-Path $root '.codex-plugin\plugin.json') | Out-Null
  Resolve-ExistingFile (Join-Path $root 'extension-host\windows\x64\extension-host.exe') | Out-Null
  Resolve-ExistingFile (Join-Path $root 'scripts\installManifest.mjs') | Out-Null
  Resolve-ExistingFile (Join-Path $root 'scripts\check-native-host-manifest.js') | Out-Null
  Resolve-ExistingFile (Join-Path $root 'scripts\check-extension-installed.js') | Out-Null
  Resolve-ExistingFile (Join-Path $root 'scripts\extension-id.json') | Out-Null
  return $root
}

function Get-StableChromeCacheRoot {
  param([string]$ChromeRoot)

  $item = Get-Item -LiteralPath $ChromeRoot -Force
  if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0 -and $item.Target) {
    $target = @($item.Target)[0]
    if (-not [string]::IsNullOrWhiteSpace($target)) {
      return (Resolve-Path -LiteralPath $target).Path
    }
  }

  return (Resolve-Path -LiteralPath $ChromeRoot).Path
}

function Test-ChromeCacheComplete {
  param([string]$CodexHomeRoot)
  $root = Join-Path $CodexHomeRoot 'plugins\cache\openai-bundled\chrome\latest'
  $required = @(
    (Join-Path $root '.codex-plugin\plugin.json'),
    (Join-Path $root 'extension-host\windows\x64\extension-host.exe'),
    (Join-Path $root 'scripts\installManifest.mjs'),
    (Join-Path $root 'scripts\check-native-host-manifest.js'),
    (Join-Path $root 'scripts\check-extension-installed.js'),
    (Join-Path $root 'scripts\extension-id.json')
  )
  foreach ($path in $required) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
      return $false
    }
  }
  return $true
}

function Repair-BundledCacheIfNeeded {
  param([string]$CodexHomeRoot)

  if (Test-ChromeCacheComplete $CodexHomeRoot) {
    return
  }

  if ($StrictVerifyOnly) {
    throw 'Chrome cache is incomplete and StrictVerifyOnly cannot repair it'
  }

  $installer = Join-Path $PSScriptRoot 'install-computer-use-local.ps1'
  Resolve-ExistingFile $installer | Out-Null
  Write-Log 'Chrome bundled cache is incomplete; repairing openai-bundled mirror/cache first'
  & powershell -NoProfile -ExecutionPolicy Bypass -File $installer -VerifyOnly
  if ($LASTEXITCODE -ne 0) {
    throw "install-computer-use-local.ps1 -VerifyOnly failed with exit code $LASTEXITCODE"
  }

  if (-not (Test-ChromeCacheComplete $CodexHomeRoot)) {
    throw 'Chrome cache is still incomplete after bundled cache repair'
  }
}

function Invoke-NodeJsonScript {
  param(
    [string]$NodePath,
    [string]$ScriptPath
  )

  $output = & $NodePath $ScriptPath --json 2>&1
  $exitCode = $LASTEXITCODE
  $text = ($output -join "`n").Trim()
  $json = $null
  if (-not [string]::IsNullOrWhiteSpace($text)) {
    try {
      $json = $text | ConvertFrom-Json
    } catch {
      throw "failed to parse JSON from ${ScriptPath}: $text"
    }
  }

  return [pscustomobject]@{
    ExitCode = $exitCode
    Json = $json
    Raw = $text
  }
}

function Install-ChromeNativeHost {
  param(
    [string]$ChromeRoot,
    [object]$Runtime
  )

  $installManifestPath = (Join-Path $ChromeRoot 'scripts\installManifest.mjs').Replace('\', '/')
  $env:CODEX_CLI_PATH = $Runtime.CodexCliPath
  $env:CODEX_NODE_PATH = $Runtime.NodePath
  $env:CODEX_NODE_REPL_PATH = $Runtime.NodeReplPath

  $code = @"
import { install } from 'file:///$installManifestPath';
await install({ appServerRuntimePaths: {
  codexCliPath: process.env.CODEX_CLI_PATH,
  nodePath: process.env.CODEX_NODE_PATH,
  nodeReplPath: process.env.CODEX_NODE_REPL_PATH
}});
console.log('installManifest ok');
"@

  $output = & $Runtime.NodePath --input-type=module --eval $code 2>&1
  if ($LASTEXITCODE -ne 0) {
    throw "installManifest.mjs failed: $($output -join ' ')"
  }
  Write-Log ($output -join ' ')
}

function Set-ChromeNativeHostStablePath {
  param(
    [string]$ChromeRoot,
    [object]$Runtime
  )

  $stableRoot = Get-StableChromeCacheRoot $ChromeRoot
  $stableHostPath = Resolve-ExistingFile (Join-Path $stableRoot 'extension-host\windows\x64\extension-host.exe')
  $manifestPath = Join-Path $env:LOCALAPPDATA 'OpenAI\extension\com.openai.codexextension.json'
  Resolve-ExistingFile $manifestPath | Out-Null

  $manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
  if ([string]$manifest.path -ne $stableHostPath) {
    $backupPath = "$manifestPath.$(Get-Date -Format 'yyyyMMdd-HHmmss-fff').bak"
    Copy-Item -LiteralPath $manifestPath -Destination $backupPath -Force
    $manifest.path = $stableHostPath
    Write-Utf8NoBom $manifestPath (($manifest | ConvertTo-Json -Depth 20) + "`n")
    Write-Log "native host manifest path pinned to stable cache: $stableHostPath"
    Write-Log "native host manifest backup: $backupPath"
  }

  $configPath = Join-Path (Split-Path -Parent $stableHostPath) 'extension-host-config.json'
  if (Test-Path -LiteralPath $configPath -PathType Leaf) {
    $config = Get-Content -Raw -LiteralPath $configPath | ConvertFrom-Json
    $config.browserClientPath = Resolve-ExistingFile (Join-Path $stableRoot 'scripts\browser-client.mjs')
    $config.codexCliPath = $Runtime.CodexCliPath
    $config.nodePath = $Runtime.NodePath
    $config.nodeReplPath = $Runtime.NodeReplPath
    Write-Utf8NoBom $configPath (($config | ConvertTo-Json -Depth 20) + "`n")
  }
}

function Get-ChromeExecutable {
  $registryKeys = @(
    'HKCU\Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe',
    'HKLM\Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe',
    'HKLM\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe'
  )

  foreach ($key in $registryKeys) {
    $output = & reg query $key /ve 2>$null
    foreach ($line in @($output)) {
      $match = [regex]::Match($line, '^\s*\(Default\)\s+REG_\w+\s+(.+?)\s*$')
      if ($match.Success) {
        $candidate = $match.Groups[1].Value.Trim('"')
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
          return $candidate
        }
      }
    }
  }

  $standard = @(
    (Join-Path $env:LOCALAPPDATA 'Google\Chrome\Application\chrome.exe'),
    (Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe')
  )
  if (${env:ProgramFiles(x86)}) {
    $standard += (Join-Path ${env:ProgramFiles(x86)} 'Google\Chrome\Application\chrome.exe')
  }

  foreach ($candidate in $standard) {
    if (Test-Path -LiteralPath $candidate -PathType Leaf) {
      return $candidate
    }
  }

  $cmd = Get-Command chrome.exe -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($cmd -and (Test-Path -LiteralPath $cmd.Source -PathType Leaf)) {
    return $cmd.Source
  }

  throw 'Google Chrome executable was not found'
}

function Open-ChromeExtensionPage {
  param(
    [string]$ExtensionId,
    [string]$ProfileDirectory
  )

  $chrome = Get-ChromeExecutable
  $url = "https://chromewebstore.google.com/detail/$ExtensionId"
  Write-Log "opening Chrome extension page for profile ${ProfileDirectory}: $url"
  Start-Process -FilePath $chrome -ArgumentList @("--profile-directory=$ProfileDirectory", '--new-window', $url)
}

function Repair-ChromeControl {
  $codexHomeRoot = Resolve-ExistingDirectory $CodexHome
  $pkg = Get-CodexPackage
  Write-Log "Codex package: $($pkg.PackageFullName) ($($pkg.SignatureKind))"

  Repair-BundledCacheIfNeeded $codexHomeRoot
  $chromeRoot = Get-ChromeCacheRoot $codexHomeRoot
  Write-Log "Chrome plugin cache: $chromeRoot"

  $runtime = Install-DesktopRuntimeCopy $pkg $codexHomeRoot

  if (-not $StrictVerifyOnly) {
    Install-ChromeNativeHost $chromeRoot $runtime
    Set-ChromeNativeHostStablePath $chromeRoot $runtime
  }

  $nativeCheck = Invoke-NodeJsonScript $runtime.NodePath (Join-Path $chromeRoot 'scripts\check-native-host-manifest.js')
  if ($nativeCheck.ExitCode -ne 0 -or -not $nativeCheck.Json.correct) {
    throw "Chrome native host manifest is not correct: $($nativeCheck.Raw)"
  }
  Write-Log "native host ok: $($nativeCheck.Json.manifestPath)"

  $extensionCheck = Invoke-NodeJsonScript $runtime.NodePath (Join-Path $chromeRoot 'scripts\check-extension-installed.js')
  $extensionId = [string]$extensionCheck.Json.extensionId
  $selectedProfile = [string]$extensionCheck.Json.selectedProfileDirectory
  if ($extensionCheck.ExitCode -eq 0) {
    Write-Log "Chrome extension connected in selected profile: $selectedProfile"
    return
  }

  $installedProfiles = @($extensionCheck.Json.profiles | Where-Object { $_.installed -and $_.enabled } | ForEach-Object { $_.profileDirectory })
  if ($installedProfiles.Count -gt 0) {
    Write-Log "Chrome extension is installed in profile(s) $($installedProfiles -join ', ') but not in selected profile $selectedProfile"
  } else {
    Write-Log "Chrome extension is not installed in selected profile $selectedProfile"
  }

  if ($OpenExtensionPage) {
    Open-ChromeExtensionPage $extensionId $selectedProfile
  }

  throw "manual Chrome extension install required for selected profile: $selectedProfile"
}

Repair-ChromeControl
