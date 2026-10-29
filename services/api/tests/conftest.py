import os

os.environ.update(ADMIN_TOKEN="admin-secret", INTERNAL_API_KEY="internal-secret",
                  CANARY_BASE_URL="https://canary.test", DATABASE_URL="sqlite://")

import pytest
from fastapi.testclient import TestClient

from app import db as dbm
from app.main import app


@pytest.fixture
def client():
    dbm.init_engine("sqlite://")
    with TestClient(app) as c:
        yield c


ADMIN = {"Authorization": "Bearer admin-secret"}
INTERNAL = {"X-Internal-Key": "internal-secret"}
