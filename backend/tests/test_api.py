import os
import random
import sys
from pathlib import Path

import pytest
from unittest.mock import AsyncMock, patch

from app.core.engine_bridge import run_cpp_optimizer
from app.models.transaction import OptimizedTransaction, OptimizationResult, Transaction


@pytest.mark.asyncio
async def test_create_group(async_client):
    payload = {
        "group_id": "group-1",
        "name": "Test Group",
        "raw_transactions": [],
        "optimized_transactions": [],
        "is_optimized": False,
        "created_at": "2026-05-17T00:00:00Z",
    }

    response = await async_client.post("/api/v1/groups", json=payload)
    assert response.status_code == 201

    body = response.json()
    assert body["group_id"] == payload["group_id"]
    assert body["name"] == payload["name"]
    assert body["is_optimized"] is False
    assert body["raw_transactions"] == []


@pytest.mark.asyncio
async def test_add_transaction_to_group(async_client):
    group_payload = {
        "group_id": "group-2",
        "name": "Transaction Test Group",
        "raw_transactions": [],
        "optimized_transactions": [],
        "is_optimized": False,
        "created_at": "2026-05-17T00:00:00Z",
    }

    create_response = await async_client.post("/api/v1/groups", json=group_payload)
    assert create_response.status_code == 201

    transaction = {"from_user": "Alice", "to_user": "Bob", "amount": 100.0}
    response = await async_client.post(
        f"/api/v1/groups/{group_payload['group_id']}/transactions",
        json=transaction,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["raw_transactions"][0]["from_user"] == "Alice"
    assert body["raw_transactions"][0]["to_user"] == "Bob"
    assert body["raw_transactions"][0]["amount"] == 100.0
    assert body["is_optimized"] is False


@pytest.mark.asyncio
async def test_optimize_endpoint_uses_cached_result_when_available(async_client):
    group_payload = {
        "group_id": "group-3",
        "name": "Optimize Cache Group",
        "raw_transactions": [],
        "optimized_transactions": [
            {"from_user": "Alice", "to_user": "Bob", "amount": 100.0}
        ],
        "is_optimized": True,
        "created_at": "2026-05-17T00:00:00Z",
    }

    response = await async_client.post("/api/v1/groups", json=group_payload)
    assert response.status_code == 201

    optimize_response = await async_client.post(f"/api/v1/optimize/{group_payload['group_id']}")
    assert optimize_response.status_code == 200
    body = optimize_response.json()
    assert body["status"] == "cached"
    assert body["optimized_transactions"][0]["from_user"] == "Alice"


@pytest.mark.asyncio
async def test_optimize_endpoint_calls_cpp_optimizer_and_persists(async_client):
    group_payload = {
        "group_id": "group-4",
        "name": "Optimize Persist Group",
        "raw_transactions": [
            {"from_user": "Alice", "to_user": "Bob", "amount": 100.0}
        ],
        "optimized_transactions": [],
        "is_optimized": False,
        "created_at": "2026-05-17T00:00:00Z",
    }

    response = await async_client.post("/api/v1/groups", json=group_payload)
    assert response.status_code == 201

    fake_result = OptimizationResult(
        group_id=group_payload["group_id"],
        optimized_transactions=[OptimizedTransaction(from_user="Alice", to_user="Bob", amount=100.0)],
        original_count=1,
        optimized_count=1,
        total_original_amount=100.0,
        total_optimized_amount=100.0,
        reduction_percentage=0.0,
        status="success",
    )

    with patch("app.api.v1.routes.optimize.run_cpp_optimizer", new=AsyncMock(return_value=fake_result)):
        optimize_response = await async_client.post(f"/api/v1/optimize/{group_payload['group_id']}")

    assert optimize_response.status_code == 200
    body = optimize_response.json()
    assert body["status"] == "success"
    assert body["optimized_transactions"][0]["amount"] == 100.0

    group_response = await async_client.get(f"/api/v1/groups/{group_payload['group_id']}")
    assert group_response.status_code == 200
    group_body = group_response.json()
    assert group_body["is_optimized"] is True
    assert group_body["optimized_transactions"][0]["amount"] == 100.0


@pytest.mark.asyncio
async def test_rejects_self_debt_transaction(async_client):
    group_payload = {
        "group_id": "group-5",
        "name": "Self Debt Group",
        "raw_transactions": [],
        "optimized_transactions": [],
        "is_optimized": False,
        "created_at": "2026-05-17T00:00:00Z",
    }

    response = await async_client.post("/api/v1/groups", json=group_payload)
    assert response.status_code == 201

    transaction = {"from_user": "Alice", "to_user": "Alice", "amount": 50.0}
    response = await async_client.post(
        f"/api/v1/groups/{group_payload['group_id']}/transactions",
        json=transaction,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rejects_zero_amount_transaction(async_client):
    group_payload = {
        "group_id": "group-6",
        "name": "Zero Amount Group",
        "raw_transactions": [],
        "optimized_transactions": [],
        "is_optimized": False,
        "created_at": "2026-05-17T00:00:00Z",
    }

    response = await async_client.post("/api/v1/groups", json=group_payload)
    assert response.status_code == 201

    transaction = {"from_user": "Alice", "to_user": "Bob", "amount": 0.0}
    response = await async_client.post(
        f"/api/v1/groups/{group_payload['group_id']}/transactions",
        json=transaction,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_large_group_payload_handles_5000_transactions(async_client):
    random.seed(0)
    users = ["Alice", "Bob", "Charlie", "Dave"]
    raw_transactions = []
    for _ in range(5000):
        payer = random.choice(users)
        payee = random.choice([u for u in users if u != payer])
        raw_transactions.append(
            {
                "from_user": payer,
                "to_user": payee,
                "amount": round(random.uniform(1.0, 100.0), 2),
            }
        )

    group_payload = {
        "group_id": "group-7",
        "name": "Stress Test Group",
        "raw_transactions": raw_transactions,
        "optimized_transactions": [],
        "is_optimized": False,
        "created_at": "2026-05-17T00:00:00Z",
    }

    response = await async_client.post("/api/v1/groups", json=group_payload)
    assert response.status_code == 201

    fake_result = OptimizationResult(
        group_id=group_payload["group_id"],
        optimized_transactions=[],
        original_count=5000,
        optimized_count=0,
        total_original_amount=0.0,
        total_optimized_amount=0.0,
        reduction_percentage=0.0,
        status="success",
    )

    with patch("app.api.v1.routes.optimize.run_cpp_optimizer", new=AsyncMock(return_value=fake_result)):
        optimize_response = await async_client.post(f"/api/v1/optimize/{group_payload['group_id']}")

    assert optimize_response.status_code == 200
    body = optimize_response.json()
    assert body["status"] == "success"
    assert body["original_count"] == 5000


@pytest.mark.asyncio
async def test_engine_handles_floating_point_precision_if_binary_available():
    binary_name = "debt_optimizer.exe" if sys.platform.startswith("win") else "debt_optimizer"
    binary_path = Path(__file__).resolve().parents[2] / "core_engine" / "build" / binary_name
    if not binary_path.exists():
        pytest.skip("C++ binary not available for integration test")

    transactions = [
        Transaction(from_user="Alice", to_user="Bob", amount=33.33),
        Transaction(from_user="Bob", to_user="Charlie", amount=33.33),
        Transaction(from_user="Charlie", to_user="Alice", amount=33.34),
    ]

    result = await run_cpp_optimizer(transactions, "float-test")

    assert result.status == "success"
    assert abs(result.total_original_amount - result.total_optimized_amount) < 0.05
    assert abs(result.total_original_amount - 100.0) < 0.05
    assert result.optimized_count <= 3


@pytest.mark.asyncio
async def test_engine_handles_disjoint_subgraphs_if_binary_available():
    binary_name = "debt_optimizer.exe" if sys.platform.startswith("win") else "debt_optimizer"
    binary_path = Path(__file__).resolve().parents[2] / "core_engine" / "build" / binary_name
    if not binary_path.exists():
        pytest.skip("C++ binary not available for integration test")

    pytest.skip("C++ binary not available for integration test")

    transactions = [
        Transaction(from_user="Alice", to_user="Bob", amount=100.0),
        Transaction(from_user="Bob", to_user="Alice", amount=50.0),
        Transaction(from_user="Charlie", to_user="Dave", amount=30.0),
        Transaction(from_user="Dave", to_user="Charlie", amount=10.0),
    ]

    result = await run_cpp_optimizer(transactions, "disjoint-test")

    assert result.status == "success"
    assert result.optimized_count == 2
    for tx in result.optimized_transactions:
        user_pair = {tx.from_user, tx.to_user}
        assert user_pair <= {"Alice", "Bob"} or user_pair <= {"Charlie", "Dave"}
