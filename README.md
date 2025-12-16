# Clip Assassin - FFmpeg Batch Edition

[English](#english) | [Русский](#russian)

<a name="english"></a>
## 🇬🇧 English

This script automatically processes video files placed in the `input` folder and saves the cut segments to the `output` folder.

### Setup

1.  Ensure you have **Python 3.x** and **FFmpeg** installed.
2.  The script will automatically create `input` and `output` folders if they don't exist.

### How to use

1.  **Put your video** in the `input` folder (e.g., `interview.mp4`).
2.  **Create a text file** with the **same name** in the `input` folder (e.g., `interview.txt`).
3.  **Add timecodes** to the text file (one range per line). You can optionally add a title in brackets `[Title]` after `--` to include it in the filename:
    ```text
    00:01:30:15-00:02:00:20
    00:03:00-00:04:00 --[My Cool Clip]
    ```
4.  **Run the script**:
    ```bash
    python clip_assassin_ffmpeg.py
    ```

### Output

The script will generate separate video files for each time range in the `output` folder.
The filenames will include the original name, optional title, and the time range.

**Example:**
*   Input: `input/interview.mp4`
*   Range: `00:03:00-00:04:00 --[My Cool Clip]`
*   Output: `output/interview_My Cool Clip_00-03-00_00-04-00.mp4`

---

<a name="russian"></a>
## 🇷🇺 Русский

Этот скрипт автоматически обрабатывает видеофайлы, помещенные в папку `input`, и сохраняет нарезанные сегменты в папку `output`.

### Установка

1.  Убедитесь, что у вас установлены **Python 3.x** и **FFmpeg**.
2.  Скрипт автоматически создаст папки `input` и `output`, если они не существуют.

### Как использовать

1.  **Поместите ваше видео** в папку `input` (например, `interview.mp4`).
2.  **Создайте текстовый файл** с **тем же именем** в папке `input` (например, `interview.txt`).
3.  **Добавьте таймкоды** в текстовый файл (один диапазон на строку). Вы можете добавить заголовок в квадратных скобках `[Заголовок]` после `--`, чтобы включить его в имя файла:
    ```text
    00:01:30:15-00:02:00:20
    00:03:00-00:04:00 --[Мой крутой клип]
    ```
4.  **Запустите скрипт**:
    ```bash
    python clip_assassin_ffmpeg.py
    ```

### Результат

Скрипт создаст отдельные видеофайлы для каждого временного диапазона в папке `output`.
Имена файлов будут включать оригинальное название, заголовок (если есть) и временной диапазон.

**Пример:**
*   Вход: `input/interview.mp4`
*   Диапазон: `00:03:00-00:04:00 --[Мой крутой клип]`
*   Выход: `output/interview_Мой крутой клип_00-03-00_00-04-00.mp4`
