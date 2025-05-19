from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.user import User, UserCreate, UserUpdate
from datetime import datetime

router = APIRouter()

# Mock database
users_db = {
    1: {
        "id": 1,
        "email": "john.doe@example.com",
        "name": "John Doe",
        "role": "admin",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
}

@router.get("/", response_model=List[User])
async def get_users():
    return list(users_db.values())

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return users_db[user_id]

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    user_id = max(users_db.keys()) + 1 if users_db else 1
    user_dict = user.model_dump()
    user_dict["id"] = user_id
    user_dict["created_at"] = datetime.now()
    user_dict["updated_at"] = datetime.now()
    users_db[user_id] = user_dict
    return user_dict

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate):
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user_dict = user.model_dump(exclude_unset=True)
    users_db[user_id].update(user_dict)
    users_db[user_id]["updated_at"] = datetime.now()
    return users_db[user_id]

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    del users_db[user_id] 