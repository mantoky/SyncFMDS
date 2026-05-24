$ErrorActionPreference = "Stop"

$python = "C:\Users\robso\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$queryFile = Join-Path $projectRoot "data\vps\vps_external_query.sql"
$outDir = Join-Path $projectRoot "data\vps"

if (-not $env:VPS_SQLSERVER_CONN) {
  Write-Host "ERRO: defina a variavel de ambiente VPS_SQLSERVER_CONN com a connection string do SQL Server." -ForegroundColor Red
  exit 1
}

& $python .\vps_connector.py `
  --out-dir $outDir `
  --sqlserver-query-file $queryFile

if ($LASTEXITCODE -ne 0) {
  Write-Host "Falha no sync VPS." -ForegroundColor Red
  exit $LASTEXITCODE
}

Write-Host "Sync VPS concluido com sucesso." -ForegroundColor Green
