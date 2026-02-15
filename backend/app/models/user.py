from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, IDMixin, TimestampMixin

if TYPE_CHECKING:
    from .memory import Memory
    from .object import RegisteredObject
    from .session import MoodEntry


class UserRole(str, enum.Enum):
    patient = "patient"
    caregiver = "caregiver"
    admin = "admin"


class User(Base, IDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    diagnosis_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    memories: Mapped[List["Memory"]] = relationship(back_populates="user")
    registered_objects: Mapped[List["RegisteredObject"]] = relationship(
        back_populates="user"
    )
    mood_entries: Mapped[List["MoodEntry"]] = relationship(
        back_populates="user", foreign_keys="MoodEntry.user_id"
    )


class CaregiverRelationship(Base, IDMixin):
    __tablename__ = "caregiver_relationships"
    __table_args__ = (
        UniqueConstraint("caregiver_id", "patient_id"),
    )

    caregiver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    relationship: Mapped[str] = mapped_column(String(100), nullable=False)
