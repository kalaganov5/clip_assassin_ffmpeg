param (
    [string]$Path = $PSScriptRoot
)

$Target = $Path.Trim('"').Trim("'")

if (Test-Path -Path $Target -PathType Leaf) {
    $TargetDir = Split-Path -Path $Target -Parent
} else {
    $TargetDir = $Target
}

Write-Host "=== Фабрика контента: Генерация субтитров (TURBO) ===" -ForegroundColor Cyan
Write-Host "Папка: $TargetDir" -ForegroundColor Cyan

# Тот самый точный путь к Whisper
$whisperExe = "C:\Users\kalag\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\whisper.exe"

if (-not (Test-Path $whisperExe)) {
    Write-Host "`n[КРИТИЧЕСКАЯ ОШИБКА] Файл whisper.exe не найден!" -ForegroundColor Red
    Write-Host "Путь: $whisperExe" -ForegroundColor Red
    Start-Sleep -Seconds 15
    exit
}

$formats = @(".mp4", ".mkv", ".avi", ".mov", ".webm")
$allFiles = Get-ChildItem -Path $TargetDir -File

foreach ($file in $allFiles) {
    if ($formats -contains $file.Extension.ToLower()) {
        $srtFile = Join-Path -Path $file.DirectoryName -ChildPath ($file.BaseName + ".srt")
        
        # Если SRT файла нет — запускаем Whisper
        if (-not (Test-Path -Path $srtFile)) {
            Write-Host "`n[РАБОТА] Распознавание видео: $($file.Name)..." -ForegroundColor Yellow
            
            # Генерируем ТОЛЬКО .srt через скоростную модель TURBO и видеокарту (CUDA)
            & $whisperExe "`"$($file.FullName)`"" --model turbo --device cuda --language ru --output_format srt --output_dir "`"$($file.DirectoryName)`""
            
            if (Test-Path -Path $srtFile) {
                Write-Host "[УСПЕХ] Субтитры готовы для: $($file.BaseName)" -ForegroundColor Green
            } else {
                Write-Host "[ОШИБКА] Сбой нейросети. Файл не создан для: $($file.BaseName)" -ForegroundColor Red
            }
        } else {
            # Если SRT файл уже есть — пропускаем видео
            Write-Host "[ПРОПУСК] Субтитры уже существуют: $($file.Name)" -ForegroundColor DarkGray
        }
    }
}

Write-Host "`nВсе задачи завершены!" -ForegroundColor Cyan
Start-Sleep -Seconds 15