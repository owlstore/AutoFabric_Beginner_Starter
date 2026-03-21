from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.db import Base


class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True)
    raw_input = Column(Text, nullable=False)
    goal_type = Column(String(50), nullable=False, default="environment_build")
    parsed_goal = Column(JSONB, nullable=False, default=dict)
    risk_level = Column(String(20), nullable=False, default="low")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class Outcome(Base):
    __tablename__ = "outcomes"
    id = Column(Integer, primary_key=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="draft")
    current_result = Column(JSONB, nullable=False, default=dict)
    next_action = Column(Text)
    risk_boundary = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
