param([switch]$RegisterMcp)
$ErrorActionPreference = 'Stop'
$tdRoot = $PSScriptRoot
$tdVenv = Join-Path $tdRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $tdVenv)) {
    python -m venv (Join-Path $tdRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Creating the MCP environment failed' }
}
& $tdVenv -m pip install -r (Join-Path $tdRoot 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Installing MCP requirements failed' }
if ($RegisterMcp) {
    if (-not (Get-Command codex -ErrorAction SilentlyContinue)) { throw 'Codex CLI is not on PATH' }
    codex mcp add touchdesigner -- $tdVenv (Join-Path $tdRoot 'server.py')
    if ($LASTEXITCODE -ne 0) { throw 'MCP registration failed' }
}
Write-Host 'Setup complete. Follow README.md to activate the bridge in Python Textport.'
