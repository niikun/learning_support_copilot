from fastapi import FastAPI
from langchain_openai import ChatOpenAI

app = FastAPI()

model = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0.0,
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/query/{query}")
def answer(query: str = None):
    """クエリを受け取り、モデルに渡して応答を取得する"""
    query = query.strip()
    if not query:
        return {"error": "クエリが空です"}
    response = model.invoke(query)
    if response and isinstance(response, list) and len(response) > 0:
        # 最初の要素を取得
        first_response = response[0]
        if isinstance(first_response, dict) and "generated_text" in first_response:
            generated_text = first_response["generated_text"]
            return {"response": generated_text}
        else:
            return {"error": "予期しない応答形式"}
    else:
        return {"error": "応答が空または無効です"}
