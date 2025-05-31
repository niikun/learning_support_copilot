import os
import asyncio
from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import BaseRetriever, Document
from langchain_openai import ChatOpenAI

from .create_retriever import create_retriever

META_INSTRUCT = (
    "あなたはメタ認知エージェントです。"
    "以下の文脈と質問だけで最終回答を今すぐ出せるか判断し、"
    "『回答可能』または『回答不可』のどちらか一語だけを出力してください。"
)

async def create_hint_rag(question:str,max_cycles:int=3) ->str:
    """
    RAGを使用して質問のヒントを提供する関数
    Args:
        question (str): 質問
        max_cycles (int): 最大サイクル数
    Returns:
        str: 回答につながるヒント
    """
    llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0.0,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
    retriever: BaseRetriever = create_retriever()
    
    # プロンプト定義
    meta_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "必ず『回答可能』または『回答不可』のどちらか一語で答えてください。"),
            ("human",
            "ユーザーの質問: {question}\n"
            "現時点の文脈:\n{context}\n"
            "→ 上記の情報だけで回答できますか？")
        ]
    )

    extract_prompt = ChatPromptTemplate.from_template(
        "質問: {question}\n"
        "→ 検索に使うキーワード（名詞や固有表現）を列挙してください。"
    )

    summarize_prompt = ChatPromptTemplate.from_template(
        "検索結果:\n{snippets}\n"
        "→ 上記を要点だけ短く要約してください。"
    )

    final_prompt = ChatPromptTemplate.from_template(
        "これまでの要約コンテキスト:\n{context}\n"
        "質問: {question}\n"
        "→ 答えを直接教えず、答えにつながるヒントを生成してください。"
        "ヒントは日本語でわかりやすく、"
        "ユーザーが次のステップを考える手助けとなるようにしてください。"
        "ヒントは具体的で、ユーザーが次に何をすべきかを示唆する内容にしてください。"
    )


    context = ""  # 初期文脈は空、もしくは事前知識
    for cycle in range(max_cycles):
        # 1) メタ認知フェーズ（RaQ）
        decision = (await llm.ainvoke(
            meta_prompt.format_messages(question=question, context=context)
        )).content.strip()
        if "回答可能" in decision:
            break

        # 2) キーワード抽出
        keywords = (await llm.ainvoke(
            extract_prompt.format_messages(question=question)
        )).content.strip()

        # 3) 検索フェーズ
        docs: List[Document] = await retriever.ainvoke(keywords)
        snippets = "\n".join(d.page_content for d in docs[:5])

        # 4) 要約フェーズ（pKA）
        summary = (await llm.ainvoke(
            summarize_prompt.format_messages(snippets=snippets)
        )).content.strip()

        # 5) コンテキストに追加
        context += "\n" + summary

    # 6) 最終回答フェーズ
    final_answer = (await llm.ainvoke(
        final_prompt.format_messages(context=context, question=question)
    )).content.strip()

    return final_answer
