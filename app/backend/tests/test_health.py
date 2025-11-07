from fastapi.testclient import TestClient

from src.main import app
from src.deps import get_db


class DummyDB:
    def execute(self, _: str):
        return 1


client = TestClient(app)


def override_db():
    yield DummyDB()


def test_healthz():
    app.dependency_overrides[get_db] = override_db
    response = client.get("/healthz")
    assert response.status_code == 200
    app.dependency_overrides.clear()
