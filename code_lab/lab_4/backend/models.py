from sqlalchemy import Column, Integer, String, Float, JSON
from database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True, nullable=False)
    items = Column(JSON, nullable=False)          # список товаров, например ["товар1", "товар2"]
    amount = Column(Float, nullable=False)
    delivery_address = Column(String, nullable=False)
    status = Column(String, default='новый', nullable=False)
