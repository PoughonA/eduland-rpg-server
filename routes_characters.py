"""Routes: CRUD Personaggi (per utente autenticato)."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from database import get_db
from models import User, Character
from deps import get_current_user

router = APIRouter(prefix="/api", tags=["characters"])


# ━━━ Schemas ━━━
class CharacterCreate(BaseModel):
    character_name: str
    class_id: int = 0       # 0=Guerriero, 1=Arciere, 2=Mago, 3=Ladro, 4=Bardo
    element_id: int = 4     # 0=Fuoco, 1=Aria, 2=Terra, 3=Acqua, 4=Neutro
    appearance_id: int = 0  # 0-11

    @field_validator("character_name")
    @classmethod
    def name_length(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 20:
            raise ValueError("Nome personaggio deve essere tra 2 e 20 caratteri")
        return v

    @field_validator("class_id")
    @classmethod
    def class_valid(cls, v: int) -> int:
        if v < 0 or v > 4:
            raise ValueError("Classe deve essere 0-4")
        return v

    @field_validator("element_id")
    @classmethod
    def element_valid(cls, v: int) -> int:
        if v < 0 or v > 4:
            raise ValueError("Elemento deve essere 0-4")
        return v

    @field_validator("appearance_id")
    @classmethod
    def appearance_valid(cls, v: int) -> int:
        if v < 0 or v > 11:
            raise ValueError("Aspetto deve essere 0-11")
        return v


# ━━━ Endpoints ━━━
@router.get("/characters")
def list_characters(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista personaggi dell'utente autenticato."""
    chars = db.query(Character).filter(Character.owner_id == user.id).all()
    return [c.to_dict() for c in chars]


@router.post("/characters", status_code=status.HTTP_201_CREATED)
def create_character(
    req: CharacterCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crea un nuovo personaggio per l'utente autenticato."""
    # Limite: max 10 personaggi per utente
    count = db.query(Character).filter(Character.owner_id == user.id).count()
    if count >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Massimo 10 personaggi per account.",
        )
    char = Character(
        owner_id=user.id,
        character_name=req.character_name.strip(),
        class_id=req.class_id,
        element_id=req.element_id,
        appearance_id=req.appearance_id,
    )
    db.add(char)
    db.commit()
    db.refresh(char)
    return char.to_dict()
