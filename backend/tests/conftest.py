import os
import sys
from types import SimpleNamespace

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

import main


class FakeInsertOneResult(SimpleNamespace):
    pass


class FakeUpdateResult(SimpleNamespace):
    pass


class FakeGroupsCollection:
    def __init__(self):
        self.store = {}

    async def insert_one(self, doc):
        self.store[doc["group_id"]] = doc.copy()
        return FakeInsertOneResult(inserted_id=doc["group_id"])

    async def find_one(self, query):
        return self.store.get(query["group_id"])

    async def update_one(self, query, update):
        group = self.store.get(query["group_id"])
        if group is None:
            return FakeUpdateResult(modified_count=0)

        if "$push" in update:
            group["raw_transactions"].append(update["$push"]["raw_transactions"])
        if "$set" in update:
            for key, value in update["$set"].items():
                group[key] = value

        self.store[group["group_id"]] = group
        return FakeUpdateResult(modified_count=1)


class FakeDB:
    def __init__(self):
        self.groups = FakeGroupsCollection()


@pytest.fixture(autouse=True)
def mock_database(monkeypatch):
    fake_db = FakeDB()
    monkeypatch.setattr("app.services.group_service.get_database", lambda: fake_db)
    monkeypatch.setattr("main.connect_to_mongo", AsyncMock())
    monkeypatch.setattr("main.close_mongo_connection", AsyncMock())
    return fake_db


@pytest.fixture
async def async_client(mock_database):
    async with AsyncClient(app=main.app, base_url="http://testserver") as client:
        yield client
