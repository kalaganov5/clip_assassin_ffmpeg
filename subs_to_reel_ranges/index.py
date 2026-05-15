import os
import time
import datetime
from google import genai
from dotenv import load_dotenv

# ================= НАСТРОЙКИ =================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Переменная GEMINI_API_KEY не найдена в .env")

# Используем модель из твоей документации
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")
if not MODEL_NAME:
    raise ValueError("Переменная GEMINI_MODEL_NAME не найдена в .env")

# Примерные цены за 1 млн токенов (для лога)
PRICE_INPUT_1M = 2.00
PRICE_OUTPUT_1M = 12.00
# =============================================

INPUT_DIR = "input_subs"
OUTPUT_DIR = "output_txt"
PROMPT_FILE = "prompt.txt"
LOG_FILE = "usage_log.txt"

# Инициализация нового клиента по стандарту 2026 года
client = genai.Client(api_key=API_KEY)

def log_usage(filename, usage):
    """Записывает использование токенов и стоимость."""
    # В новой библиотеке метаданные лежат здесь:
    prompt_tokens = usage.prompt_token_count or 0
    candidate_tokens = usage.candidates_token_count or 0
    
    cost_in = (prompt_tokens / 1_000_000) * PRICE_INPUT_1M
    cost_out = (candidate_tokens / 1_000_000) * PRICE_OUTPUT_1M
    total_cost = cost_in + cost_out
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"[{timestamp}] Файл: {filename} | "
        f"In: {prompt_tokens} t, Out: {candidate_tokens} t | "
        f"Cost: ${total_cost:.5f}\n"
    )
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    return total_cost

def setup():
    """Создает папки, если их нет."""
    for folder in [INPUT_DIR, OUTPUT_DIR]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    if not os.path.exists(PROMPT_FILE):
        print(f"⚠️ Внимание: Создай файл {PROMPT_FILE} и положи туда свой промт!")

def run():
    if not os.path.exists(PROMPT_FILE):
        return
        
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        base_prompt = f.read().strip()

    # Ищем файлы субтитров
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.srt', '.vtt'))]
    
    if not files:
        print(f"ℹ️ Положи .srt файлы в папку '{INPUT_DIR}'")
        return

    print(f"🚀 Запуск конвейера. Модель: {MODEL_NAME}")
    print("-" * 50)
    
    total_session_cost = 0

    for filename in files:
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(OUTPUT_DIR, f"{base_name}.txt")

        # Если уже обработано — пропускаем
        if os.path.exists(output_path):
            continue

        print(f"⏳ Обработка: {filename}...", end=" ", flush=True)

        try:
            with open(os.path.join(INPUT_DIR, filename), 'r', encoding='utf-8') as f:
                content = f.read()

            # Вызов модели через новый клиент
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=f"{base_prompt}\n\nТЕКСТ СУБТИТРОВ:\n{content}"
            )
            
            # Сохраняем результат
            if response.text:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text.strip())
                
                # Считаем стоимость из метаданных ответа
                cost = log_usage(filename, response.usage_metadata)
                total_session_cost += cost
                print(f"✅ Готово! (${cost:.4f})")
            else:
                print("⚠️ Пустой ответ.")

            # Небольшая пауза, чтобы API не ругался на скорость
            time.sleep(2)

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)

    print("-" * 50)
    print(f"🎉 Все готово! Результаты в папке: {OUTPUT_DIR}")
    print(f"💰 Общая стоимость этой сессии: ${total_session_cost:.4f}")

if __name__ == "__main__":
    setup()
    run()
