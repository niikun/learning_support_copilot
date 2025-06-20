# Learning Support Copilot

[![CI](https://github.com/niikun/learning_support_copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/niikun/learning_support_copilot/actions/workflows/ci.yml)

学習支援を目的としたRAG（Retrieval-Augmented Generation）ベースのAIチャットボットシステムです。

## 概要

このプロジェクトは、学習者の質問に対して適切な回答とヒントを提供するAI学習支援システムです。FastAPIベースのバックエンドAPI、Reactフロントエンド、そして管理ダッシュボードを含む完全なWebアプリケーションとして構築されています。

## 主な機能

- **RAGベースの質問応答**: 学習資料に基づいた正確な回答を生成
- **ヒント生成**: 直接的な回答ではなく、学習を促進するヒントを提供
- **自動評価システム**: 生成された回答の品質を自動的に評価
- **管理ダッシュボード**: 評価データの可視化と分析
- **データエクスポート**: 評価結果をCSV/JSON形式でエクスポート
- **ファイルアップロード**: 学習資料のアップロード機能

## 技術スタック

### バックエンド
- **FastAPI**: 高性能なPython Webフレームワーク
- **LangChain**: LLMアプリケーション開発フレームワーク
- **ChromaDB**: ベクトルデータベース
- **Redis**: キャッシュシステム
- **SQLAlchemy**: データベースORM
- **Matplotlib**: データ可視化

### フロントエンド
- **React**: UIフレームワーク
- **React Router**: ルーティング
- **React Markdown**: マークダウン表示

### インフラストラクチャ
- **Docker**: コンテナ化
- **Docker Compose**: マルチコンテナ管理

## セットアップ

### 前提条件
- Docker
- Docker Compose
- OpenAI API Key
- LangChain API Key (オプション)

### 環境変数の設定

プロジェクトルートに`.env`ファイルを作成し、以下の変数を設定してください：

```bash
OPENAI_API_KEY=your_openai_api_key
LANGCHAIN_API_KEY=your_langchain_api_key  # オプション
```

### 起動方法

```bash
# リポジトリをクローン
git clone https://github.com/niikun/learning_support_copilot.git
cd learning_support_copilot

# Docker Composeでサービスを起動
docker-compose up -d

# ログを確認
docker-compose logs -f
```

## サービスへのアクセス

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **API ドキュメント**: http://localhost:8000/docs
- **ChromaDB**: http://localhost:8001
- **Redis**: localhost:6379

## API エンドポイント

### 主要エンドポイント

- `GET /` - ヘルスチェック
- `GET /chat/{query}` - 簡単なチャット応答
- `POST /create_answer` - 質問に対する回答生成と評価
- `POST /create_hint` - ヒント生成
- `POST /upload` - ファイルアップロード
- `GET /export/evaluations` - 評価データのエクスポート
- `GET /metrics/quality/daily.png` - 品質メトリクスの可視化

### リクエスト例

```bash
# 回答生成
curl -X POST "http://localhost:8000/create_answer" \
  -H "Content-Type: application/json" \
  -d '{"question": "Dockerとは何ですか？"}'

# ヒント生成
curl -X POST "http://localhost:8000/create_hint" \
  -H "Content-Type: application/json" \
  -d '{"question": "Dockerとは何ですか？"}'
```

## 開発

### 開発環境での起動

```bash
# バックエンドのみ起動（開発用）
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# フロントエンドのみ起動（開発用）
cd frontend
npm install
npm start
```

### テスト実行

```bash
# バックエンドテスト
cd backend
python -m pytest app/tests/

# フロントエンドテスト
cd frontend
npm test
```

## プロジェクト構造

```
learning_support_copilot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPIアプリケーション
│   │   ├── chat_bot.py          # チャットボット機能
│   │   ├── answer_rag.py        # RAG回答生成
│   │   ├── hint_rag.py          # ヒント生成
│   │   ├── evaluator.py         # 回答評価システム
│   │   ├── db.py                # データベース設定
│   │   └── tests/
│   ├── data/                    # 学習資料
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── AdminDashboard.js    # 管理ダッシュボード
│   │   └── ...
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yaml
└── README.md
```

## 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 関連リソース

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [React Documentation](https://react.dev/)
- [ChromaDB Documentation](https://docs.trychroma.com/)