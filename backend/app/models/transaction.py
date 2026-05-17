"""
Pydantic models for Debt Settlement Engine API
"""

from pydantic import BaseModel, Field, model_validator
from typing import List


class Transaction(BaseModel):
    """Individual transaction between two parties"""
    from_user: str = Field(..., description="User who owes money")
    to_user: str = Field(..., description="User who is owed money")
    amount: float = Field(..., gt=0, description="Transaction amount")

    @model_validator(mode="after")
    def validate_participants(self):
        if self.from_user == self.to_user:
            raise ValueError("from_user and to_user must be different")
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "from_user": "alice",
                "to_user": "bob",
                "amount": 100.0
            }
        }


class OptimizationRequest(BaseModel):
    """Request to optimize cash flow for a group"""
    transactions: List[Transaction] = Field(..., description="List of transactions to optimize")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transactions": [
                    {"from_user": "A", "to_user": "B", "amount": 100.0},
                    {"from_user": "B", "to_user": "C", "amount": 100.0},
                    {"from_user": "C", "to_user": "A", "amount": 100.0}
                ]
            }
        }


class OptimizedTransaction(BaseModel):
    """Optimized transaction result"""
    from_user: str = Field(..., description="User who pays")
    to_user: str = Field(..., description="User who receives")
    amount: float = Field(..., description="Payment amount")


class OptimizationResult(BaseModel):
    """Result of cash flow optimization"""
    group_id: str = Field(..., description="Group identifier for the optimization request")
    optimized_transactions: List[OptimizedTransaction] = Field(default_factory=list, description="Optimized transaction list")
    original_count: int = Field(..., description="Original number of transactions")
    optimized_count: int = Field(..., description="Optimized number of transactions")
    total_original_amount: float = Field(..., description="Total original amount")
    total_optimized_amount: float = Field(..., description="Total optimized amount")
    reduction_percentage: float = Field(..., description="Percentage reduction in transactions")
    status: str = Field(..., description="Status of optimization")
    
    class Config:
        json_schema_extra = {
            "example": {
                "group_id": "group_123",
                "optimized_transactions": [],
                "original_count": 3,
                "optimized_count": 0,
                "total_original_amount": 300.0,
                "total_optimized_amount": 0.0,
                "reduction_percentage": 100.0,
                "status": "success"
            }
        }
