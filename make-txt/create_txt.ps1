param (
    [string]$Path = $PSScriptRoot
)

# Очищаем путь
$Target = $Path.Trim('"').Trim("'")

# ГЛАВНАЯ ПРАВКА: Если нажали на файл, берем его родительскую папку
if (Test-Path -Path $Target -PathType Leaf) {
    $TargetDir = Split-Path -Path $Target -Parent
} else {
    $TargetDir = $Target
}

Write-Host "Работаем в папке: $TargetDir" -ForegroundColor Cyan

$formats = @(".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm")
$allFiles = Get-ChildItem -Path $TargetDir -File
$count = 0

foreach ($file in $allFiles) {
    if ($formats -contains $file.Extension.ToLower()) {
        $newFilePath = Join-Path -Path $file.DirectoryName -ChildPath ($file.BaseName + ".txt")
        
        if (-not (Test-Path -Path $newFilePath)) {
            New-Item -Path $newFilePath -ItemType File -Force | Out-Null
            Write-Host "Создан: $($file.BaseName).txt"
            $count++
        }
    }
}

Write-Host "`nГотово! Создано файлов: $count" -ForegroundColor Green
Start-Sleep -Seconds 3