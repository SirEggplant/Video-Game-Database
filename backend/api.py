"""FastAPI application exposing the Video Game Database features."""

import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

# These imports work both with ``python backend/api.py`` and with
# ``uvicorn backend.api:app --reload`` (the backend package registers src).
from src.auth.authentication import login_with_email, login_with_user, register
from src.collections.crud import (
    add_game_to_collection,
    check_if_collection_exists,
    create_collection,
    delete_collection,
    delete_game_from_collection,
    list_users_collections,
    rename_collection,
)
from src.games.playing import play_Game, rate_Game
from src.games.recommendations import recommend_games
from src.games.search import (
    get_game_all,
    get_game_by_developer,
    get_game_by_genre,
    get_game_by_platform,
    get_game_by_price_between,
    get_game_by_price_lower_than,
    get_game_by_publisher,
    get_game_by_release_year,
    get_game_by_title,
    get_games_by_esrb,
)
from src.models.schemas import (
    CollectionCreateRequest,
    CollectionGameRequest,
    CollectionRenameRequest,
    CollectionResponse,
    FollowRequest,
    GameSearchResponse,
    LoginRequest,
    MessageResponse,
    PlayRequest,
    RateRequest,
    RegisterRequest,
    TokenResponse,
    UserSearchResponse,
)
from src.social.follow import follow, get_followers, get_my_follows, search_by_email, unfollow


JWT_SECRET = os.getenv("JWT_SECRET", "change-this-development-jwt-secret")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 12
bearer_scheme = HTTPBearer()

