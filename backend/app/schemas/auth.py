from uuid import UUID
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    agence_id: UUID | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    agence_id: UUID | None


class UserRead(BaseModel):
    id: UUID
    email: str
    role: str
    agence_id: UUID | None

    model_config = {"from_attributes": True}
