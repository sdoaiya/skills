param(
  [switch]$DryRun,
  [switch]$ApplyToExtractedAsar,
  [string]$AsarPath,
  [string]$WorkDir = (Join-Path $env:TEMP "codex-window-asar-patch"),
  [string]$PatchedAsarPath
)

$ErrorActionPreference = "Stop"

function Write-Step([string]$Message) {
  Write-Host "[codex-window] $Message"
}

function Resolve-CodexAsar {
  param([string]$ExplicitPath)
  if ($ExplicitPath) {
    $resolved = Resolve-Path -LiteralPath $ExplicitPath -ErrorAction Stop
    return $resolved.Path
  }

  $pkg = Get-AppxPackage -Name OpenAI.Codex | Select-Object -First 1
  if (-not $pkg) {
    throw "OpenAI.Codex package not found. Pass -AsarPath explicitly."
  }

  $candidates = @(
    (Join-Path $pkg.InstallLocation "resources\app.asar"),
    (Join-Path $pkg.InstallLocation "app\resources\app.asar")
  )

  foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate) {
      Write-Step "package: $($pkg.PackageFullName)"
      Write-Step "signature: $($pkg.SignatureKind)"
      return $candidate
    }
  }

  throw "Could not find app.asar under $($pkg.InstallLocation)."
}

function Invoke-Asar {
  param([string[]]$Arguments)
  $cmd = Get-Command npx -ErrorAction Stop
  & $cmd.Source --yes "@electron/asar" @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "asar command failed: npx --yes @electron/asar $($Arguments -join ' ')"
  }
}

function Replace-Count {
  param(
    [string]$Text,
    [string]$Pattern,
    [string]$Replacement,
    [ref]$Count
  )
  $matches = [regex]::Matches($Text, $Pattern)
  $Count.Value = $matches.Count
  if ($matches.Count -eq 0) {
    return $Text
  }
  return [regex]::Replace($Text, $Pattern, $Replacement)
}

function Set-Utf8NoBom {
  param(
    [string]$Path,
    [string]$Text
  )
  $encoding = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $Text, $encoding)
}

if (-not $DryRun -and -not $ApplyToExtractedAsar) {
  $DryRun = $true
}

$asar = Resolve-CodexAsar -ExplicitPath $AsarPath
Write-Step "asar: $asar"

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  throw "node is required."
}
if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
  throw "npx is required."
}

$extractDir = Join-Path $WorkDir "extracted"
$outDir = Join-Path $WorkDir "out"
Remove-Item -LiteralPath $extractDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $extractDir, $outDir | Out-Null

Write-Step "extracting asar to $extractDir"
Invoke-Asar -Arguments @("extract", $asar, $extractDir)

$mainFiles = Get-ChildItem -LiteralPath (Join-Path $extractDir ".vite\build") -Filter "main-*.js" -File -ErrorAction Stop
$mainFile = $mainFiles | Sort-Object Length -Descending | Select-Object -First 1
if (-not $mainFile) {
  throw "Could not find .vite\build\main-*.js in extracted asar."
}

$cssFile = Get-ChildItem -LiteralPath (Join-Path $extractDir "webview\assets") -Filter "app-shell-*.css" -File -ErrorAction SilentlyContinue | Sort-Object Length -Descending | Select-Object -First 1
$indexFile = Join-Path $extractDir "webview\index.html"

Write-Step "main js: $($mainFile.FullName)"
if ($cssFile) { Write-Step "app shell css: $($cssFile.FullName)" }
if (Test-Path -LiteralPath $indexFile) { Write-Step "index html: $indexFile" }

$results = [ordered]@{}

$main = Get-Content -LiteralPath $mainFile.FullName -Raw
$transparentMatch = [regex]::Match($main, '([A-Za-z_$][A-Za-z0-9_$]*)=`#00000000`')
$transparentVar = if ($transparentMatch.Success) { $transparentMatch.Groups[1].Value } else { $null }
$results["transparent background const"] = if ($transparentVar) { "matched var $transparentVar" } else { "not matched" }

