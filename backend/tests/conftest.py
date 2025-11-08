from __future__ import annotations

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401 - đảm bảo model được load
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models.user import User
from app.storage.local import storage

TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app = create_app()
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client(tmp_path):
    try:
        from fastapi.testclient import TestClient
    except Exception:
        pytest.skip("httpx không khả dụng nên bỏ qua integration tests")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    admin = User(email="admin@example.com", password_hash=get_password_hash("admin123"), role="admin")
    db.add(admin)
    db.commit()
    db.close()
    storage.base_dir = tmp_path
    with TestClient(app) as c:
        yield c
