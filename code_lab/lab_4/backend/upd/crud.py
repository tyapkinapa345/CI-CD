from sqlalchemy.orm import Session
from models import Order
from schemas import OrderCreate, OrderUpdate

def get_order(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()

def get_order_by_number(db: Session, order_number: str):
    return db.query(Order).filter(Order.order_number == order_number).first()

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Order).offset(skip).limit(limit).all()

def create_order(db: Session, order: OrderCreate):
    # Преобразуем список OrderItem в список словарей
    items_dicts = [item.dict() for item in order.items]
    db_order = Order(
        order_number=order.order_number,
        items=items_dicts,
        amount=order.amount,
        delivery_address=order.delivery_address,
        status=order.status
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def update_order(db: Session, order_id: int, order_update: OrderUpdate):
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    update_data = order_update.dict(exclude_unset=True)
    if 'items' in update_data and update_data['items'] is not None:
        update_data['items'] = [item.dict() for item in update_data['items']]
    for key, value in update_data.items():
        setattr(db_order, key, value)
    db.commit()
    db.refresh(db_order)
    return db_order
def delete_order(db: Session, order_id: int):
    db_order = get_order(db, order_id)
    if db_order:
        db.delete(db_order)
        db.commit()
        return True
    return False
