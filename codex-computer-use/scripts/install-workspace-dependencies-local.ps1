[CmdletBinding()]
param(
  [switch]$VerifyOnly,
  [switch]$StrictVerifyOnly,
  [string]$Release = 'latest',
  [string]$InstallRoot = (Join-Path $env:USERPROFILE '.cache\codex-runtimes'),
  [string]$BaseUrl = 'https://persistent.oaistatic.com'
)

$ErrorActionPreference = 'Stop'
$LogPrefix = '[codex-workspace-deps]'
$RuntimeName = 'codex-primary-runtime'
$ManifestName = 'LATEST.json'

function Write-Log {
  param([string]$Message)
  Write-Host "$LogPrefix $Message"
}

function Get-Target {
  Join-Path $InstallRoot $RuntimeName
}

function Get-TargetTriple {
  $arch = if ([System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture -eq [System.Runtime.InteropServices.Architecture]::Arm64) { 'arm64' } else { 'x64' }
  "win32-$arch"
}

function Get-ManifestUrl {
  param([string]$TargetTriple)
  "$($BaseUrl.TrimEnd('/'))/$RuntimeName/$Release/$TargetTriple/$ManifestName"
}

function Get-Manifest {
  $url = Get-ManifestUrl (Get-TargetTriple)
  Write-Log "fetching manifest: $url"
  Invoke-RestMethod -Uri $url -Headers @{ 'User-Agent' = 'codex-primary-runtime-installer' } -TimeoutSec 60
}

function Test-WorkspaceDependencies {
  param([switch]$RequireLatest)

  $target = Get-Target
  $runtimeJson = Join-Path $target 'runtime.json'
  if (-not (Test-Path -LiteralPath $runtimeJson -PathType Leaf)) {
    throw "Codex dependency bundle metadata is missing: $runtimeJson"
  }

  $meta = Get-Content -LiteralPath $runtimeJson -Raw | ConvertFrom-Json
  if ([string]::IsNullOrWhiteSpace($meta.bundleVersion)) {
    throw "Codex dependency bundle version is missing in runtime.json"
  }

  $node = Join-Path $target 'dependencies\node\bin\node.exe'
  $nodeModules = Join-Path $target 'dependencies\node\node_modules'
  $python = Join-Path $target 'dependencies\python\python.exe'
  foreach ($path in @($node, $nodeModules, $python)) {
    if (-not (Test-Path -LiteralPath $path)) {
      throw "missing required workspace dependency path: $path"
    }
  }

  if ($RequireLatest) {
    $manifest = Get-Manifest
    if ($manifest.bundleVersion -and $manifest.bundleVersion -ne $meta.bundleVersion) {
      throw "workspace dependency bundle is outdated: installed=$($meta.bundleVersion), latest=$($manifest.bundleVersion)"
    }
  }

  Write-Log "verification ok: bundleVersion=$($meta.bundleVersion)"
}

function Invoke-PythonInstaller {
  param([object]$Manifest)

  $manifestJson = $Manifest | ConvertTo-Json -Depth 20 -Compress
  $target = Get-Target
  $script = @'
import hashlib, json, os, pathlib, shutil, sys, tarfile, tempfile, urllib.request, uuid

manifest = json.loads(sys.argv[1])
install_root = pathlib.Path(sys.argv[2])
runtime_name = sys.argv[3]
target = pathlib.Path(sys.argv[4])
headers = {"User-Agent": "codex-primary-runtime-installer"}
install_root.mkdir(parents=True, exist_ok=True)
tmp_root = pathlib.Path(tempfile.mkdtemp(prefix="codex-runtime-install-", dir=str(install_root)))
archive = tmp_root / manifest["archiveName"]
payload = tmp_root / "payload"
payload.mkdir(parents=True, exist_ok=True)
try:
    req = urllib.request.Request(manifest["archiveUrl"], headers=headers)
    h = hashlib.sha256()
    with urllib.request.urlopen(req, timeout=600) as resp, archive.open("wb") as f:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
            h.update(chunk)
    digest = h.hexdigest()
    expected = manifest["archiveSha256"].lower()
    if digest != expected:
        raise RuntimeError(f"Checksum mismatch: expected {expected}, got {digest}")

    mode = "r:xz" if manifest.get("format", "").lower() == "tar.xz" or archive.name.endswith(".tar.xz") else "r:*"
    with tarfile.open(archive, mode=mode) as tf:
        payload_resolved = payload.resolve()
        members = tf.getmembers()
        for member in members:
            dest = (payload / member.name).resolve()
            if dest != payload_resolved and payload_resolved not in dest.parents:
                raise RuntimeError(f"Archive entry extracts outside payload: {member.name}")
        tf.extractall(payload)

    extracted = payload / runtime_name
    if not extracted.is_dir():
        raise RuntimeError(f"Missing extracted runtime root: {extracted}")
    runtime_json = extracted / "runtime.json"
    meta = json.loads(runtime_json.read_text(encoding="utf-8"))
    if meta.get("bundleVersion") != manifest.get("bundleVersion"):
        raise RuntimeError(f"runtime.json bundleVersion mismatch: {meta.get('bundleVersion')}")

    required = [
        extracted / "dependencies" / "node" / "bin" / "node.exe",
        extracted / "dependencies" / "node" / "node_modules",
        extracted / "dependencies" / "python" / "python.exe",
    ]
    for path in required:
        if not path.exists():
            raise RuntimeError(f"Missing required runtime path: {path}")

    previous = install_root / f"{runtime_name}.previous-{uuid.uuid4().hex}"
    if target.exists():
        target.rename(previous)
    extracted.rename(target)
    if previous.exists():
        shutil.rmtree(previous, ignore_errors=True)
finally:
    shutil.rmtree(tmp_root, ignore_errors=True)
'@

  $temp = Join-Path $env:TEMP ('codex-workspace-deps-install-' + [guid]::NewGuid().ToString('N') + '.py')
  try {
    [System.IO.File]::WriteAllText($temp, $script, [System.Text.UTF8Encoding]::new($false))
    $python = Get-Command python -ErrorAction Stop | Select-Object -First 1
    & $python.Source $temp $manifestJson $InstallRoot $RuntimeName $target
    if ($LASTEXITCODE -ne 0) {
      throw "python workspace dependency installer failed with exit code $LASTEXITCODE"
    }
  } finally {
    Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue
  }
}

function Install-WorkspaceDependencies {
  $manifest = Get-Manifest
  $target = Get-Target
  $runtimeJson = Join-Path $target 'runtime.json'
  if (Test-Path -LiteralPath $runtimeJson -PathType Leaf) {
    $meta = Get-Content -LiteralPath $runtimeJson -Raw | ConvertFrom-Json
    if ($manifest.bundleVersion -and $meta.bundleVersion -eq $manifest.bundleVersion) {
      Write-Log "already current: bundleVersion=$($meta.bundleVersion)"
      return
    }
  }

  Write-Log "installing workspace dependency bundle: $($manifest.bundleVersion)"
  Invoke-PythonInstaller $manifest
  Write-Log "installed workspace dependency bundle: $($manifest.bundleVersion)"
}

if ($StrictVerifyOnly) {
  Test-WorkspaceDependencies -RequireLatest
  exit 0
}

if ($VerifyOnly) {
  try {
    Test-WorkspaceDependencies
    exit 0
  } catch {
    Write-Log "verification failed: $($_.Exception.Message)"
    Write-Log 'repairing workspace dependencies and retrying verification'
    Install-WorkspaceDependencies
    Test-WorkspaceDependencies
    exit 0
  }
}

Install-WorkspaceDependencies
Test-WorkspaceDependencies
