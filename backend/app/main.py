"""FastAPI entry point for the LangGraph-based chatbot.
This module exposes two endpoints:
- GET /           → ヘルスチェック
- GET /query/{q}  → チャットボット応答
"""
import shutil
from pathlib import Path
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends,UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from fastapi.responses import StreamingResponse, Response, JSONResponse
from sqlalchemy import select, func, text
import pandas as pd
import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates 

from .chat_bot import create_response
from .answer_rag import iterate_rag
from .hint_rag import create_hint_rag
from .evaluator import evaluate_answer
from .db import Evaluation, get_session, init_db

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 必要に応じて制限
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    """質問のリクエストモデル"""
    question: str

class QAResponse(BaseModel):
    """質問応答のレスポンスモデル"""
    response: str
    score: Optional[int] = None


@app.on_event("startup")
async def on_startup():
    await init_db()

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

@app.post("/create_answer",response_model=QAResponse)
async def create_answer(
    req : QuestionRequest,
    session: AsyncSession = Depends(get_session),):
    """質問を受け取り、モデルに渡して応答を取得する"""

    text = req.question.strip()
    if not text:
        raise HTTPException(status_code=400, detail="質問は空であってはなりません。")
    
    # 1) 回答生成
    answer = await iterate_rag(text)

    # 2) 自動評価
    eval_res = await evaluate_answer(text, answer)

    # 3) DB へ保存
    record = Evaluation(
        question=text,
        answer=answer,
        score=eval_res.score,
        reason=eval_res.reason,
    )
    session.add(record)
    await session.commit()
    return {"response": answer, "score": eval_res.score}

@app.post("/create_hint",response_model=QAResponse)
async def create_hint(req: QuestionRequest):
    """質問を受け取り、ヒントを生成する"""
    text = req.question.strip()
    if not text:
        raise HTTPException(status_code=400, detail="質問は空であってはなりません。")
    hint = await create_hint_rag(text)
    return {"response": hint}

# --- 評価データのエクスポート ---
@app.get("/export/evaluations")
async def export_evaluations(
    start: Optional[str] = None,
    end:   Optional[str] = None,
    fmt:   str = "csv",
    session: AsyncSession = Depends(get_session),
):
    """
    評価データを CSV または JSON でダウンロード。
    ・start, end は ISO8601 形式の日付文字列 (例: 2025-05-01)
    ・fmt=csv (デフォルト) or fmt=json
    """
    q = select(Evaluation)
    if start:
        q = q.where(Evaluation.created_at >= start)
    if end:
        q = q.where(Evaluation.created_at < end)
    result = await session.execute(q)
    records = result.scalars().all()

    # DataFrame に変換
    df = pd.DataFrame([{
        "id": rec.id,
        "question": rec.question,
        "answer": rec.answer,
        "score": rec.score,
        "reason": rec.reason,
        "created_at": rec.created_at.isoformat(),
    } for rec in records])

    if fmt.lower() == "json":
        return JSONResponse(content=df.to_dict(orient="records"))

    # CSV をストリーミング
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    headers = {
        "Content-Disposition": "attachment; filename=\"evaluations.csv\""
    }
    return StreamingResponse(buf, media_type="text/csv", headers=headers)

@app.get("/metrics/quality/daily.png")
async def daily_quality_from_db(session: AsyncSession = Depends(get_session)):
    # 1) DB から集計
    q = (
        select(
            func.date(Evaluation.created_at).label("day"),
            func.avg(Evaluation.score).label("avg_score"),
        )
        .group_by(func.date(Evaluation.created_at))
        .order_by(func.date(Evaluation.created_at))
    )
    result = await session.execute(q)
    rows = result.all()
    df = pd.DataFrame(rows, columns=["day", "avg_score"])
    df["day"] = pd.to_datetime(df["day"])

    # 2) 最新日を基準に過去 30 日分にフィルタ
    end = df["day"].max()
    start = end - pd.Timedelta(days=30)
    df = df[(df["day"] >= start) & (df["day"] <= end)]

    # 3) プロット
    fig, ax = plt.subplots()
    ax.plot(df["day"], df["avg_score"], marker="o")
    ax.set_xlim(start, end)

    # 週ごと（または interval=5 なら5日おき）の目盛り表示
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    fig.autofmt_xdate()

    ax.set_title("Dayly Average")
    ax.set_xlabel("DateDate")
    ax.set_ylabel("Average Score")
    ax.set_ylim(0, 10)

    # 4) PNG にして返却
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return Response(buf.getvalue(), media_type="image/png")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # 絶対パスで保存（Dockerなら /app/data/ などに合わせる）
    save_dir = Path("/app/data")
    save_dir.mkdir(parents=True, exist_ok=True)  # ディレクトリがなければ作成
    path = save_dir / file.filename
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"filename": file.filename}
