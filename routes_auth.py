"""Routes: Registrazione e Login."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth_utils import hash_password, verify_password, create_token

router = APIRouter(prefix="/api", tags=["auth"])


# ━━━ Schemas ━━━
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: str
    role: str = "studente"

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("La password deve avere almeno 6 caratteri")
        return v

    @field_validator("username")
    @classmethod
    def username_length(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 20:
            raise ValueError("Username deve essere tra 2 e 20 caratteri")
        return v

    @field_validator("role")
    @classmethod
    def role_valid(cls, v: str) -> str:
        if v not in ("studente", "docente"):
            raise ValueError("Ruolo deve essere 'studente' o 'docente'")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    uid: str
    token: str
    username: str
    email: str
    role: str
    message: str


# ━━━ Endpoints ━━━
@router.post("/register", response_model=AuthResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # Controlla se email gia' registrata
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email gia' registrata. Usa ACCEDI.",
        )
    # Crea utente
    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        username=req.username.strip(),
        role=req.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    # Genera token
    token = create_token(user.id, user.email)
    return AuthResponse(
        uid=user.id,
        token=token,
        username=user.username,
        email=user.email,
        role=user.role,
        message="Registrazione riuscita!",
    )


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account non trovato. Registrati prima.",
        )
    if not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password errata.",
        )
    token = create_token(user.id, user.email)
    return AuthResponse(
        uid=user.id,
        token=token,
        username=user.username,
        email=user.email,
        role=user.role,
        message="Login riuscito!",
    )
