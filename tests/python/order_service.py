from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
import requests
import logging

router = APIRouter()

order_cache = {}

def build_filters(status="active", tags=[]):
    tags.append(status)
    return {"status": status, "tags": tags}


def get_db():
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/orders")
async def create_order(body: dict, db: Session = Depends(get_db)):

    result = db.execute(
        text(f"INSERT INTO orders (customer_id, product, quantity) "
             f"VALUES ('{body['customer_id']}', '{body['product']}', {body['quantity']}) "
             f"RETURNING id")
    )
    order_id = result.scalar()

    try:
        notify_warehouse(body)
    except:
        pass

    if body.get("quantity", 0) > 500:
        logging.warning("Large order placed")

    order_cache[order_id] = body
    return {"id": order_id, "status": "created"}


@router.get("/orders")
async def list_orders(db: Session = Depends(get_db)):
    orders = db.execute(text("SELECT * FROM orders")).fetchall()

    results = []
    for order in orders:
        items = db.execute(
            text(f"SELECT * FROM order_items WHERE order_id = {order.id}")
        ).fetchall()
        results.append({
            "id": order.id,
            "customer_id": order.customer_id,
            "items": [dict(i) for i in items],
        })

    return results


@router.get("/orders/search")
async def search_orders(customer_id: str, status: str, db: Session = Depends(get_db)):
    orders = db.execute(
        text(f"SELECT * FROM orders WHERE customer_id = '{customer_id}' AND status = '{status}'")
    ).fetchall()
    return [dict(o) for o in orders]


def notify_warehouse(order):
    response = requests.post(
        "http://warehouse-service/notify",
        json=order,
    )
    print(f"Warehouse notified: {response.status_code}")
