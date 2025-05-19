from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="User Info API")

class User(BaseModel):
    id: int
    name: str
    email: str
    role: str

@app.get("/", response_model=User)
async def get_user_info():
    # Mock user data
    return {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "role": "admin"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 