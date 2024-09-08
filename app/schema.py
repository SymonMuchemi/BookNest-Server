from pydantic import BaseModel, Field


class BookSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    author: str = Field(..., min_length=3, max_length=255)
    image_url: str = Field(..., min_length=10)
    quantity: int = Field(gt=0)
    rental_fee: int = Field(gt=10)


class MemberSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    debt: int = Field(..., ge=0, lt=500)