app = FastAPI(title="Video Game Database API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_error_handler(_request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request, exc: RequestValidationError):
    message = "; ".join(error["msg"] for error in exc.errors())
    return JSONResponse(status_code=422, content={"detail": message})


@app.exception_handler(Exception)
async def unexpected_error_handler(_request, _exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def _token_for(user_uuid: str, username: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": user_uuid, "username": username, "exp": expires_at}, JWT_SECRET, JWT_ALGORITHM)


def current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]) -> dict[str, str]:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise ValueError("Missing subject")
        return {"user_uuid": str(user_uuid), "username": str(payload.get("username", ""))}
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token")


CurrentUser = Annotated[dict[str, str], Depends(current_user)]
GAME_FIELDS = (
    "game_uuid", "title", "platforms", "developers", "publishers", "total_playtime_minutes",
    "esrb_rating", "total_user_rating", "first_release_date", "release_year", "min_price",
    "max_price", "genres",
)


def _json_value(value: Any) -> Any:
    if isinstance(value, (datetime, Decimal)):
        return str(value) if isinstance(value, datetime) else float(value)
    return value


def _game_dict(row: Any) -> dict[str, Any]:
    game = {name: _json_value(value) for name, value in zip(GAME_FIELDS, row)}
    game["game_uuid"] = str(game["game_uuid"])
    for key in ("platforms", "developers", "publishers", "genres"):
        game[key] = game[key] or []
    return game


def _collection_dict(row: Any) -> dict[str, Any]:
    return {
        "collection_uuid": str(row[0]), "user_uuid": str(row[1]), "collection_name": row[2],
        "num_of_games": row[3], "total_playtime": row[4],
    }


def _matches(value: Any, query: str) -> bool:
    if isinstance(value, (list, tuple)):
        return any(query.lower() in str(item).lower() for item in value)
    return query.lower() in str(value or "").lower()


def _search_games(**filters: Any) -> list[dict[str, Any]]:
    """Delegate retrieval to the existing search functions, then combine filters."""
    active = {key: value for key, value in filters.items() if value is not None}
    if not active:
        rows = get_game_all()
    elif "title" in active:
        rows = get_game_by_title(["", "", "", active["title"]])
    elif "genre" in active:
        rows = get_game_by_genre(active["genre"])
    elif "platform" in active:
        rows = get_game_by_platform(active["platform"])
    elif "year" in active:
        rows = get_game_by_release_year(str(active["year"]))
    elif "developer" in active:
        rows = get_game_by_developer(["", "", "", active["developer"]])
    elif "publisher" in active:
        rows = get_game_by_publisher(["", "", "", active["publisher"]])
    elif active.get("price_min") is not None and active.get("price_max") is not None:
        rows = get_game_by_price_between(str(active["price_min"]), str(active["price_max"]))
    elif "price_max" in active:
        rows = get_game_by_price_lower_than(str(active["price_max"]))
    elif "esrb" in active:
        rows = get_games_by_esrb(active["esrb"])
    else:
        rows = get_game_all()

    games = [_game_dict(row) for row in (rows or [])]
    for key, value in active.items():
        if key == "price_min":
            games = [game for game in games if game["min_price"] is not None and game["min_price"] >= value]
        elif key == "price_max":
            games = [game for game in games if game["max_price"] is not None and game["max_price"] <= value]
        elif key == "year":
            games = [game for game in games if game["release_year"] == value]
        elif key == "esrb":
            games = [game for game in games if _matches(game["esrb_rating"], value)]
        else:
            field = "genres" if key == "genre" else f"{key}s" if key in {"developer", "publisher"} else key
            games = [game for game in games if _matches(game.get(field), value)]
    return games


@app.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(request: RegisterRequest):
    user = register(request.username, request.password, request.first_name, request.last_name, request.email)
    if not user:
        raise HTTPException(status_code=409, detail="Username or email is already registered")
    return {"access_token": _token_for(str(user[0]), request.username)}


@app.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    if bool(request.username) == bool(request.email):
        raise HTTPException(status_code=400, detail="Provide exactly one of username or email")
    user = login_with_user(request.username, request.password) if request.username else login_with_email(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    return {"access_token": _token_for(str(user[0]), user[1])}


@app.get("/games/search", response_model=list[GameSearchResponse])
def search_games(title: str | None = None, genre: str | None = None, platform: str | None = None,
                 year: int | None = None, developer: str | None = None, publisher: str | None = None,
                 price_min: float | None = None, price_max: float | None = None, esrb: str | None = None):
    return _search_games(title=title, genre=genre, platform=platform, year=year, developer=developer,
                         publisher=publisher, price_min=price_min, price_max=price_max, esrb=esrb)


@app.get("/games/recommendations", response_model=list[GameSearchResponse])
def recommendations(user: CurrentUser):
    return [_game_dict(row) for row in (recommend_games(user["user_uuid"]) or [])]


@app.get("/collections", response_model=list[CollectionResponse])
def collections(user: CurrentUser):
    return [_collection_dict(row) for row in (list_users_collections(user["user_uuid"]) or [])]


@app.post("/collections", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def create_user_collection(request: CollectionCreateRequest, user: CurrentUser):
    if check_if_collection_exists(user["user_uuid"], request.collection_name):
        raise HTTPException(status_code=409, detail="A collection with that name already exists")
    created = create_collection(user["user_uuid"], request.collection_name)
    if not created:
        raise HTTPException(status_code=400, detail="Could not create collection")
    rows = list_users_collections(user["user_uuid"]) or []
    return next(_collection_dict(row) for row in rows if row[2] == request.collection_name)


@app.put("/collections/{collection_name}", response_model=CollectionResponse)
def rename_user_collection(collection_name: str, request: CollectionRenameRequest, user: CurrentUser):
    updated = rename_collection(user["user_uuid"], collection_name, request.new_name)
    if not updated:
        raise HTTPException(status_code=404, detail="Collection not found or name already in use")
    return _collection_dict(updated)


@app.delete("/collections/{collection_name}", response_model=MessageResponse)
def delete_user_collection(collection_name: str, user: CurrentUser):
    if not check_if_collection_exists(user["user_uuid"], collection_name):
        raise HTTPException(status_code=404, detail="Collection not found")
    delete_collection(user["user_uuid"], collection_name)
    return {"message": "Collection deleted"}


@app.post("/collections/{collection_name}/games", response_model=MessageResponse)
def add_collection_game(collection_name: str, request: CollectionGameRequest, user: CurrentUser):
    if not check_if_collection_exists(user["user_uuid"], collection_name):
        raise HTTPException(status_code=404, detail="Collection not found")
    if not add_game_to_collection([collection_name, request.game_title], user["user_uuid"]):
        raise HTTPException(status_code=400, detail="Could not add game to collection")
    return {"message": "Game added to collection"}


@app.delete("/collections/{collection_name}/games/{game_uuid}", response_model=MessageResponse)
def remove_collection_game(collection_name: str, game_uuid: str, user: CurrentUser):
    if not check_if_collection_exists(user["user_uuid"], collection_name):
        raise HTTPException(status_code=404, detail="Collection not found")
    game = next((row for row in (get_game_all() or []) if str(row[0]) == game_uuid), None)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if not delete_game_from_collection([collection_name, game[1]]):
        raise HTTPException(status_code=400, detail="Could not remove game from collection")
    return {"message": "Game removed from collection"}


@app.post("/games/play", response_model=MessageResponse)
def record_play(request: PlayRequest, user: CurrentUser):
    if not play_Game(user["user_uuid"], ["play", str(request.minutes), request.game_title]):
        raise HTTPException(status_code=400, detail="Could not record play session; you may not own this game")
    return {"message": "Play session recorded"}


@app.post("/games/rate", response_model=MessageResponse)
def rate_game(request: RateRequest, user: CurrentUser):
    if not rate_Game(user["user_uuid"], [request.game_title, str(request.rating)]):
        raise HTTPException(status_code=400, detail="Could not rate game; you may not own this game")
    return {"message": "Game rating saved"}


@app.post("/social/follow", response_model=MessageResponse)
def follow_user(request: FollowRequest, user: CurrentUser):
    if not follow(user["user_uuid"], request.username):
        raise HTTPException(status_code=400, detail="Could not follow user")
    return {"message": "User followed"}


@app.post("/social/unfollow", response_model=MessageResponse)
def unfollow_user(request: FollowRequest, user: CurrentUser):
    if not unfollow(user["user_uuid"], request.username):
        raise HTTPException(status_code=404, detail="Follow relationship not found")
    return {"message": "User unfollowed"}


def _social_rows(rows: Any) -> list[dict[str, Any]]:
    result = []
    for username, details in rows or []:
        followers, following, collections = details or (0, 0, 0)
        result.append({"username": username, "followers": followers, "following": following, "collections": collections})
    return result


@app.get("/social/followers", response_model=list[UserSearchResponse])
def followers(user: CurrentUser):
    return _social_rows(get_followers(user["user_uuid"]))


@app.get("/social/following", response_model=list[UserSearchResponse])
def following(user: CurrentUser):
    return _social_rows(get_my_follows(user["user_uuid"]))


@app.get("/users/search", response_model=list[UserSearchResponse])
def user_search(email: str):
    return _social_rows(search_by_email(email))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.api:app", host="127.0.0.1", port=8000, reload=True)
