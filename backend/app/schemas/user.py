from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: str = "member"


class UserResponse(UserCreate):
    id: int

    class Config:
        from_attributes = True