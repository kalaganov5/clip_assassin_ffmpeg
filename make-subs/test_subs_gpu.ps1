param(
    [string]$WhisperExe = "C:\Users\kalag\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\whisper.exe",
    [string]$Model = "turbo",
    [string]$Language = "ru",
    [int]$DurationSec = 8
)

$ErrorActionPreference = "Stop"

function Write-Step($msg) {
    Write-Host "`n=== $msg ===" -ForegroundColor Cyan
}

function Fail($msg) {
    Write-Host "[FAIL] $msg" -ForegroundColor Red
    exit 1
}

Write-Step "GPU Subtitles Smoke Test"

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Fail "ffmpeg not found in PATH."
}
if (-not (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) {
    Write-Host "[WARN] nvidia-smi not found. GPU process sampling will be skipped." -ForegroundColor Yellow
}

if (-not (Test-Path $WhisperExe)) {
    Fail "whisper.exe not found: $WhisperExe"
}

Write-Host "[INFO] whisper.exe: $WhisperExe"
Write-Host "[INFO] model: $Model | language: $Language | duration: ${DurationSec}s"

Write-Step "Validate Python CUDA + Whisper model device"
$pyProbe = @"
import json
import torch
import whisper

out = {
    "torch_cuda_available": bool(torch.cuda.is_available()),
    "torch_cuda_device_count": int(torch.cuda.device_count()),
}

if out["torch_cuda_available"] and out["torch_cuda_device_count"] > 0:
    out["torch_cuda_name"] = torch.cuda.get_device_name(0)

model = whisper.load_model("${Model}", device="cuda")
out["whisper_model_device"] = str(next(model.parameters()).device)

print(json.dumps(out, ensure_ascii=False))
"@

$probeJson = $pyProbe | py -
if (-not $probeJson) {
    Fail "Python CUDA/Whisper probe returned empty output."
}

$probe = $probeJson | ConvertFrom-Json
Write-Host "[INFO] torch.cuda.is_available: $($probe.torch_cuda_available)"
Write-Host "[INFO] torch.cuda.device_count: $($probe.torch_cuda_device_count)"
if ($probe.PSObject.Properties.Name -contains "torch_cuda_name") {
    Write-Host "[INFO] torch.cuda device: $($probe.torch_cuda_name)"
}
Write-Host "[INFO] whisper model device: $($probe.whisper_model_device)"

if (-not $probe.torch_cuda_available) {
    Fail "torch reports CUDA unavailable."
}
if (-not ("$($probe.whisper_model_device)".ToLower().StartsWith("cuda"))) {
    Fail "Whisper model did not load on CUDA device."
}

$tmp = Join-Path $env:TEMP ("clip_assassin_subs_gpu_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tmp | Out-Null
$wav = Join-Path $tmp "gpu_probe.wav"
$srt = Join-Path $tmp "gpu_probe.srt"
$stdoutLog = Join-Path $tmp "whisper_gpu.stdout.log"
$stderrLog = Join-Path $tmp "whisper_gpu.stderr.log"

Write-Step "Create synthetic audio"
ffmpeg -hide_banner -loglevel error -y -f lavfi -i "sine=frequency=440:sample_rate=16000" -t $DurationSec -ac 1 -ar 16000 $wav
if (-not (Test-Path $wav)) {
    Fail "Failed to generate test audio."
}

Write-Step "Run Whisper CLI with CUDA"
$args = @(
    "`"$wav`"",
    "--model", $Model,
    "--device", "cuda",
    "--language", $Language,
    "--output_format", "srt",
    "--output_dir", "`"$tmp`""
)

$proc = Start-Process -FilePath $WhisperExe -ArgumentList $args -PassThru -NoNewWindow -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog
Write-Host "[INFO] Whisper PID: $($proc.Id)"

if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    # Best-effort sample for human diagnostics (not hard pass/fail signal).
    Write-Host "[INFO] nvidia-smi snapshot during run:"
    nvidia-smi | Select-Object -First 12
}
$proc.WaitForExit()
$proc.Refresh()
$exitCode = $proc.ExitCode

Write-Host "[INFO] Whisper exit code: $exitCode"

Write-Step "Validate outputs"
if (-not (Test-Path $srt)) {
    Write-Host "[INFO] Whisper logs: $stdoutLog ; $stderrLog"
    if (Test-Path $stdoutLog) { Get-Content -Path $stdoutLog | Select-Object -Last 40 }
    if (Test-Path $stderrLog) { Get-Content -Path $stderrLog | Select-Object -Last 40 }
    Fail "SRT file was not created."
}

if (($null -ne $exitCode) -and ($exitCode -ne 0)) {
    Write-Host "[INFO] Whisper logs: $stdoutLog ; $stderrLog"
    if (Test-Path $stdoutLog) { Get-Content -Path $stdoutLog | Select-Object -Last 40 }
    if (Test-Path $stderrLog) { Get-Content -Path $stderrLog | Select-Object -Last 40 }
    Fail "Whisper exited with non-zero code."
}

Write-Host "[PASS] CUDA subtitles test passed." -ForegroundColor Green
Write-Host "[PASS] SRT created: $srt" -ForegroundColor Green
Write-Host "[PASS] Whisper model loaded on CUDA device." -ForegroundColor Green
Write-Host "[INFO] Temp folder: $tmp"
