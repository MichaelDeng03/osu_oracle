from sqlmodel import Field, SQLModel


# Refer to https://osu.ppy.sh/docs/#userextended
# Simplified version of UserExtended model.
class UserSQLModel(SQLModel, table=True):
    id: int = Field(primary_key=True, description="Unique identifier for the user")
    avatar_url: str = Field(..., description="URL to the user's avatar image")
    country_code: str = Field(
        ..., description="ISO 3166-1 alpha-2 country code of the user"
    )
    username: str = Field(..., description="The user's username")


class BeatmapsetSQLModel(SQLModel, table=True):
    """
    Almost a comprehensive model of a beatmapset.
    Refer to https://tybug.dev/ossapi/api-reference.html#ossapi.models.Beatmapset
    And to https://osu.ppy.sh/docs/#beatmapsets
    """

    id: int = Field(
        primary_key=True, description="Unique identifier for the beatmapset"
    )
    artist: str = Field(..., description="Artist of the beatmapset")
    # beatmaps: list[BeatmapSQLModel] Go to bottom for relationships
    bpm: float = Field(..., description="Beats per minute of the beatmapset")
    creator: str = Field(..., description="Creator of the beatmapset")
    current_user_playcount: int = Field(..., description="Play count of the beatmapset")
    description: str = Field("", description="Description of the beatmapset")
    favourite_count: int = Field(
        ..., description="Number of times the beatmapset has been favourited"
    )
    language: str | None = Field(default=None, description="Language of the beatmapset")
    nsfw: bool = Field(
        default=False, description="Whether the beatmapset is marked as NSFW"
    )
    offset: int = Field(default=0)
    preview_url: str = Field(..., description="URL to the beatmapset preview audio")
    ranked: bool = Field(..., description="Whether the beatmapset is ranked")
    source: str = Field(..., description="Source of the beatmapset")
    tags: str = Field(..., description="Space-separated tags for the beatmapset")
    title: str = Field(..., description="Title of the beatmapset")
    title_unicode: str = Field(..., description="Unicode title of the beatmapset")
    user_id: int = Field(..., description="ID of the user who created the beatmapset")
    video: bool = Field(
        default=False, description="Whether the beatmapset contains a video"
    )

    beatmaps: list["BeatmapSQLModel"] = []  # Relationship placeholder


class BeatmapSQLModel(SQLModel, table=True):
    id: int = Field(primary_key=True, description="Unique identifier for the beatmap")

    accuracy: float = Field(..., description="OD value of the beatmap")
    ar: float = Field(..., description="AR value of the beatmap")
    beatmapset_id: int = Field(
        ..., description="ID of the beatmapset this beatmap belongs to"
    )
    bpm: float = Field(..., description="BPM of the beatmap")
    convert: bool = Field(
        default=False,
        description="Whether the beatmap is a conversion from another mode",
    )
    count_circles: int = Field(..., description="Number of circles in the beatmap")
    count_sliders: int = Field(..., description="Number of sliders in the beatmap")
    count_spinners: int = Field(..., description="Number of spinners in the beatmap")
    cs: float = Field(..., description="CS value of the beatmap")
    difficulty_rating: float = Field(..., description="Star rating of the beatmap")
    drain: float = Field(..., description="HP drain value of the beatmap")
    hit_length: int = Field(..., description="Length of the beatmap in seconds")
    is_scoreable: bool = Field(
        default=True, description="Whether the beatmap is scoreable"
    )
    max_combo: int = Field(..., description="Maximum combo of the beatmap")
    mode: str = Field(
        ...,
        description="Game mode of the beatmap. https://tybug.dev/ossapi/api-reference.html#ossapi.enums.GameMode",
    )
    passcount: int = Field(..., description="Number of passes on the beatmap")
    playcount: int = Field(..., description="Number of plays of the beatmap")
    ranked: int = Field(
        ...,
        description="Ranked status of the beatmap. https://tybug.dev/ossapi/api-reference.html#ossapi.enums.RankStatus",
    )
    rating: float = Field(..., description="Rating of the beatmap")
    top_tag_ids: list[int] = Field(
        default=[], description="List of top tag IDs associated with the beatmap"
    )
    total_length: int = Field(..., description="Total length of the beatmap in seconds")
    url: str = Field(..., description="URL to the beatmap")
    user_id: int = Field(..., description="ID of the user who created the beatmap")
    version: str = Field(
        ..., description="Version name of the beatmap (basically the diff name)"
    )


# class ScoreSQLModel(SQLModel, table=True):
# pass
