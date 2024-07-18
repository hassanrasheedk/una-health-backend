from fastapi.testclient import TestClient
from main import app, get_db
from models import Base, engine
from sqlalchemy.orm import sessionmaker
import pytest

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_app():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def db_session():
    db = SessionTesting()
    yield db
    db.close()

def test_create_glucose_level(test_app, db_session):
    response = test_app.post("/api/v1/levels/", json={"user_id": "test_user", "timestamp": "2023-01-01T00:00:00", "glucose_value": 100.0})
    assert response.status_code == 200
    assert response.json()["user_id"] == "test_user"

def test_get_glucose_levels(test_app, db_session):
    response = test_app.get("/api/v1/levels/?user_id=test_user")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_glucose_level(test_app, db_session):
    response = test_app.get("/api/v1/levels/1")
    assert response.status_code == 200
    assert response.json()["user_id"] == "test_user"