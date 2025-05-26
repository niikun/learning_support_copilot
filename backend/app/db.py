import datetime as dt
from pathlib import Path
from sqlalchemy import DateTime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# データベースファイルの絶対パスを決定（.env は使わない）
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'eval.db'
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# 非同期エンジンの生成
engine = create_async_engine(
    DATABASE_URL,
    echo=True,       # SQL ログを出力して動作確認しやすく
    future=True,
)

# 非同期セッションメーカー
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base クラス定義
class Base(DeclarativeBase):
    pass

# Evaluation モデル定義
class Evaluation(Base):
    __tablename__ = "evaluations"

    id:         Mapped[int]         = mapped_column(primary_key=True)
    question:   Mapped[str]         = mapped_column(nullable=False)
    answer:     Mapped[str]         = mapped_column(nullable=False)
    score:      Mapped[int]         = mapped_column(nullable=False)
    reason:     Mapped[str | None]  = mapped_column(nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime,
        default=dt.datetime.utcnow,
        nullable=False,
    )

# セッション取得用の依存関数
async def get_session() -> AsyncSession:
    """
    FastAPI などでの依存注入用: async for でセッションを取得し、自動でクローズ
    """
    async with async_session() as session:
        yield session

# テーブル作成用ユーティリティ
async def init_db() -> None:
    """
    アプリ起動時などに呼び出してテーブルを作成
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
