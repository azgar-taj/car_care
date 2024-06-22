from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str
    isAdmin: bool = False

class Service(BaseModel):
    service_name: str
    service_price: int
    service_description: str
    service_duration: int

class BaseResponse(BaseModel):
    success: bool
    message: str

class UserResponse(BaseResponse):
    userId: str
    status: str