from pydantic import BaseModel, conint, confloat, constr
from typing import Optional, List
from datetime import datetime

# User
class UserBase(BaseModel):
    telegram_id: conint(ge=1)
    username: Optional[str] = None

class UserCreate(UserBase):
    referrer_id: Optional[int] = None

class UserResponse(UserBase):
    id: int
    spins: int
    points: float
    created_at: datetime

    class Config:
        from_attributes = True

# Task
class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    cpa_network_id: str
    reward_spins: int
    is_active: bool = True

class TaskResponse(TaskBase):
    id: int

    class Config:
        from_attributes = True

# Reward
class RewardBase(BaseModel):
    prize_type: str
    prize_value: str

class RewardResponse(RewardBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Spin Result
class SpinResult(BaseModel):
    prize_type: str
    prize_value: str
    remaining_spins: int
    angle: int # For frontend animation

# Purchase Result
class PurchaseResult(BaseModel):
    spins_purchased: int
    remaining_spins: int
    remaining_points: float

# Postback
class CPAPostback(BaseModel):
    click_id: str # transaction_id
    sub_id: int # user_id / telegram_id
    payout: float
    token: str # Security token

# Auth
class AuthVerifyRequest(BaseModel):
    init_data: str

class AuthVerifyResponse(BaseModel):
    user: "UserResponse"

# Admin
class AdminStats(BaseModel):
    total_users: int
    total_tasks_completed: int
    total_spins_consumed: int
    estimated_revenue: float

class AdminAddSpins(BaseModel):
    amount: int

class AdminBroadcast(BaseModel):
    message: str
