"""gpt4o-miniを使用して質問に答えるためのコード"""

import os
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0.0,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)


def create_response(query: str):
    """クエリを受け取り、モデルに渡して応答を取得する"""
    query = query.strip()
    if not query:
        raise ValueError("クエリは空であってはなりません。")
    response = model.invoke(query)
    return response
