from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr
import json
import uuid


class Conversation(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str
    title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    meta_data: Optional[str] = Field(sa_column=sa.Column(sa.Text), default="{}")  # JSON string


class Message(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id")
    role: str  # "user" or "assistant"
    content: str = Field(sa_column=sa.Column(sa.Text, nullable=False))
    created_at: datetime = Field(default_factory=datetime.now)
    meta_data: Optional[str] = Field(sa_column=sa.Column(sa.Text), default="{}")  # JSON string để lưu thông tin về tools, actions, v.v. 