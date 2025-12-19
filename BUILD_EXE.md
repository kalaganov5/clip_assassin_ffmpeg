# Инструкция по сборке (Build Instructions)

## 🤖 Автоматическая сборка (GitHub Actions)

Этот проект настроен на автоматическую сборку при каждом обновлении (push) или создании релиза.
*   Зайдите во вкладку **Actions** на GitHub, чтобы увидеть процесс сборки.
*   Готовые файлы можно скачать из **Artifacts** (для каждого коммита) или **Releases** (для стабильных версий).

---

## 🛠 Ручная сборка (Manual Build)

Чтобы превратить скрипты в программы (.exe / binary) локально, выполните следующие шаги.

### 1. Установка PyInstaller

Откройте терминал и установите библиотеку:

```bash
pip install pyinstaller
```

### 2. Сборка программ

Выполните эти команды в терминале (находясь в корне проекта):

#### Windows
```bash
pyinstaller --onefile --console --name "ClipAssassin_Reels" scripts/make_reels.py
pyinstaller --onefile --console --name "ClipAssassin_Intro" scripts/make_intro.py
```

#### macOS
```bash
# Создание .app бандла
pyinstaller --windowed --name "ClipAssassin_Reels" scripts/make_reels.py
pyinstaller --windowed --name "ClipAssassin_Intro" scripts/make_intro.py
```

#### Linux
```bash
pyinstaller --onefile --name "ClipAssassin_Reels" scripts/make_reels.py
pyinstaller --onefile --name "ClipAssassin_Intro" scripts/make_intro.py
```

### 3. Где искать готовые программы?

После сборки у вас появится папка `dist`. В ней будут лежать исполняемые файлы.

### 4. Как использовать

1.  Заберите файлы из папки `dist`.
2.  Запустите программу.
3.  Откроется окно выбора папки. Выберите папку, где лежат ваши видео и текстовые файлы.

**Важно:** Рядом с программой (или в системе) должен быть установлен **FFmpeg**.
