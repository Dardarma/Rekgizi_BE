from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    nama: str
    email: str
    role: str

    model_config = {
        "from_attributes": True
    }

class LoginSchema(BaseModel):
    email: str
    password: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
    
