import enum
from datetime import datetime
from typing import Any, Mapping, Optional, Self, cast
from uuid import UUID, uuid4

from pydantic import ValidationError, model_validator
from sqlalchemy import CheckConstraint, Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Integer
from sqlalchemy.schema import Index
from sqlalchemy.sql import func
from sqlmodel import JSON, Column, Enum, Field, Relationship, SQLModel


class Base(SQLModel):
    id: int = Field(primary_key=True, nullable=False)  # All of the osu objects already have a unique id.

    def __repr__(self) -> str:
        return self.model_dump_json(indent=4, exclude_unset=False, exclude_none=False, exclude_defaults=False)


class MetadataMixin(SQLModel):
    """
    Mixin class for created_at, and updated_at fields
    """

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
class User(Base, MetadataMixin, table=True):
    scores: list["Score"] = Relationship(back_populates="user", cascade_delete=True)


# Score models
class Score(Base, MetadataMixin, table=True):
    user: "User" = Relationship(back_populates="scores")

    user_id: int = Field(
        description="The user (id) this score belongs to",
        foreign_key="user.id",
        nullable=False,
    )


# Beatmap models
class Modes(enum.Enum):
    osu = 'osu'
    taiko = 'taiko'
    mania = 'mania'
    fruits = 'fruits'


class Beatmap(Base, MetadataMixin, table=True):
    mode: Modes = Field(sa_column=Column(SAEnum(Modes, name="mode_enum"), nullable=False))
    beatmapset: "Beatmapset" = Relationship(back_populates="beatmaps")

    beatmapset_id: int = Field(
        description="The beatmapset (id) this beatmap belongs to",
        foreign_key="beatmapset.id",
        nullable=False,
    )


# Beatmapset models
class Beatmapset(Base, MetadataMixin, table=True):
    beatmaps: list["Beatmap"] = Relationship(back_populates="beatmapset", cascade_delete=True)
