"""Pytest fixtures for MediaFetch tests."""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set a test database URL before importing app modules
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# Now import app modules
from app.database import Base, get_db
from app.main import app
from app.models import DownloadTask


@pytest.fixture(scope="session")
def test_engine():
    """Create a SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///./test.db",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    # Clean up the test file after tests
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture
def db_session(test_engine):
    """Create a fresh database session for each test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    """Return a TestClient instance with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clear_db(db_session):
    """Clear all download tasks before each test."""
    db_session.query(DownloadTask).delete()
    db_session.commit()
    yield