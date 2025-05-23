"""FastAPI entry point for the LangGraph-based chatbot.
This module exposes two endpoints:
- GET /           → ヘルスチェック
- GET /query/{q}  → チャットボット応答
"""

from fastapi import FastAPI, HTTPException
from .chat_bot import create_response

app = FastAPI()


@app.get("/")
def read_root():
    """ヘルスチェック用のシンプルなエンドポイント"""
    return {"Hello": "World"}


@app.get("/query/{query}")
def answer(query: str):
    """クエリを受け取り、モデルに渡して応答を取得する"""
    text = query.strip()
    if not text:
        raise HTTPException(status_code=400, detail="クエリは空であってはなりません。")
    response = create_response(text)
    return {"response": response.content}
