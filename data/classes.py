""" This module is for osu.db tables """

from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Beatmap(Base):
    __tablename__ = "beatmaps"

    id: Mapped[int] = mapped_column(primary_key=True)
    beatmap_id: Mapped[int | None] = mapped_column(default=-1)
    beatmapset_id: Mapped[int | None] = mapped_column(default=-1)
    difficulty_rating: Mapped[float | None] = mapped_column(default=-1)
    bpm: Mapped[float | None] = mapped_column(default=-1)
    count_circles: Mapped[int | None] = mapped_column(default=-1)
    count_sliders: Mapped[int | None] = mapped_column(default=-1)
    count_spinners: Mapped[int | None] = mapped_column(default=-1)
    cs: Mapped[float | None] = mapped_column(default=-1)
    drain: Mapped[float | None] = mapped_column(default=-1)
    accuracy: Mapped[float | None] = mapped_column(default=-1)
    ar: Mapped[float | None] = mapped_column(default=-1)
    max_combo: Mapped[int | None] = mapped_column(default=-1)
    length_seconds: Mapped[int | None] = mapped_column(default=-1)
    author_id: Mapped[int | None] = mapped_column(default=-1)
    mode_int: Mapped[int | None] = mapped_column(default=-1)
    version: Mapped[str | None] = mapped_column(default="")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(default=-1)
    username: Mapped[str | None] = mapped_column(String, default="")
    total_pp: Mapped[float | None] = mapped_column(default=-1)
    hit_acc: Mapped[float | None] = mapped_column(default=-1)
    ranked_score: Mapped[int | None] = mapped_column(default=-1)
    play_count: Mapped[int | None] = mapped_column(default=-1)
    playtime: Mapped[int | None] = mapped_column(default=-1)
    count_100: Mapped[int | None] = mapped_column(default=-1)
    count_50: Mapped[int | None] = mapped_column(default=-1)
    count_300: Mapped[int | None] = mapped_column(default=-1)
    count_miss: Mapped[int | None] = mapped_column(default=-1)
    total_hits: Mapped[int | None] = mapped_column(default=-1)
    country: Mapped[str | None] = mapped_column(default="")
    join_date: Mapped[datetime | None] = mapped_column(default="")
    update_date: Mapped[datetime | None] = mapped_column(default="")


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int | None] = mapped_column(primary_key=True)
    score_id: Mapped[int | None] = mapped_column(default=-1)
    user_id: Mapped[int | None] = mapped_column(default=-1)
    beatmap_id: Mapped[int | None] = mapped_column(default=-1)
    mods: Mapped[int | None] = mapped_column(default=-1)
    score: Mapped[int | None] = mapped_column(default=-1)
    max_combo: Mapped[int | None] = mapped_column(default=-1)
    perfect: Mapped[bool | None] = mapped_column(default=False)
    count_50: Mapped[int | None] = mapped_column(default=-1)
    count_100: Mapped[int | None] = mapped_column(default=-1)
    count_300: Mapped[int | None] = mapped_column(default=-1)
    count_geki: Mapped[int | None] = mapped_column(default=-1)
    count_katu: Mapped[int | None] = mapped_column(default=-1)
    count_miss: Mapped[int | None] = mapped_column(default=-1)
    pp: Mapped[float | None] = mapped_column(default=-1.0)
    rank: Mapped[str | None] = mapped_column(String(5), default="")
    created_at: Mapped[datetime | None] = mapped_column(default="")
    mode: Mapped[int | None] = mapped_column(String(5), default=-1)
    name: Mapped[str | None] = mapped_column(String(50), default="")


class Beatmapset(Base):
    __tablename__ = "beatmapsets"

    id: Mapped[int | None] = mapped_column(primary_key=True)
    beatmapset_id: Mapped[int | None] = mapped_column(default=-1)
    language: Mapped[str | None] = mapped_column(default="")
    nsfw: Mapped[bool | None] = mapped_column(default=False)
    play_count: Mapped[int | None] = mapped_column(default=-1)
    ranked_date: Mapped[datetime | None] = mapped_column(default="")  # ISO 8601
    tags: Mapped[str | None] = mapped_column(default="")
    title: Mapped[str | None] = mapped_column(default="")
    artist: Mapped[str | None] = mapped_column(default="")
    author_id: Mapped[int | None] = mapped_column(default=-1)
