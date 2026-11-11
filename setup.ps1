param(
    [switch]$WithPose,
    [switch]$RegisterMcp,
    [string]$TouchDesignerPython = 'C:\Program Files\Derivative\TouchDesigner\bin\python.exe'
)
$ErrorActionPreference = 'Stop'
$tdRoot = $PSScriptRoot
$tdVenv = Join-Path $tdRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $tdVenv)) {
    python -m venv (Join-Path $tdRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Creating the MCP environment failed' }
}
& $tdVenv -m pip install -r (Join-Path $tdRoot 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Installing MCP requirements failed' }
if ($WithPose) {
    if (-not (Test-Path -LiteralPath $TouchDesignerPython)) {
        throw 'Specify -TouchDesignerPython with the bundled Python 3.11 executable'
    }
    $tdPosePython = Join-Path $tdRoot '.pose-venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $tdPosePython)) {
        & $TouchDesignerPython -m venv (Join-Path $tdRoot '.pose-venv')
        if ($LASTEXITCODE -ne 0) { throw 'Creating the pose environment failed' }
    }
    & $tdPosePython -m pip install -r (Join-Path $tdRoot 'requirements-pose.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Installing pose requirements failed' }
    $tdModels = Join-Path $tdRoot 'models'
    New-Item -ItemType Directory -Path $tdModels -Force | Out-Null
    $tdModel = Join-Path $tdModels 'pose_landmarker_lite.task'
    if (-not (Test-Path -LiteralPath $tdModel)) {
        Invoke-WebRequest 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task' -OutFile $tdModel
    }
    $tdHash = (Get-FileHash -LiteralPath $tdModel -Algorithm SHA256).Hash.ToLowerInvariant()
    $tdExpected = (Get-Content -LiteralPath (Join-Path $tdRoot 'models.sha256')).Split(' ')[0]
    if ($tdHash -ne $tdExpected) { throw 'Pose model checksum mismatch; remove the model and download again' }
}
if ($RegisterMcp) {
    if (-not (Get-Command codex -ErrorAction SilentlyContinue)) { throw 'Codex CLI is not on PATH' }
    codex mcp add touchdesigner -- $tdVenv (Join-Path $tdRoot 'server.py')
    if ($LASTEXITCODE -ne 0) { throw 'MCP registration failed' }
}
Write-Host 'Setup complete. Follow README.md to activate the bridge in Python Textport.'
