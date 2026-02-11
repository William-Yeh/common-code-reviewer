# Test sample: FastAPI + SQLAlchemy order service with intentional issues
# This file contains ~12 deliberate problems for the code review skill to catch.

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
import requests
import logging

router = APIRouter()

# [ISSUE: Global mutable state]
order_cache = {}

# [ISSUE: Mutable default argument]
def build_filters(status="active", tags=[]):
    tags.append(status)
    return {"status": status, "tags": tags}


# [ISSUE: Missing type hints on public function]
def get_db():
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# [ISSUE: God function — does validation, querying, transformation, caching, notification]
@router.post("/orders")
async def create_order(body: dict, db: Session = Depends(get_db)):
    # [ISSUE: No Pydantic model — raw dict input with no validation]

    # [ISSUE: SQL injection via string interpolation with text()]
    result = db.execute(
        text(f"INSERT INTO orders (customer_id, product, quantity) "
             f"VALUES ('{body['customer_id']}', '{body['product']}', {body['quantity']}) "
             f"RETURNING id")
    )
    order_id = result.scalar()

    # [ISSUE: Bare except that swallows all errors]
    try:
        notify_warehouse(body)
    except:
        pass

    # [ISSUE: Magic number]
    if body.get("quantity", 0) > 500:
        logging.warning("Large order placed")

    order_cache[order_id] = body
    return {"id": order_id, "status": "created"}


@router.get("/orders")
async def list_orders(db: Session = Depends(get_db)):
    # [ISSUE: Unbounded query — no limit, no pagination]
    orders = db.execute(text("SELECT * FROM orders")).fetchall()

    # [ISSUE: N+1 query — fetching items per order in a loop]
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
    # [ISSUE: SQL injection via f-string in text()]
    orders = db.execute(
        text(f"SELECT * FROM orders WHERE customer_id = '{customer_id}' AND status = '{status}'")
    ).fetchall()
    return [dict(o) for o in orders]


# [ISSUE: Sync blocking I/O in a module used by async routes]
def notify_warehouse(order):
    # [ISSUE: No timeout on HTTP request]
    response = requests.post(
        "http://warehouse-service/notify",
        json=order,
    )
    # [ISSUE: No error check on response status]
    print(f"Warehouse notified: {response.status_code}")
