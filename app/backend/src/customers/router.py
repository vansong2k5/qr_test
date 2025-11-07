from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..crud.customer import customer as customer_crud
from ..deps import get_current_user, get_db
from ..schemas.customer import CustomerCreate, CustomerOut, CustomerUpdate

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/", response_model=list[CustomerOut])
async def list_customers(
    q: str = Query(""),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return customer_crud.search(db, query=q, skip=skip, limit=limit)


@router.post("/", response_model=CustomerOut, status_code=201)
async def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    return customer_crud.create(db, obj_in=payload)


@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = customer_crud.get(db, id=customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerOut)
async def update_customer(customer_id: int, payload: CustomerUpdate, db: Session = Depends(get_db)):
    customer = customer_crud.get(db, id=customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer_crud.update(db, db_obj=customer, obj_in=payload)


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = customer_crud.get(db, id=customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer_crud.remove(db, id=customer_id)
    return None
