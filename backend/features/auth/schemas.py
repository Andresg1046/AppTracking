from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    reset_code: str
    new_password: str

class LogoutResponse(BaseModel):
    message: str

class SessionInfo(BaseModel):
    id: int
    device_info: Optional[str]
    ip_address: Optional[str]
    created_at: datetime
    last_used: datetime
    is_active: bool

class SessionsResponse(BaseModel):
    sessions: list[SessionInfo]
    max_sessions: int  
