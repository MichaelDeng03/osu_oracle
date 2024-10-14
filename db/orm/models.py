from datetime import datetime
from enum import Enum
from typing import Any, Mapping, Optional, Self, cast
from uuid import UUID, uuid4

from pydantic import ValidationError, model_validator
from sqlalchemy import CheckConstraint, DateTime
from sqlalchemy.schema import Index
from sqlalchemy.sql import func
from sqlmodel import Field, Relationship, SQLModel


class Base(SQLModel):
    def __repr__(self) -> str:
        return self.model_dump_json(indent=4, exclude_unset=True, exclude_none=True)


class MetadataMixin(SQLModel):
    """
    Mixin class for id, created_at, and updated_at fields
    """

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    created_at: datetime | None = Field(
        default=None,
        sa_type=cast(Any, DateTime(timezone=True)),
        sa_column_kwargs=cast(Mapping[str, Any], {"server_default": func.now()}),
        nullable=False,
    )
    modified_at: datetime | None = Field(
        default=None,
        sa_type=cast(Any, DateTime(timezone=True)),
        sa_column_kwargs=cast(Mapping[str, Any], {"onupdate": func.now(), "server_default": func.now()}),
    )


# User models


class UserBase(Base):
    pass


class UserUpdate(UserBase):
    pass


class User(UserBase, MetadataMixin, table=True):
    pass


# Beatmap models
class ModeEnum(Enum):
    STANDARD = 1
    TAIKO = 2
    CATCH = 3
    MANIA = 4


class Beatmapbase(Base):
    mode: ModeEnum


# Beatmapset models


# Score models
