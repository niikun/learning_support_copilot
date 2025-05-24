"""
RAGのRetrieverを作成するためのコードです。
"""

import os
from langchain_community.document_loaders import TextLoader, PythonLoader, PyPDFLoader, NotebookLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

retriever_cache = None

def create_retriever():
    global retriever_cache
    if retriever_cache is not None:
        return retriever_cache

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEYが設定されていません。")

    docs = []
    data_dir = "/app/data"
    for fname in os.listdir(data_dir):
        fpath = os.path.join(data_dir, fname)
        if fname.endswith(".txt"):
            docs.extend(TextLoader(fpath).load())
        elif fname.endswith(".md"):
            docs.extend(UnstructuredMarkdownLoader(fpath).load())
        elif fname.endswith(".py"):
            docs.extend(PythonLoader(fpath).load())
        elif fname.endswith(".ipynb"):
            docs.extend(NotebookLoader(fpath).load())
        elif fname.endswith(".pdf"):
            docs.extend(PyPDFLoader(fpath).load())
        # 必要なら他の拡張子も追加

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=openai_api_key,
    )
    db = Chroma.from_documents(all_splits, embeddings)
    retriever_cache = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5},
    )
    return retriever_cache



