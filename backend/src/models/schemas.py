"""Pydantic request and response contracts for the HTTP API."""

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=256)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)


class LoginRequest(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str = Field(min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class GameSearchResponse(BaseModel):
    game_uuid: str
    title: str
    platforms: list[str] = []
    developers: list[str] = []
    publishers: list[str] = []
    total_playtime_minutes: int | None = None
    esrb_rating: str | None = None
    total_user_rating: float | None = None
    first_release_date: date | None = None
    release_year: int | None = None
    min_price: float | None = None
    max_price: float | None = None
    genres: list[str] = []


class CollectionResponse(BaseModel):
    collection_uuid: str
    user_uuid: str
    collection_name: str
    num_of_games: int
    total_playtime: int


class CollectionCreateRequest(BaseModel):
    collection_name: str = Field(min_length=1, max_length=255)


class CollectionRenameRequest(BaseModel):
    new_name: str = Field(min_length=1, max_length=255)


class CollectionGameRequest(BaseModel):
    game_title: str = Field(min_length=1, max_length=255)


class PlayRequest(BaseModel):
    game_title: str = Field(min_length=1, max_length=255)
    minutes: int = Field(ge=0, le=100_000)


class RateRequest(BaseModel):
    game_title: str = Field(min_length=1, max_length=255)
    rating: int = Field(ge=1, le=5)


class FollowRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)


class UserSearchResponse(BaseModel):
    username: str
    followers: int
    following: int
    collections: int


class MessageResponse(BaseModel):
    message: str
