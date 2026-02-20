"""Routes: Save / Load / Reset progressi giocatore."""
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import User, Progress
from deps import get_current_user
from typing import Any

router = APIRouter(prefix="/api", tags=["progress"])


# ━━━ Schemas ━━━
class ProgressData(BaseModel):
    player_name: str = "Studente"
    player_level: int = 1
    player_xp: int = 0
    player_gold: int = 0
    player_energy: int = 100
    owned_items: list[str] = []
    unlocked_skills: list[int] = []
    earned_trophies: list[str] = []
    equipped_items: dict[str, Any] = {}
    total_battles_won: int = 0
    total_bosses_defeated: list[str] = []
    total_questions_answered: int = 0
    total_questions_correct: int = 0
    best_streak: int = 0
    current_dungeon_floor: int = 0


# ━━━ Endpoints ━━━
@router.get("/progress")
def load_progress(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Carica progressi dell'utente."""
    prog = db.query(Progress).filter(Progress.user_id == user.id).first()
    if prog is None:
        # Nessun progresso ancora: ritorna defaults vuoti
        return ProgressData().model_dump()
    return prog.to_dict()


@router.put("/progress")
def save_progress(
    data: ProgressData,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Salva/aggiorna progressi dell'utente (upsert)."""
    prog = db.query(Progress).filter(Progress.user_id == user.id).first()
    if prog is None:
        prog = Progress(user_id=user.id)
        db.add(prog)
    # Aggiorna tutti i campi
    prog.player_name = data.player_name
    prog.player_level = data.player_level
    prog.player_xp = data.player_xp
    prog.player_gold = data.player_gold
    prog.player_energy = data.player_energy
    prog.owned_items = data.owned_items
    prog.unlocked_skills = data.unlocked_skills
    prog.earned_trophies = data.earned_trophies
    prog.equipped_items = data.equipped_items
    prog.total_battles_won = data.total_battles_won
    prog.total_bosses_defeated = data.total_bosses_defeated
    prog.total_questions_answered = data.total_questions_answered
    prog.total_questions_correct = data.total_questions_correct
    prog.best_streak = data.best_streak
    prog.current_dungeon_floor = data.current_dungeon_floor
    db.commit()
    db.refresh(prog)
    return {"message": "Progressi salvati", "data": prog.to_dict()}


@router.delete("/progress", status_code=status.HTTP_200_OK)
def reset_progress(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reset completo dei progressi (cancella la riga)."""
    prog = db.query(Progress).filter(Progress.user_id == user.id).first()
    if prog:
        db.delete(prog)
        db.commit()
    return {"message": "Progressi resettati"}
