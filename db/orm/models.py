import enum
from datetime import datetime
from typing import Any, Mapping, cast

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.sql import func
from sqlmodel import Column, Field, Relationship, SQLModel


# Enums
class Modes(enum.Enum):
    osu = 'osu'
    taiko = 'taiko'
    mania = 'mania'
    fruits = 'fruits'


class Mods(enum.IntFlag):
    NoMod = 0
    NoFail = 1
    Easy = 2
    TouchDevice = 4
    Hidden = 8
    HardRock = 16
    SuddenDeath = 32
    DoubleTime = 64
    Relax = 128
    HalfTime = 256
    Nightcore = 512  # NC only gives 576 (DoubleTime + Nightcore)
    Flashlight = 1024
    Autoplay = 2048
    SpunOut = 4096
    Relax2 = 8192  # Autopilot
    Perfect = 16384  # PF only gives 16416 (SuddenDeath + Perfect)
    Key4 = 32768
    Key5 = 65536
    Key6 = 131072
    Key7 = 262144
    Key8 = 524288
    FadeIn = 1048576
    Random = 2097152
    Cinema = 4194304
    Target = 8388608
    Key9 = 16777216
    KeyCoop = 33554432
    Key1 = 67108864
    Key3 = 134217728
    Key2 = 268435456
    ScoreV2 = 536870912
    Mirror = 1073741824

    # Compound Mods
    KeyMod = Key1 | Key2 | Key3 | Key4 | Key5 | Key6 | Key7 | Key8 | Key9 | KeyCoop
    FreeModAllowed = (
        NoFail | Easy | Hidden | HardRock | SuddenDeath | Flashlight | FadeIn | Relax | Relax2 | SpunOut | KeyMod
    )
    ScoreIncreaseMods = Hidden | HardRock | DoubleTime | Flashlight | FadeIn


class Base(SQLModel):
    def __repr__(self) -> str:
        return self.model_dump_json(indent=4, exclude_unset=False, exclude_none=False, exclude_defaults=False)


class MetadataMixin(SQLModel):
    """
    Mixin class for created_at, and updated_at fields
    """

    id: int = Field(primary_key=True, nullable=False)  # All of the osu objects already have a unique id.
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
    mods: Mods = Field(sa_column=Column(SAEnum(Mods, name="mods_enum"), nullable=False))
    pp: float = Field(description="The pp of the score", nullable=False)
    beatmap_id: int = Field(
        description="The beatmap (id) this score belongs to",
        foreign_key="beatmap.id",
        nullable=False,
    )
    user_id: int = Field(
        description="The user (id) this score belongs to",
        foreign_key="user.id",
        nullable=False,
    )
    user: "User" = Relationship(back_populates="scores")
    beatmap: "Beatmap" = Relationship(back_populates="scores")


# Beatmap models
class Beatmap(Base, MetadataMixin, table=True):
    mode: Modes = Field(sa_column=Column(SAEnum(Modes, name="mode_enum"), nullable=False))
    beatmapset: "Beatmapset" = Relationship(back_populates="beatmap")
    scores: list["Score"] = Relationship(
        back_populates="beatmap", sa_relationship_kwargs={"lazy": "select"}
    )  # Don't load scores until explicitly accessed

    beatmapset_id: int = Field(
        description="The beatmapset (id) this beatmap belongs to",
        foreign_key="beatmapset.id",
        nullable=False,
    )


# Beatmapset models
class Beatmapset(Base, MetadataMixin, table=True):
    beatmaps: list["Beatmap"] = Relationship(back_populates="beatmapset", cascade_delete=True)
