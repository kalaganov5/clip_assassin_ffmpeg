# Clip Assassin - FFmpeg Batch Edition

[English](#english) | [Русский](#russian)

<a name="english"></a>
## 🇬🇧 English

This toolset automatically processes video files to create Reels and Intros based on text file inputs.

### Project Structure

*   `REELS/`: Folder for processing Reels.
    *   `input/`: Place source videos and text files here.
    *   `output/`: Generated clips will appear here.
*   `INTROS/`: Folder for processing Intros.
    *   `input/`: Place source videos and text files here.
    *   `output/`: Generated intros will appear here.
*   `scripts/`: Contains the python scripts.
    *   `make_reels.py`: Script for cutting Reels.
    *   `make_intro.py`: Script for cutting Intros.

### Setup

1.  Ensure you have **Python 3.x** and **FFmpeg** installed.
2.  The scripts will automatically create necessary folders if they don't exist.

### How to use

#### 1. Creating Reels

1.  **Put your video** in `REELS/input` (e.g., `interview.mp4`).
2.  **Create a text file** with the **same name** in `REELS/input` (e.g., `interview.txt`).
3.  **Add timecodes** (one range per line). Optionally add a title in brackets `[Title]` after `--`:
    ```text
    00:01:30:15-00:02:00:20
    00:03:00-00:04:00 --[My Cool Clip]
    ```
4.  **Run the script**:
    ```bash
    python scripts/make_reels.py
    ```
5.  **Output**: Files like `interview_My Cool Clip_00-03-00_00-04-00.mp4` in `REELS/output`.

#### 2. Creating Intros

1.  **Put your video** in `INTROS/input`.
2.  **Create a text file** with the **same name** in `INTROS/input`.
3.  **Add timecodes**. The entire line content will be used for the filename (cleaned up).
    ```text
    06_00:07:45–00:07:53 -- (2 sec) (Phrase: "People pay us")
    ```
4.  **Run the script**:
    ```bash
    python scripts/make_intro.py
    ```
5.  **Output**: Files like `06_00-07-45–00-07-53 - (2 sec) (People pay us).mp4` in `INTROS/output`.

---

<a name="russian"></a>
## 🇷🇺 Русский

Этот набор инструментов автоматически обрабатывает видеофайлы для создания Рилсов (Reels) и Интро на основе текстовых файлов.

### Структура проекта

*   `REELS/`: Папка для обработки Рилсов.
    *   `input/`: Сюда кладем исходные видео и текстовые файлы.
    *   `output/`: Здесь появляются готовые клипы.
*   `INTROS/`: Папка для обработки Интро.
    *   `input/`: Сюда кладем исходные видео и текстовые файлы.
    *   `output/`: Здесь появляются готовые интро.
*   `scripts/`: Папка со скриптами.
    *   `make_reels.py`: Скрипт для нарезки Рилсов.
    *   `make_intro.py`: Скрипт для нарезки Интро.

### Установка

1.  Убедитесь, что у вас установлены **Python 3.x** и **FFmpeg**.
2.  Скрипты автоматически создадут нужные папки при запуске.

### Как использовать

#### 1. Создание Рилсов (Reels)

1.  **Поместите видео** в папку `REELS/input` (например, `interview.mp4`).
2.  **Создайте текстовый файл** с **тем же именем** в `REELS/input` (например, `interview.txt`).
3.  **Добавьте таймкоды** (один диапазон на строку). Можно добавить заголовок в квадратных скобках `[Заголовок]` после `--`:
    ```text
    00:01:30:15-00:02:00:20
    00:03:00-00:04:00 --[Мой крутой клип]
    ```
4.  **Запустите скрипт**:
    ```bash
    python scripts/make_reels.py
    ```

    ```bash
    python3 scripts/make_reels.py
    ```
5.  **Результат**: Файлы вида `interview_Мой крутой клип_00-03-00_00-04-00.mp4` в папке `REELS/output`.

#### 2. Создание Интро

1.  **Поместите видео** в папку `INTROS/input`.
2.  **Создайте текстовый файл** с **тем же именем** в `INTROS/input`.
3.  **Добавьте таймкоды**. Вся строка целиком будет использована для имени файла (с очисткой от спецсимволов).
    ```text
    06_00:07:45–00:07:53 -- (2 сек) (Фраза: «Люди платят нам»)
    ```
4.  **Запустите скрипт**:
    ```bash
    python scripts/make_intro.py
    ```
5.  **Результат**: Файлы вида `06_00-07-45–00-07-53 - (2 сек) (Люди платят нам).mp4` в папке `INTROS/output`.
