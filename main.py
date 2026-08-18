from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from database import init_db, get_all_news, get_news_by_id
from scraper import fetch_and_save_news
from ai_service import rewrite_text, get_available_models
import uvicorn
import json

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup_event():
    init_db()
    if not get_all_news():
        fetch_and_save_news()

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/api/news")
def api_get_news():
    return get_all_news()

@app.get("/api/models")
def api_get_models():
    return get_available_models()

@app.post("/api/news/{news_id}/rewrite")
def api_rewrite_news(news_id: int, mood: str, model: str):
    news = get_news_by_id(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    
    moods = json.loads(news['moods']) if news['moods'] else {}
    cache_key = f"{mood}_{model}"
    
    if cache_key in moods:
        return {"text": moods[cache_key]}
    
    rewritten_text = rewrite_text(news_id, news['original_text'], mood, model)
    return {"text": rewritten_text}

@app.post("/api/parse")
def api_parse():
    fetch_and_save_news()
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)