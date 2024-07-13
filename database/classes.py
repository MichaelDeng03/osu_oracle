""" This module is for osu.db tables """

from dataclasses import dataclass
from ossapi import Ossapi
import ossapi.models
from time import strftime, localtime
import time
from datetime import datetime


@dataclass
class Beatmap:
    """
    Keeps select attributes from ossapi.models.Beatmap
    """

    beatmap_id: int
    beatmapset_id: int
    difficulty_rating: float
    bpm: float
    count_circles: int
    count_sliders: int
    count_spinners: int
    cs: float
    drain: float
    accuracy: float
    ar: float
    max_combo: int
    length_seconds: int
    author_id: int
    mode_int: int
    version: str

    def __init__(self, beatmap: ossapi.models.Beatmap):
        self.beatmap_id = getattr(beatmap, "id", None)
        self.beatmapset_id = getattr(beatmap, "beatmapset_id", None)
        self.difficulty_rating = getattr(beatmap, "difficulty_rating", None)
        self.bpm = getattr(beatmap, "bpm", None)
        self.count_circles = getattr(beatmap, "count_circles", None)
        self.count_sliders = getattr(beatmap, "count_sliders", None)
        self.count_spinners = getattr(beatmap, "count_spinners", None)
        self.cs = getattr(beatmap, "cs", None)
        self.drain = getattr(beatmap, "drain", None)
        self.accuracy = getattr(beatmap, "accuracy", None)
        self.ar = getattr(beatmap, "ar", None)
        self.max_combo = getattr(beatmap, "max_combo", None)
        self.length_seconds = getattr(beatmap, "total_length", None)
        self.author_id = getattr(beatmap, "user_id", None)
        self.mode_int = getattr(beatmap, "mode_int", None)
        self.version = getattr(beatmap, "version", None)

    def insert(self, cursor):
        """Inserts beatmap into beatmaps table, if it doesn't already exist."""
        sql = """
        INSERT OR IGNORE INTO beatmaps (
            beatmap_id, beatmapset_id, difficulty_rating, bpm, count_circles, count_sliders, 
            count_spinners, cs, drain, accuracy, ar, max_combo, length_seconds, 
            author_id, mode_int, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(
            sql,
            (
                self.beatmap_id,
                self.beatmapset_id,
                self.difficulty_rating,
                self.bpm,
                self.count_circles,
                self.count_sliders,
                self.count_spinners,
                self.cs,
                self.drain,
                self.accuracy,
                self.ar,
                self.max_combo,
                self.length_seconds,
                self.author_id,
                self.mode_int,
                self.version,
            ),
        )


@dataclass
class User:
    """Keep select attributes from ossapi.models.User"""

    user_id: int
    username: str
    total_pp: float
    hit_acc: float
    ranked_score: int
    play_count: int
    playtime: int
    count_100: int
    count_50: int
    count_300: int
    count_miss: int
    total_hits: int
    country: str
    join_date: str  # ISO 8601
    update_date: str  # ISO 8601

    def __init__(self, user: ossapi.models.User):
        self.user_id = getattr(user, "id", None)
        self.username = getattr(user, "username", None)

        # Check if 'statistics' exists in user and set attributes accordingly
        statistics = getattr(user, "statistics", None)
        if statistics:
            self.total_pp = getattr(statistics, "pp", None)
            self.hit_acc = getattr(statistics, "hit_accuracy", None)
            self.ranked_score = getattr(statistics, "ranked_score", None)
            self.play_count = getattr(statistics, "play_count", None)
            self.playtime = getattr(statistics, "play_time", None)
            self.count_100 = getattr(statistics, "count_100", None)
            self.count_50 = getattr(statistics, "count_50", None)
            self.count_300 = getattr(statistics, "count_300", None)
            self.count_miss = getattr(statistics, "count_miss", None)
            self.total_hits = getattr(statistics, "total_hits", None)
        else:
            self.total_pp = None
            self.hit_acc = None
            self.ranked_score = None
            self.play_count = None
            self.playtime = None
            self.count_100 = None
            self.count_50 = None
            self.count_300 = None
            self.count_miss = None
            self.total_hits = None

        self.country = getattr(user, "country", None)
        self.country = getattr(self.country, "code", None) if self.country else None
        self.join_date = getattr(user, "join_date", None)
        self.join_date = (
            datetime.strftime(self.join_date, "%Y-%m-%d %H:%M:%S")
            if self.join_date
            else None
        )
        self.update_date = strftime("%Y-%m-%d %H:%M:%S", localtime(time.time()))

    def insert(self, cursor):
        """Inserts or updates into users table"""
        sql = """
        INSERT INTO users (
            user_id, username, total_pp, hit_acc, ranked_score, play_count, playtime, count_100, count_50, 
            count_300, count_miss, total_hits, country, join_date, update_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            total_pp = excluded.total_pp,
            hit_acc = excluded.hit_acc,
            ranked_score = excluded.ranked_score,
            play_count = excluded.play_count,
            playtime = excluded.playtime,
            count_100 = excluded.count_100,
            count_50 = excluded.count_50,
            count_300 = excluded.count_300,
            count_miss = excluded.count_miss,
            total_hits = excluded.total_hits,
            country = excluded.country,
            join_date = excluded.join_date,
            update_date = excluded.update_date
        """
        cursor.execute(
            sql,
            (
                self.user_id,
                self.username,
                self.total_pp,
                self.hit_acc,
                self.ranked_score,
                self.play_count,
                self.playtime,
                self.count_100,
                self.count_50,
                self.count_300,
                self.count_miss,
                self.total_hits,
                self.country,
                self.join_date,
                self.update_date,
            ),
        )


@dataclass
class Score:
    """
    Keeps select attributes from ossapi.models.Score
    """

    score_id: int
    user_id: int
    beatmap_id: int
    mods: int
    score: int
    max_combo: int
    perfect: bool
    count_50: int
    count_100: int
    count_300: int
    count_geki: int
    count_katu: int
    count_miss: int
    pp: float
    rank: str
    created_at: str  # ISO 8601
    mode: int
    name: str

    def __init__(self, score: ossapi.models.Score):
        self.score_id = getattr(score, "id", None)
        self.user_id = getattr(score, "user_id", None)

        # Handle nested beatmap attributes
        beatmap = getattr(score, "beatmap", None)
        self.beatmap_id = getattr(beatmap, "id", None) if beatmap else None

        # Handle mods if they exist
        mods = getattr(score, "mods", None)
        self.mods = getattr(mods, "value", None) if mods else None

        self.score = getattr(score, "score", None)
        self.max_combo = getattr(score, "max_combo", None)
        self.perfect = getattr(score, "perfect", None)

        # Handle nested statistics attributes
        statistics = getattr(score, "statistics", None)
        self.count_50 = getattr(statistics, "count_50", None) if statistics else None
        self.count_100 = getattr(statistics, "count_100", None) if statistics else None
        self.count_300 = getattr(statistics, "count_300", None) if statistics else None
        self.count_geki = (
            getattr(statistics, "count_geki", None) if statistics else None
        )
        self.count_katu = (
            getattr(statistics, "count_katu", None) if statistics else None
        )
        self.count_miss = (
            getattr(statistics, "count_miss", None) if statistics else None
        )

        self.pp = getattr(score, "pp", None)
        self.rank = getattr(score, "rank", None)
        self.rank = getattr(self.rank, "value", None) if self.rank else None
        self.created_at = getattr(score, "created_at", None)
        self.created_at = datetime.strftime(self.created_at, "%Y-%m-%d %H:%M:%S")
        self.mode = getattr(score, "mode_int", None)

        self.name = None

    def insert(self, cursor):
        """Inserts into scores table"""
        sql = """
        INSERT OR IGNORE INTO scores (
            score_id, user_id, beatmap_id, mods, score, max_combo, perfect, count_50, count_100, 
            count_300, count_geki, count_katu, count_miss, pp, rank, created_at, mode
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(
            sql,
            (
                self.score_id,
                self.user_id,
                self.beatmap_id,
                self.mods,
                self.score,
                self.max_combo,
                self.perfect,
                self.count_50,
                self.count_100,
                self.count_300,
                self.count_geki,
                self.count_katu,
                self.count_miss,
                self.pp,
                self.rank,
                self.created_at,
                self.mode,
            ),
        )


@dataclass
class Beatmapset:
    """
    Keeps select attributes from ossapi.models.Beatmapset
    """

    beatmapset_id: int
    language: str
    nsfw: bool
    play_count: int
    ranked_date: str  # ISO 8601
    tags: str
    title: str
    artist: str
    author_id: int

    def __init__(self, beatmapset: ossapi.models.Beatmapset):
        self.beatmapset_id = getattr(beatmapset, "id", None)
        self.language = getattr(beatmapset, "language", None)
        if self.language and "name" in self.language:
            self.language = self.language["name"]

        self.nsfw = getattr(beatmapset, "nsfw", None)
        self.play_count = getattr(beatmapset, "play_count", None)
        self.ranked_date = getattr(beatmapset, "ranked_date", None)
        self.ranked_date = (
            datetime.strftime(self.ranked_date, "%Y-%m-%d %H:%M:%S")
            if self.ranked_date
            else None
        )
        self.tags = getattr(beatmapset, "tags", None)
        self.title = getattr(beatmapset, "title", None)
        self.artist = getattr(beatmapset, "artist", None)
        self.author_id = getattr(beatmapset, "user_id", None)

    def insert(self, cursor):
        """Inserts into table."""

        query = """
        INSERT OR IGNORE INTO beatmapsets (
            beatmapset_id, language, nsfw, play_count, ranked_date, tags, title, artist, author_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(
            query,
            (
                self.beatmapset_id,
                self.language,
                self.nsfw,
                self.play_count,
                self.ranked_date,
                self.tags,
                self.title,
                self.artist,
                self.author_id,
            ),
        )
