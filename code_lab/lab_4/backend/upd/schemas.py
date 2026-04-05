from pydantic import BaseModel, Field, validator
from typing import List, Optional

class OrderItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=1, le=10000)

class OrderCreate(BaseModel):
    order_number: str = Field(..., min_length=1, max_length=50)
    items: List[OrderItem]   # теперь список объектов с name и quantity
    amount: float = Field(..., gt=0)
    delivery_address: str = Field(..., min_length=5)
    status: Optional[str] = Field('новый', max_length=50)

    @validator('order_number')
    def order_number_alphanumeric(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Order number must be alphanumeric (dash/underscore allowed)')
        return v

class OrderUpdate(BaseModel):
    order_number: Optional[str] = None
    items: Optional[List[OrderItem]] = None
    amount: Optional[float] = Field(None, gt=0)
    delivery_address: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)

class OrderResponse(OrderCreate):
    id: int
    class Config:
        orm_mode = True
