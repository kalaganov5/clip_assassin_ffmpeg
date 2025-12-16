# Руководство по установке / Installation Guide

Для работы Clip Assassin FFmpeg необходимо установить **Python** и **FFmpeg**.

---

## 🪟 Windows

### 1. Установка Python
1. Перейдите на официальный сайт: [python.org/downloads](https://www.python.org/downloads/).
2. Нажмите большую желтую кнопку **Download Python 3.x.x**.
3. Запустите скачанный установщик.
4. **ВАЖНО:** Внизу поставьте галочку **"Add Python to PATH"** (Добавить Python в PATH).
5. Нажмите **Install Now**.

### 2. Установка FFmpeg
1. Перейдите на сайт [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
2. В разделе "release builds" скачайте **ffmpeg-release-essentials.zip**.
3. Распакуйте архив. Переименуйте папку внутри в `ffmpeg` и переместите её в корень диска `C:\` (чтобы получилось `C:\ffmpeg`).
4. Добавление в систему:
   - Нажмите **Пуск**, введите "изменение системных переменных среды" и откройте.
   - Нажмите **Переменные среды...** (Environment Variables).
   - В разделе **Системные переменные** (нижнее окно) найдите строку **Path** и нажмите **Изменить**.
   - Нажмите **Создать** и введите: `C:\ffmpeg\bin`
   - Нажмите **ОК** во всех окнах.

---

## 🍎 macOS

### 1. Установка Python
MacOS обычно поставляется с Python, но лучше установить свежую версию.
1. Перейдите на [python.org/downloads](https://www.python.org/downloads/).
2. Скачайте и запустите установщик для macOS.
3. Следуйте инструкциям на экране.
4. После установки запустите файл `Install Certificates.command` в папке Python (откроется автоматически или найдите в Программах).

### 2. Установка FFmpeg
Самый простой способ — через Homebrew.

**Если у вас нет Homebrew:**
1. Откройте **Терминал** (Command + Space, введите "Terminal").
2. Вставьте команду и нажмите Enter (потребуется пароль администратора):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

**Установка FFmpeg через Homebrew:**
1. В терминале введите:
   ```bash
   brew install ffmpeg
   ```

---

## ✅ Проверка установки

Откройте терминал (или командную строку) и введите команды:

**Проверка Python:**
```bash
python --version
# или (на mac/linux иногда)
python3 --version
```

**Проверка FFmpeg:**
```bash
ffmpeg -version
```

Если вы видите номера версий, значит всё установлено правильно! Теперь вы можете запускать Clip Assassin.
