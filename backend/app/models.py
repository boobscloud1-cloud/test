from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    spins = Column(Integer, default=0)
    points = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("spins >= 0", name="ck_users_spins_nonneg"),
        CheckConstraint("points >= 0", name="ck_users_points_nonneg"),
    )
    
    referrals = relationship("Referral", back_populates="referrer", foreign_keys="Referral.referrer_id")
    rewards = relationship("Reward", back_populates="user")
    tasks_completed = relationship("TaskCompletion", back_populates="user")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    cpa_network_id = Column(String)
    reward_spins = Column(Integer, default=1)
    cpa_payout = Column(Float, default=0.0) # Estimated revenue in USD
    is_active = Column(Boolean, default=True)

class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"))
    referred_id = Column(Integer, ForeignKey("users.id"), unique=True)
    is_qualified = Column(Boolean, default=False) # True if referred user completed a task
    created_at = Column(DateTime, default=datetime.utcnow)

    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals")
    referred = relationship("User", foreign_keys=[referred_id])

class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    prize_type = Column(String, nullable=False) # "points", "item", etc.
    prize_value = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="rewards")

class TaskCompletion(Base):
    __tablename__ = "task_completions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    transaction_id = Column(String, unique=True, index=True) # From CPA postback
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="tasks_completed")
