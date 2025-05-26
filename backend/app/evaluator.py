import os
import datetime as dt
from pydantic import BaseModel,Field, ValidationError, conint, constr
import json
from langchain_openai import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate

class EvalResult(BaseModel):
    """
    評価結果のモデル
    Attributes:
        score (conint): スコア（1〜10）
        reason (constr): 理由（100文字以内）
    """
    score: conint(ge=1, le=10)
    reason: constr(strip_whitespace=True, min_length=1, max_length=100)

    @classmethod
    def from_llm(cls,raw_json:str)-> "EvalResult":
        """
        LLMからの生のJSON文字列をパースしてEvalResultインスタンスを生成
        Args:
            raw_json (str): LLMからの生のJSON文字列
        Returns:
            EvalResult: パースされた評価結果
        """
        try:
            data = json.loads(raw_json)
            return cls.model_validate(data)   # v2 系
        except (json.JSONDecodeError, ValidationError):
            return cls(score=1, reason="LLM 出力のパース失敗")

_evaluator_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
     "あなたは厳格なレビュワーです。以下の質問と回答を 1〜10 点で採点し、"
     "理由を簡潔に述べて JSON で出力してください。フォーマット: "
     '{{"score": <int>, "reason": "<string>"}}'
     "例）"
        '{{"score": 8, "reason": "回答は正確で、詳細な説明がありました。"}}'),
    ("human", "質問:\n{question}\n\n回答:\n{answer}")
    ]
)

_evaluator_llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0.0,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    max_retries=3,
    timeout=20,
)

async def evaluate_answer(question:str, answer:str)-> EvalResult:
    """
    質問と回答を評価する関数
    Args:
        question (str): 質問
        answer (str): 回答
    Returns:
        dict: 評価結果（スコアと理由）
    """
    if not question or not answer:
        raise ValueError("質問と回答は必須です。")

    response = await _evaluator_llm.ainvoke(
        _evaluator_prompt.format_messages(question=question, answer=answer)
    )
    
    # レスポンスから JSON をパース
    try:
        result = response.content.strip()
        return EvalResult.from_llm(result)
    except Exception as e:
        raise ValueError(f"評価結果のパースに失敗しました: {e}")