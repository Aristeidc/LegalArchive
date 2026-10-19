import pytest
from fastapi.testclient import TestClient

import database
from main import app


@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(database,"DB_PATH",tmp_path / "test.db")
    with TestClient(app) as test_client:
        yield test_client

