"""FastAPI entry point for the LangGraph-based chatbot.
This module exposes two endpoints:
- GET /           → ヘルスチェック
- GET /query/{q}  → チャットボット応答
"""

from fastapi import FastAPI, HTTPException
from .chat_bot import create_response
from .dual_rag import iterate_rag
from .hint_rag import create_hint_rag

app = FastAPI()


@app.get("/")
def read_root():
    """ヘルスチェック用のシンプルなエンドポイント"""
    return {"Hello": "World"}


@app.get("/chat/{query}")
def chat(query: str):
    """クエリを受け取り、モデルに渡して応答を取得する"""
    text = query.strip()
    if not text:
        raise HTTPException(status_code=400, detail="クエリは空であってはなりません。")
    response = create_response(text)
    return {"response": response.content}

@app.get("/create_answer/{question}")
def create_answer(question: str):
    """質問を受け取り、モデルに渡して応答を取得する"""
    text = question.strip()
    if not text:
        raise HTTPException(status_code=400, detail="質問は空であってはなりません。")
    response = iterate_rag(text)
    return {"response": response}

@app.get("/create_hint/{question}")
def create_hint(question: str):
    """質問を受け取り、ヒントを生成する"""
    text = question.strip()
    if not text:
        raise HTTPException(status_code=400, detail="質問は空であってはなりません。")
    response = create_hint_rag(text)
    return {"response": response}
