import numpy as np
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_401_UNAUTHORIZED
from joblib import load
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from functools import lru_cache

# Security
security = HTTPBearer()
TOKEN = "hacker101"

# App instance
app = FastAPI(
    title="Premier League Regression Prediction",
    description="""
    This API serves a regression ML model for predicting total minutes played by a Premier League player based on stats.
    Features:
    - Accepts any frontend (CORS enabled)
    - Protected with Bearer token authentication
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "DELETE"],
    allow_headers=["*"],
)

# Token-based Authorization
def authorize(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != TOKEN:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="A valid token is needed!"
        )
    return credentials.credentials

# Load ML model with LRU caching
@lru_cache()
def get_model():
    return load("model.pkl")

# Pydantic model for input validation
class Validate(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=100)
    club: str = Field(..., min_length=1, max_length=50)
    nationality: str = Field(..., min_length=1, max_length=50)
    position: str 

    appearances: int = Field(..., ge=0, le=50)
    minutes: int = Field(..., ge=0, le=4000)
    shots: int = Field(..., ge=0, le=200)
    shots_on_target: int = Field(..., ge=0, le=150)
    touches: int = Field(..., ge=0, le=5000)
    passes: int = Field(..., ge=0, le=3000)
    successful_passes: int = Field(..., ge=0, le=3000)
    crosses: int = Field(..., ge=0, le=300)
    successful_crosses: int = Field(..., ge=0, le=300)
    carries: int = Field(..., ge=0, le=1000)
    progressive_carries: int = Field(..., ge=0, le=500)
    tackles: int = Field(..., ge=0, le=200)
    interceptions: int = Field(..., ge=0, le=200)
    clearances: int = Field(..., ge=0, le=300)

    conversion_rate: Optional[float] = Field(None, ge=0, le=100)
    pass_accuracy: Optional[float] = Field(None, ge=0, le=100)
    cross_accuracy: Optional[float] = Field(None, ge=0, le=100)

    @field_validator('player_name', 'club', 'nationality')
    @classmethod
    def check_not_empty(cls, v):
        if not v.strip():
            raise ValueError("This field must not be empty.")
        return v

# Prediction Endpoint
@app.post("/predict")
def predict(data: Validate, token: str = Depends(authorize)):
    # Fill input data in the correct order (ensure this matches training order)
    input_data = np.array([
        data.appearances,
        data.shots,
        data.shots_on_target,
        data.conversion_rate or 0,
        0,  # Big Chances Missed
        0,  # Hit Woodwork
        0,  # Offsides
        data.touches,
        data.passes,
        data.successful_passes,
        data.pass_accuracy or 0,
        data.crosses,
        data.successful_crosses,
        data.cross_accuracy or 0,
        0, 0, 0, 0,  # fThird passes, successful, %, Through Balls
        data.carries,
        data.progressive_carries,
        0, 0, 0, 0,  # Carries ended with goal, assist, shot, chance
        0, 0, 0,  # Possession Won, Dispossessed, Clean Sheets
        data.clearances,
        data.interceptions,
        0,  # Blocks
        data.tackles,
        0, 0, 0,  # Ground duels
        0, 0, 0,  # Aerial duels
        0, 0, 0,  # Goals Conceded, Own Goals, Fouls
        0, 0, 0,  # Yellow, Red, Saves
        0, 0, 0,  # Saves %, Penalties Saved, Clearances Off Line
        0, 0,  # Punches, High Claims
        0, 0, 0,  # Encoded position, club, nationality
        0, 0, 0   # Duplicates of encoded fields
    ]).reshape(1, -1)

    model = get_model()
    prediction = model.predict(input_data).item()

    return {
        "player_name": data.player_name,
        "predicted_minutes": prediction
    }
