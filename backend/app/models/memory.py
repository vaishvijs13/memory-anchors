from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, IDMixin, TimestampMixin

if TYPE_CHECKING:
    from .object import RegisteredObject
    from .user import User


class Memory(Base, IDMixin, TimestampMixin):
    __tablename__ = "memories"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    narrative_text: Mapped[str] = mapped_column(Text, nullable=False)
    context_hint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sensory_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    time_period: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    significance: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    audio_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="memories")
    objects: Mapped[List["MemoryObject"]] = relationship(
        back_populates="memory", cascade="all, delete-orphan"
    )
    people: Mapped[List["MemoryPerson"]] = relationship(
        back_populates="memory", cascade="all, delete-orphan"
    )
    emotions: Mapped[List["MemoryEmotion"]] = relationship(
        back_populates="memory", cascade="all, delete-orphan"
    )


class MemoryObject(Base, IDMixin):
    __tablename__ = "memory_objects"

    memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("memories.id"), nullable=False
    )
    object_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("registered_objects.id"), nullable=False
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    memory: Mapped["Memory"] = relationship(back_populates="objects")
    registered_object: Mapped["RegisteredObject"] = relationship()


class MemoryPerson(Base, IDMixin):
    __tablename__ = "memory_people"

    memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("memories.id"), nullable=False
    )
    person_name: Mapped[str] = mapped_column(String(255), nullable=False)
    relationship_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    memory: Mapped["Memory"] = relationship(back_populates="people")


class MemoryEmotion(Base, IDMixin):
    __tablename__ = "memory_emotions"

    memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("memories.id"), nullable=False
    )
    emotion: Mapped[str] = mapped_column(String(100), nullable=False)
    intensity: Mapped[float] = mapped_column(Float, default=0.5)

    memory: Mapped["Memory"] = relationship(back_populates="emotions")
