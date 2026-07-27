from enum import Enum as PyEnum
from typing import List, TYPE_CHECKING
from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.session import Session


class UserRole(str, PyEnum):
    ADMIN = "admin"
    TEACHER = "teacher"
    PARENT = "parent"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="userrole"), nullable=False)

    # Relationships
    # A teacher can lead multiple sessions
    teaches_sessions: Mapped[List["Session"]] = relationship(
        "Session",
        foreign_keys="[Session.teacher_id]",
        back_populates="teacher",
        cascade="all, delete-orphan",
    )
    # A student/parent can attend multiple sessions
    student_sessions: Mapped[List["Session"]] = relationship(
        "Session",
        foreign_keys="[Session.student_id]",
        back_populates="student",
        cascade="all, delete-orphan",
    )
