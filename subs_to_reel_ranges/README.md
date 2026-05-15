# subs_to_reel_ranges

Скрипт берет `.srt/.vtt` из `input_subs`, отправляет текст в Gemini и сохраняет результат в `output_txt` как `.txt`.

## 1. Требования

- Windows + PowerShell
- Python 3.10+
- Установленные пакеты:
  - `google-genai`
  - `python-dotenv`

Установка:

```powershell
py -m pip install google-genai python-dotenv
```

## 2. Настройка `.env`

Создайте файл `.env` (в корне проекта или в папке `subs_to_reel_ranges`) и добавьте:

```env
GEMINI_API_KEY=your_real_api_key
GEMINI_MODEL_NAME=gemini-2.5-pro
```

## 3. Подготовка файлов

1. Положите файлы субтитров `.srt` или `.vtt` в папку `input_subs`.
2. Проверьте/отредактируйте `prompt.txt` в этой же папке.

Структура:

```text
subs_to_reel_ranges/
  index.py
  prompt.txt
  input_subs/
  output_txt/
```

## 4. Запуск

Запускать из папки `subs_to_reel_ranges`:

```powershell
cd .\subs_to_reel_ranges
py .\index.py
```

## 5. Результат

- Для каждого входного файла создается `.txt` в `output_txt`.
- Лог токенов и примерной стоимости пишется в `usage_log.txt`.

## 6. Частые ошибки

- `Переменная GEMINI_API_KEY не найдена в .env`  
  Проверьте, что переменная есть в `.env`.

- `Переменная GEMINI_MODEL_NAME не найдена в .env`  
  Добавьте модель в `.env`, например `gemini-2.5-pro`.

- `Положи .srt файлы в папку 'input_subs'`  
  В папке `input_subs` нет подходящих файлов.
