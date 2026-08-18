import os
import httpx
from dotenv import load_dotenv
from database import update_mood

load_dotenv()
API_KEY = os.getenv("HF_API_KEY")

def get_available_models():
    # Возвращаем модели, которые точно работают на бесплатном Inference API
    return [
        "Qwen/Qwen2.5-7B-Instruct",
        "meta-llama/Meta-Llama-3-8B-Instruct",
        "mistralai/Mistral-7B-Instruct-v0.3"
    ]

MOOD_PROMPTS = {
    "joyful": "Перепиши новость максимально радостно и оптимистично.",
    "sad": "Перепиши новость в мрачном, грустном и депрессивном тоне.",
    "ironic": "Перепиши новость в саркастичном и ироничном стиле.",
    "neutral": "Перепиши новость сухо, нейтрально и максимально объективно."
}

# Новый актуальный эндпоинт Hugging Face (Router)
API_URL = "https://router.huggingface.co/v1/chat/completions"

def rewrite_text(news_id, original_text, mood, model_name):
    system_prompt = f"""
    Ты профессиональный редактор. {MOOD_PROMPTS.get(mood, 'Перепиши нейтрально')}.
    СТРОГИЕ ПРАВИЛА:
    1. НЕЛЬЗЯ менять имена, фамилии, названия компаний, цифры, даты, суммы и места.
    2. НЕЛЬЗЯ добавлять новые факты или выдумывать события, которых нет в исходном тексте.
    3. Разрешено менять только прилагательные, наречия и структуру предложений для передачи нужного настроения.
    4. Сохраняй смысл новости неизменным.
    """
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": original_text}
        ],
        "temperature": 0.2,
        "max_tokens": 1024
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            rewritten = result['choices'][0]['message']['content']
            
            cache_key = f"{mood}_{model_name}"
            update_mood(news_id, cache_key, rewritten)
            return rewritten
    except Exception as e:
        print(f"Ошибка Hugging Face API: {e}")
        if "502" in str(e) or "503" in str(e) or "429" in str(e):
            return "Сервер Hugging Face перегружен. Попробуйте выбрать другую модель или нажать 'Обновить ленту'."
        return f"Ошибка генерации: {str(e)}"