import os
from sqlalchemy import Integer, String, Text, create_engine, text  # <--- Add text here
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from pgvector.sqlalchemy import Vector

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://fitcoach:fitcoach@localhost:5432/fitcoach"
)
EMBEDDING_DIM = 384  # must match the embedding model

class Base(DeclarativeBase):
    pass

class ChunkModel(Base):
    __tablename__ = "chunks"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    document_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    page: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector(EMBEDDING_DIM), nullable=False)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def init_db() -> None:
    """Creates tables and enables the vector extension."""
    with engine.begin() as conn:
        # Wrap raw SQL strings with text()
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)