import httpx
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from database import save_news

def fetch_and_save_news():
    rss_url = "https://rssexport.rbc.ru/rbcnews/news/30/full.rss"
    
    try:
        # Скачиваем RSS ленту
        with httpx.Client(timeout=10.0) as client:
            response = client.get(rss_url)
            response.raise_for_status()
        
        # Парсим XML встроенными средствами Python
        root = ET.fromstring(response.content)
        
        news_list = []
        # Ищем все теги <item> в ленте
        for item in root.findall('.//item')[:10]:
            title = item.findtext('title', '').strip()
            link = item.findtext('link', '').strip()
            description = item.findtext('description', '').strip()
            
            # Очищаем описание от HTML-тегов
            soup = BeautifulSoup(description, "html.parser")
            clean_text = soup.get_text(separator=" ", strip=True)
            
            if title and clean_text:
                news_list.append({
                    'title': title,
                    'original_text': clean_text,
                    'source_url': link,
                    'source_name': 'РБК'
                })
        
        if news_list:
            save_news(news_list)
            print(f"Сохранено {len(news_list)} новостей.")
        else:
            print("Не удалось получить новости.")
            
    except Exception as e:
        print(f"Ошибка при парсинге: {e}")

if __name__ == "__main__":
    fetch_and_save_news()