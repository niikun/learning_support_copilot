"""
RAG 用の Retriever を初回実行時に 1 度だけ作り、
以降はキャッシュ済みインスタンスを返すユーティリティ。

依存:
    pip install \
        langchain-openai langchain-chroma \
        unstructured[markdown] nbformat pypdf2
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import List

from langchain_community.document_loaders import (
    TextLoader,
    PythonLoader,
    PyPDFLoader,
    NotebookLoader,
    UnstructuredMarkdownLoader,
)
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

logger = logging.getLogger(__name__)
DATA_DIR = Path("/app/data")  # 必要に応じて変更


# ────────────────────────────────────────────────────────────
# 内部ヘルパ
# ────────────────────────────────────────────────────────────
def _load_file(path: Path) -> List[Document]:
    """拡張子に応じた Loader で Document のリストを返す。失敗時は空リスト。"""
    try:
        if path.suffix == ".txt":
            return TextLoader(str(path)).load()

        if path.suffix == ".md":
            return UnstructuredMarkdownLoader(str(path)).load()

        if path.suffix == ".py":
            return PythonLoader(str(path)).load()

        if path.suffix == ".ipynb":
            # Notebook はセル単位で Document を生成
            return NotebookLoader(str(path)).load_and_split()

        if path.suffix == ".pdf":
            # PDF はページ単位で Document を生成
            return PyPDFLoader(str(path)).load_and_split()

        logger.debug("未対応拡張子のためスキップ: %s", path.name)
    except Exception as exc:  # noqa: BLE001
        logger.warning("読み込み失敗 %s (%s)", path.name, exc)
    return []


# ────────────────────────────────────────────────────────────
# 外部公開関数
# ────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def create_retriever() -> BaseRetriever:
    """
    初回呼び出し時だけドキュメントをロード → 分割 → Chroma に格納し、
    生成した Retriever を返す。2 回目以降はキャッシュを返す。
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise EnvironmentError("環境変数 OPENAI_API_KEY が設定されていません。")

    # 1. ドキュメント読み込み
    docs: List[Document] = []
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"DATA_DIR が存在しません: {DATA_DIR}")

    for path in DATA_DIR.iterdir():
        docs.extend(_load_file(path))

    if not docs:
        raise RuntimeError(f"読み込めたドキュメントが 0 件です: {DATA_DIR}")

    logger.info("Loaded %d raw documents from %s", len(docs), DATA_DIR)

    # 2. チャンク分割
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    logger.info("Split into %d chunks", len(chunks))

    # 3. Embedding & Chroma 構築
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=openai_api_key,
    )
    chroma_db = Chroma.from_documents(chunks, embeddings)
    logger.info("Chroma collection created with %d embeddings", len(chunks))

    # 4. Retriever 化
    retriever = chroma_db.as_retriever(
        search_type="mmr",  # diversity を確保
        search_kwargs={"k": 10, "fetch_k": 40},
    )
    logger.info("Retriever ready (k=10, fetch_k=40, type=mmr)")
    return retriever