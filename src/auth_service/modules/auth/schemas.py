from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    model_config = {'from_attributes': True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserLoginReturn(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

    model_config = {'from_attributes': True}


class UserRefreshToken(BaseModel):
    access_token: str
    token_type: str = 'bearer'

    model_config = {'from_attributes': True}


class RefreshRequest(BaseModel):
    refresh_token: str


class VerifyEmailRabbitMQ(BaseModel):
    type: str = 'verify_email'
    email: EmailStr
    name: str
    code: str


class ResetPasswordRabbitMQ(BaseModel):
    type: str = 'reset_password'
    email: EmailStr
    name: str
    token: str


class ValidateAccount(BaseModel):
    email: EmailStr
    code: str


class UserCreatedEvent(BaseModel):
    user_id: int
    email: EmailStr
    username: str
