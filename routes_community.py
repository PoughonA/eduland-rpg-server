"""Routes: Community — classifica globale e personaggi di tutti gli utenti."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import User, Character, Progress
from deps import get_current_user

router = APIRouter(prefix="/api/community", tags=["community"])


@router.get("/characters")
def list_all_characters(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Ritorna tutti i personaggi di tutti gli utenti (per la tab community)."""
    chars = (
        db.query(Character)
        .options(joinedload(Character.owner))
        .order_by(Character.level.desc(), Character.created_at.desc())
        .limit(200)
        .all()
    )
    return [c.to_dict() for c in chars]


@router.get("/users")
def list_all_users(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Ritorna classifica utenti — ordinata per XP decrescente."""
    users = db.query(User).all()
    result = []
    for u in users:
        # Carica progressi se esistono
        prog = db.query(Progress).filter(Progress.user_id == u.id).first()
        entry = {
            "uid": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "level": prog.player_level if prog else 1,
            "xp": prog.player_xp if prog else 0,
        }
        result.append(entry)
    # Ordina per XP decrescente
    result.sort(key=lambda x: x["xp"], reverse=True)
    return result[:100]
