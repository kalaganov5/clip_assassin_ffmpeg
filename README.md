# Clip Assassin - FFmpeg Batch Edition

[English](#english) | [Русский](#russian)

<a name="english"></a>
## 🇬🇧 English

This toolset automatically processes video files to create Reels and Intros based on text file inputs.

### 📥 Download

You don't need to install Python! Just download the latest version for your OS from the **[Releases](../../releases)** page.

*   **Windows**: Download `.exe` files.
*   **macOS**: Download `.zip` files. Unzip them to get the `.app` application.

### ⚠️ macOS Users (Important!)

When you try to run the app for the first time, macOS might block it because it's from an "Unidentified Developer".

1.  **Right-click** (or Control-click) the app icon.
2.  Select **Open** from the menu.
3.  Click **Open** in the dialog box that appears.
    *   *You only need to do this once.*

### ⚙️ Prerequisites

Before running the program, you **MUST** have **FFmpeg** installed on your system.

#### How to install FFmpeg:

*   **Windows**:
    1.  Download `ffmpeg-release-essentials.zip` from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
    2.  Extract `ffmpeg.exe` from the `bin` folder.
    3.  Place `ffmpeg.exe` **in the same folder** as `ClipAssassin_Reels.exe` (or add it to your system PATH).
*   **macOS**:
    *   Install via Homebrew: `brew install ffmpeg`

### 🎛️ Encoder Policy (GPU/CPU)

The app supports configurable encoder behavior via environment variables:

```env
CA_ENCODER_POLICY=auto
CA_ENCODER_PRIORITY=h264_nvenc,h264_qsv,h264_amf,libx264
CA_ENCODER_LOG=basic
```

Variables:
*   `CA_ENCODER_POLICY=auto|strict_gpu|cpu_only` (default: `auto`)
    *   `auto`: tries GPU encoders first, falls back to CPU (`libx264`) if needed.
    *   `strict_gpu`: hardware encoder only; fails if GPU encoder is not usable.
    *   `cpu_only`: always uses `libx264`.
*   `CA_ENCODER_PRIORITY`: optional comma-separated override of encoder order.
*   `CA_ENCODER_LOG=basic|debug`: debug mode prints detailed skip/fallback reasons.

Platform defaults:
*   **Windows**: `h264_nvenc,h264_qsv,h264_amf,libx264` (NVIDIA/Intel/AMD -> CPU fallback).
*   **macOS (including Apple Silicon)**: `h264_videotoolbox,libx264`.
*   **Linux**: `h264_vaapi,h264_nvenc,h264_qsv,h264_amf,libx264`.

For Apple Silicon, ensure FFmpeg has VideoToolbox encoder support (`h264_videotoolbox`).

Quick diagnostic:
```bash
ffmpeg -hide_banner -encoders
```

### 🚀 How to use

1.  **Run the program** (`ClipAssassin_Reels` or `ClipAssassin_Intro`).
2.  A dialog window will open. **Select the folder** containing your video files and corresponding `.txt` files.
3.  The program will automatically create an `output` folder inside your selected folder and save the clips there.

#### Text File Formats

**For Reels (`ClipAssassin_Reels`):**
```text
00:01:30:15-00:02:00:20
00:03:00-00:04:00 --[My Cool Clip]
```
*Result: `VideoName_My Cool Clip_00-03-00_00-04-00.mp4`*

**For Intros (`ClipAssassin_Intro`):**
```text
06_00:07:45–00:07:53 -- (2 sec) (Phrase: "People pay us")
```
*Result: `06_00-07-45–00-07-53 - (2 sec) (People pay us).mp4`*

---

<a name="russian"></a>
## 🇷🇺 Русский

Этот набор инструментов автоматически обрабатывает видеофайлы для создания Рилсов (Reels) и Интро на основе текстовых файлов.

### 📥 Скачать

Вам не нужно устанавливать Python! Просто скачайте последнюю версию для вашей ОС на странице **[Releases](../../releases)**.

*   **Windows**: Скачивайте `.exe` файлы.
*   **macOS**: Скачивайте `.zip` архивы. Распакуйте их, чтобы получить приложение `.app`.

### ⚠️ Пользователям macOS (Важно!)

При первом запуске macOS может заблокировать программу, так как она от "Неустановленного разработчика".

1.  Нажмите **Правой кнопкой мыши** (или Control+клик) на иконку приложения.
2.  Выберите **Открыть** (Open) в меню.
3.  Нажмите **Открыть** (Open) в появившемся окне.
    *   *Это нужно сделать только один раз.*

### ⚙️ Требования

Перед запуском программы у вас **ОБЯЗАТЕЛЬНО** должен быть установлен **FFmpeg**.

#### Как установить FFmpeg:

*   **Windows**:
    1.  Скачайте `ffmpeg-release-essentials.zip` с сайта [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
    2.  Извлеките файл `ffmpeg.exe` из папки `bin`.
    3.  Положите `ffmpeg.exe` **в ту же папку**, где лежит ваша программа `ClipAssassin_Reels.exe` (или добавьте его в системный PATH).
*   **macOS**:
    *   Установите через Homebrew: `brew install ffmpeg`

### 🎛️ Политика энкодера (GPU/CPU)

Программа поддерживает настройку поведения энкодера через переменные окружения:

```env
CA_ENCODER_POLICY=auto
CA_ENCODER_PRIORITY=h264_nvenc,h264_qsv,h264_amf,libx264
CA_ENCODER_LOG=basic
```

Переменные:
*   `CA_ENCODER_POLICY=auto|strict_gpu|cpu_only` (по умолчанию: `auto`)
    *   `auto`: сначала пробует GPU-энкодеры, при проблемах переходит на CPU (`libx264`).
    *   `strict_gpu`: только аппаратный энкодер; при недоступности завершает с ошибкой.
    *   `cpu_only`: всегда использует `libx264`.
*   `CA_ENCODER_PRIORITY`: опциональное переопределение порядка энкодеров через запятую.
*   `CA_ENCODER_LOG=basic|debug`: `debug` показывает детальные причины пропуска/fallback.

Платформенные приоритеты по умолчанию:
*   **Windows**: `h264_nvenc,h264_qsv,h264_amf,libx264` (NVIDIA/Intel/AMD -> fallback на CPU).
*   **macOS (включая Apple Silicon)**: `h264_videotoolbox,libx264`.
*   **Linux**: `h264_vaapi,h264_nvenc,h264_qsv,h264_amf,libx264`.

Для Apple Silicon убедитесь, что ваша сборка FFmpeg содержит поддержку VideoToolbox (`h264_videotoolbox`).

Быстрая диагностика:
```bash
ffmpeg -hide_banner -encoders
```

### 🚀 Как использовать

1.  **Запустите программу** (`ClipAssassin_Reels` или `ClipAssassin_Intro`).
2.  Откроется окно. **Выберите папку**, в которой лежат ваши видео и текстовые файлы (`.txt`).
3.  Программа автоматически создаст папку `output` внутри выбранной папки и сохранит туда результат.

#### Форматы текстовых файлов

**Для Рилсов (`ClipAssassin_Reels`):**
```text
00:01:30:15-00:02:00:20
00:03:00-00:04:00 --[Мой крутой клип]
```
*Результат: `VideoName_Мой крутой клип_00-03-00_00-04-00.mp4`*

**Для Интро (`ClipAssassin_Intro`):**
```text
06_00:07:45–00:07:53 -- (2 сек) (Фраза: «Люди платят нам»)
```
*Результат: `06_00-07-45–00-07-53 - (2 сек) (Люди платят нам).mp4`*