if ($transparentVar) {
  $count = 0
  $main = Replace-Count $main ('(' + [regex]::Escape($transparentVar) + ')=`#00000000`') '$1=`#1f1f1f`' ([ref]$count)
  $results["set opaque background const"] = $count

  $count = 0
  $main = Replace-Count $main ('color:' + [regex]::Escape($transparentVar) + ',symbolColor:') 'color:a.nativeTheme.shouldUseDarkColors?`#1f1f1f`:`#f9f9f9`,symbolColor:' ([ref]$count)
  $results["titlebar overlay color"] = if ($count -gt 0) { $count } else { "not matched or already changed" }

  $count = 0
  $micaPattern = 'e===`win32`&&!A2\(t\)\?\{backgroundColor:' + [regex]::Escape($transparentVar) + ',backgroundMaterial:`mica`\}'
  $main = Replace-Count $main $micaPattern 'e===`win32`&&!A2(t)?{backgroundColor:r?a2:o2,backgroundMaterial:`none`}' ([ref]$count)
  $results["windows mica fallback"] = if ($count -gt 0) { $count } else { "not matched or already changed" }
}

$count = 0
$main = Replace-Count $main 'process\.platform===`darwin`&&\(M\.on\(`move`,ne\),M\.on\(`resize`,ne\)\)' 'M.on(`move`,ne),M.on(`resize`,ne)' ([ref]$count)
$results["resize listener darwin gate"] = if ($count -gt 0) { $count } else { "not matched or already fixed" }

if ($ApplyToExtractedAsar) {
  Set-Utf8NoBom -Path $mainFile.FullName -Text $main
}

if ($cssFile) {
  $css = Get-Content -LiteralPath $cssFile.FullName -Raw
  $countA = 0
  $css = Replace-Count $css "\.app-header-tint\{background-color:var\(--codex-titlebar-tint,transparent\)\}" '.app-header-tint{background-color:var(--codex-titlebar-tint,var(--color-background-surface-under))}' ([ref]$countA)
  $countB = 0
  $css = Replace-Count $css "\.app-header-tint\[data-app-shell-header-edge-scroll=true\]\{background-color:#0000\}" '.app-header-tint[data-app-shell-header-edge-scroll=true]{background-color:var(--color-background-surface-under)}' ([ref]$countB)
  $results["app-shell transparent tint"] = if (($countA + $countB) -gt 0) { ($countA + $countB) } else { "not matched or already fixed" }
  if ($ApplyToExtractedAsar) {
    Set-Utf8NoBom -Path $cssFile.FullName -Text $css
  }
}

if (Test-Path -LiteralPath $indexFile) {
  $html = Get-Content -LiteralPath $indexFile -Raw
  $count = 0
  $html = Replace-Count $html "--startup-background:\s*(?:transparent|#00000000|#0000);" '--startup-background: #1f1f1f;' ([ref]$count)
  $results["startup transparent background"] = if ($count -gt 0) { $count } else { "not matched or already fixed" }
  if ($ApplyToExtractedAsar) {
    Set-Utf8NoBom -Path $indexFile -Text $html
  }
}

Write-Step "patch report:"
foreach ($key in $results.Keys) {
  Write-Host "  - ${key}: $($results[$key])"
}

if ($DryRun -and -not $ApplyToExtractedAsar) {
  Write-Step "dry run complete; no files were modified."
  exit 0
}

if (-not $PatchedAsarPath) {
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  $PatchedAsarPath = Join-Path $outDir "app.windowfix.$stamp.asar"
}

Write-Step "packing patched asar to $PatchedAsarPath"
Remove-Item -LiteralPath $PatchedAsarPath -Force -ErrorAction SilentlyContinue
Invoke-Asar -Arguments @("pack", $extractDir, $PatchedAsarPath)
Get-Item -LiteralPath $PatchedAsarPath | Select-Object FullName,Length,LastWriteTime
Write-Step "patched asar generated; this script did not replace the installed Codex package."
