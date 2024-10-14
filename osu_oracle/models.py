# """ This module is for osu.db tables """

# from datetime import datetime

# from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# class Base(DeclarativeBase):
#     pass


# class User(Base):
#     __tablename__ = "users"

#     user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     username: Mapped[str | None] = mapped_column(String(50), nullable=True)
#     total_pp: Mapped[float | None] = mapped_column(Float, nullable=True)
#     hit_acc: Mapped[float | None] = mapped_column(Float, nullable=True)
#     playtime: Mapped[int | None] = mapped_column(default=-1, nullable=True)
#     country: Mapped[str | None] = mapped_column(String(2), nullable=True)
#     update_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

#     # Relationships
#     scores: Mapped[list["Score"]] = relationship("Score", back_populates="user")  # List of user scores
#     beatmapsets: Mapped[list["Beatmapset"]] = relationship(
#         "Beatmapset", back_populates="user"
#     )  # List of beatmapsets the user has created


# class Score(Base):
#     __tablename__ = "scores"

#     score_id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
#     beatmap_id: Mapped[int] = mapped_column(ForeignKey('beatmaps.beatmap_id'))
#     mods: Mapped[int] = mapped_column(Integer)
#     mode: Mapped[int | None] = mapped_column(String(5))
#     max_combo: Mapped[int | None] = mapped_column(Integer, nullable=True)
#     pp: Mapped[float] = mapped_column(Float, nullable=True)
#     rank: Mapped[str | None] = mapped_column(String(5), nullable=True)
#     created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

#     # Relationships
#     user: Mapped["User"] = relationship("User", back_populates="scores")
#     beatmap: Mapped["Beatmap"] = relationship("Beatmap", back_populates="scores")


# class Beatmap(Base):
#     __tablename__ = "beatmaps"

#     beatmap_id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     beatmapset_id: Mapped[int] = mapped_column(ForeignKey('beatmapsets.beatmapset_id'))
#     difficulty_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
#     bpm: Mapped[float | None] = mapped_column(Float, nullable=True)
#     count_circles: Mapped[int | None] = mapped_column(Integer, nullable=True)
#     count_sliders: Mapped[int | None] = mapped_column(Integer, nullable=True)
#     count_spinners: Mapped[int | None] = mapped_column(Integer, nullable=True)
#     cs: Mapped[float | None] = mapped_column(Float, nullable=True)
#     drain: Mapped[float | None] = mapped_column(Float, nullable=True)
#     accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
#     ar: Mapped[float | None] = mapped_column(Float, nullable=True)
#     max_combo: Mapped[int | None] = mapped_column(Integer, nullable=True)
#     length_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
#     author_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
#     mode_int: Mapped[int | None] = mapped_column(Integer, nullable=True)
#     version: Mapped[str | None] = mapped_column(String(50), nullable=True)

#     # Relationships
#     beatmapset: Mapped["Beatmapset"] = relationship("Beatmapset", back_populates="beatmaps")
#     scores: Mapped[list["Score"]] = relationship("Score", back_populates="beatmap")


# class Beatmapset(Base):
#     __tablename__ = "beatmapsets"

#     beatmapset_id: Mapped[int] = mapped_column(primary_key=True)
#     language: Mapped[str | None] = mapped_column(String(20), nullable=True)
#     ranked_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
#     tags: Mapped[str | None] = mapped_column(String(50))
#     title: Mapped[str | None] = mapped_column(String(50))
#     artist: Mapped[str | None] = mapped_column(String(50))
#     author_id: Mapped[int | None] = mapped_column(ForeignKey('users.user_id'))
#     # TODO Add cards

#     # Relationships
#     user: Mapped["User"] = relationship("User", back_populates="beatmapsets")
#     beatmaps: Mapped[list["Beatmap"]] = relationship("Beatmap", back_populates="beatmapset")
