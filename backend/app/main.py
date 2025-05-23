import os
from fastapi import FastAPI
from .chat_bot import create_response

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/query/{query}")
def answer(query: str):
    """クエリを受け取り、モデルに渡して応答を取得する"""
    query = query.strip()
    if not query:
        raise ValueError("クエリは空であってはなりません。")
    response = create_response(query)
    return {"response": response.content}