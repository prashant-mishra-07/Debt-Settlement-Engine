"""
API routes for debt optimization endpoints
"""

from fastapi import APIRouter, HTTPException
from app.models.transaction import OptimizedTransaction, Transaction, OptimizationResult
from app.core.engine_bridge import run_cpp_optimizer
from app.services.group_service import get_group, update_group_optimized_status
import subprocess

router = APIRouter()


@router.post("/optimize/{group_id}", response_model=OptimizationResult)
async def optimize_cash_flow(group_id: str):
    """
    Optimize cash flow for a given group of transactions by group ID.
    """
    group_data = await get_group(group_id)
    if not group_data:
        raise HTTPException(status_code=404, detail=f"Group '{group_id}' not found.")

    if group_data.get("is_optimized"):
        raw_transactions = [Transaction(**t) for t in group_data.get("raw_transactions", [])]
        optimized_transactions = [OptimizedTransaction(**t) for t in group_data.get("optimized_transactions", [])]
        original_count = len(raw_transactions)
        optimized_count = len(optimized_transactions)
        total_original_amount = sum(t.amount for t in raw_transactions)
        total_optimized_amount = sum(t.amount for t in optimized_transactions)
        reduction_percentage = (
            ((original_count - optimized_count) * 100.0 / original_count)
            if original_count > 0 else 0.0
        )

        return OptimizationResult(
            group_id=group_id,
            optimized_transactions=optimized_transactions,
            original_count=original_count,
            optimized_count=optimized_count,
            total_original_amount=total_original_amount,
            total_optimized_amount=total_optimized_amount,
            reduction_percentage=reduction_percentage,
            status="cached",
        )

    raw_transactions = [Transaction(**t) for t in group_data.get("raw_transactions", [])]
    if not raw_transactions:
        raise HTTPException(status_code=400, detail="No raw transactions available for optimization.")

    try:
        result = await run_cpp_optimizer(raw_transactions, group_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"C++ optimizer binary not found: {str(e)}")
    except subprocess.TimeoutExpired as e:
        raise HTTPException(status_code=504, detail=f"C++ optimizer timed out: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

    optimized_payload = [t.dict() for t in result.optimized_transactions]
    saved = await update_group_optimized_status(group_id, optimized_payload)
    if not saved:
        raise HTTPException(status_code=500, detail="Failed to persist optimized transactions.")

    return result


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "debt-settlement-engine-api"}
