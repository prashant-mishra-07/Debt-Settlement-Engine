"""
Subprocess orchestrator for C++ debt optimizer engine
Handles file-based IPC with the C++ binary
"""

import asyncio
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List

from app.models.transaction import Transaction, OptimizationResult, OptimizedTransaction


def _sanitize_filename(value: str) -> str:
    """Create a filesystem-safe string for temporary file names."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in value).strip("_") or "debt_group"


async def run_cpp_optimizer(transactions: List[Transaction], group_id: str) -> OptimizationResult:
    """
    Run the C++ debt optimizer using file-based IPC
    
    Args:
        transactions: List of Transaction objects to optimize
        group_id: Unique identifier for the optimization request
        
    Returns:
        OptimizationResult with optimized transactions and metadata
    """
    # Resolve path to C++ binary cross-platform
    project_root = Path(__file__).resolve().parent.parent.parent
    binary_name = "debt_optimizer.exe" if sys.platform.startswith("win") else "debt_optimizer"
    cpp_binary = project_root / "core_engine" / "build" / binary_name

    if not cpp_binary.exists():
        raise FileNotFoundError(f"C++ binary not found at {cpp_binary}")

    safe_group_id = _sanitize_filename(group_id)

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        input_file = temp_dir / f"temp_input_{safe_group_id}.json"
        output_file = temp_dir / "output.json"

        try:
            # Step A: Serialize transactions to input JSON file
            input_data = {
                "transactions": [
                    {
                        "from_user": t.from_user,
                        "to_user": t.to_user,
                        "amount": t.amount,
                    }
                    for t in transactions
                ]
            }

            with open(input_file, "w", encoding="utf-8") as f:
                json.dump(input_data, f, indent=2)

            # Step B: Execute C++ binary
            process = await asyncio.create_subprocess_exec(
                str(cpp_binary),
                str(input_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(temp_dir),
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10.0)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise subprocess.TimeoutExpired(str(cpp_binary), 10.0)

            if process.returncode != 0:
                error_msg = stderr.decode("utf-8", errors="replace") if stderr else "Unknown error"
                raise Exception(
                    f"C++ optimizer failed with return code {process.returncode}: {error_msg}"
                )

            if not output_file.exists():
                raise FileNotFoundError(f"Output file not found at {output_file}")

            with open(output_file, "r", encoding="utf-8") as f:
                output_data = json.load(f)

            optimized_transactions = [
                OptimizedTransaction(
                    from_user=t_data["from_user"],
                    to_user=t_data["to_user"],
                    amount=t_data["amount"],
                )
                for t_data in output_data.get("optimized_transactions", [])
            ]

            result = OptimizationResult(
                group_id=group_id,
                optimized_transactions=optimized_transactions,
                original_count=output_data.get("original_count", len(transactions)),
                optimized_count=output_data.get("optimized_count", len(optimized_transactions)),
                total_original_amount=output_data.get("total_original_amount", 0.0),
                total_optimized_amount=output_data.get("total_optimized_amount", 0.0),
                reduction_percentage=output_data.get("reduction_percentage", 0.0),
                status=output_data.get("status", "success"),
            )

            return result
        finally:
            if input_file.exists():
                try:
                    input_file.unlink()
                except Exception:
                    pass
            if output_file.exists():
                try:
                    output_file.unlink()
                except Exception:
                    pass


# Synchronous wrapper for compatibility
def run_cpp_optimizer_sync(transactions: List[Transaction], group_id: str) -> OptimizationResult:
    """
    Synchronous wrapper for run_cpp_optimizer
    """
    return asyncio.run(run_cpp_optimizer(transactions, group_id))
