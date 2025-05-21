from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Table, Column, String, DateTime, MetaData, create_engine
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.core.database import get_db, engine
from app.core.models import Product, User
from app.core.schemas import Item as ItemSchema
from app.core.schemas import ItemCreate, BatchItemCreate
from app.api.deps import get_current_user

router = APIRouter()

def get_items_table(product_id: int) -> Table:
    """Get or create items table for a specific product."""
    table_name = f"items_{product_id}"
    metadata = MetaData()
    
    # Define the table structure
    items_table = Table(
        table_name,
        metadata,
        Column("id", String, primary_key=True),
        Column("key", String, nullable=False),
        Column("box_key", String, nullable=False),
        Column("created_at", DateTime, default=datetime.utcnow, nullable=False)
    )
    
    # Create the table if it doesn't exist
    metadata.create_all(engine)
    return items_table

@router.get("/{product_id}", response_model=List[ItemSchema])
def read_items(
    product_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve items for a specific product.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    items_table = get_items_table(product_id)
    items = db.execute(items_table.select().offset(skip).limit(limit)).fetchall()
    return [dict(item) for item in items]

@router.post("/{product_id}", response_model=ItemSchema)
def create_item(
    *,
    product_id: int,
    db: Session = Depends(get_db),
    item_in: ItemCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new item for a specific product.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    items_table = get_items_table(product_id)
    item_id = str(uuid.uuid4())
    
    item = {
        "id": item_id,
        "key": item_in.key,
        "box_key": item_in.box_key,
        "created_at": datetime.utcnow()
    }
    
    db.execute(items_table.insert().values(**item))
    db.commit()
    return item

@router.post("/{product_id}/batch", response_model=List[ItemSchema])
def create_batch_items(
    *,
    product_id: int,
    db: Session = Depends(get_db),
    batch_in: BatchItemCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create multiple items for a specific product.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    items_table = get_items_table(product_id)
    items = []
    
    for _ in range(batch_in.quantity):
        item_id = str(uuid.uuid4())
        item = {
            "id": item_id,
            "key": str(uuid.uuid4()),
            "box_key": batch_in.box_key,
            "created_at": datetime.utcnow()
        }
        items.append(item)
    
    db.execute(items_table.insert(), items)
    db.commit()
    return items

@router.delete("/{product_id}/{item_id}", response_model=ItemSchema)
def delete_item(
    *,
    product_id: int,
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Delete an item.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    items_table = get_items_table(product_id)
    item = db.execute(
        items_table.select().where(items_table.c.id == item_id)
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    db.execute(items_table.delete().where(items_table.c.id == item_id))
    db.commit()
    return dict(item) 