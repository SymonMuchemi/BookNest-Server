from datetime import datetime
from .utils import TransactionType
from pydantic import BaseModel, Field


class BookSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    author: str = Field(..., min_length=3, max_length=255)
    image_url: str = Field(..., min_length=10)
    quantity: int = Field(..., gt=0)
    rental_fee: int = Field(gt=10, default=10)


class MemberSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    debt: int = Field(..., ge=0, lt=500)


class TransactionSchema(BaseModel):
    book_id: int = Field(..., ge=1)
    member_id: int = Field(..., gt=0)
    type: TransactionType = Field(...)
    amount: int = Field(default=0)
    date: datetime = Field(default_factory=datetime.now)
