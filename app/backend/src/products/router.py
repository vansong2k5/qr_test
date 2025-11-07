from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..crud.product import product as product_crud
from ..deps import get_current_user, get_db
from ..schemas.product import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/", response_model=list[ProductOut])
async def list_products(status: str | None = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return product_crud.filter_by_status(db, status=status, skip=skip, limit=limit)


@router.post("/", response_model=ProductOut, status_code=201)
async def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    return product_crud.create(db, obj_in=payload)


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = product_crud.get(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = product_crud.get(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_crud.update(db, db_obj=product, obj_in=payload)


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = product_crud.get(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product_crud.remove(db, id=product_id)
    return None


@router.post("/import", status_code=204)
async def import_products(file: UploadFile = File(...)):
    # placeholder for CSV import
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    return None
