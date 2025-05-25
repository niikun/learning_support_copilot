"""FastAPI entry point for the LangGraph-based chatbot.
This module exposes two endpoints:
- GET /           → ヘルスチェック
- GET /query/{q}  → チャットボット応答
"""
import asyncio
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

from .chat_bot import create_response
from .answer_rag import iterate_rag
from .hint_rag import create_hint_rag

app = FastAPI()

class QuestionRequest(BaseModel):
    """質問のリクエストモデル"""
    question: str

class QAResponse(BaseModel):
    """質問応答のレスポンスモデル"""
    response: str


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

@app.post("/create_answer,response_model=QAResponse)")
async def create_answer(req : QuestionRequest):
    """質問を受け取り、モデルに渡して応答を取得する"""
    text = req.question.strip()
    if not text:
        raise HTTPException(status_code=400, detail="質問は空であってはなりません。")
    answer = await iterate_rag(text)
    return {"response": answer}

@app.post("/create_hint",response_model=QAResponse)
async def create_hint(req: QuestionRequest):
    """質問を受け取り、ヒントを生成する"""
    text = req.question.strip()
    if not text:
        raise HTTPException(status_code=400, detail="質問は空であってはなりません。")
    hint = await create_hint_rag(text)
    return {"response": hint}
