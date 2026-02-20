"""Modelli SQLAlchemy — tabelle User, Character, Progress."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from database import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=new_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(50), nullable=False)
    role = Column(String(20), nullable=False, default="studente")  # studente | docente
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    characters = relationship("Character", back_populates="owner", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="owner", uselist=False, cascade="all, delete-orphan")


class Character(Base):
    __tablename__ = "characters"

    id = Column(String(36), primary_key=True, default=new_uuid)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    character_name = Column(String(50), nullable=False)
    class_id = Column(Integer, nullable=False, default=0)       # 0-4 (Guerriero..Bardo)
    element_id = Column(Integer, nullable=False, default=4)     # 0-4 (Fuoco..Neutro)
    appearance_id = Column(Integer, nullable=False, default=0)  # 0-11
    level = Column(Integer, nullable=False, default=1)
    xp = Column(Integer, nullable=False, default=0)
    hp = Column(Integer, nullable=False, default=100)
    max_hp = Column(Integer, nullable=False, default=100)
    attack = Column(Integer, nullable=False, default=15)
    defense = Column(Integer, nullable=False, default=10)
    speed = Column(Integer, nullable=False, default=10)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="characters")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "character_name": self.character_name,
            "class": self.class_id,
            "element": self.element_id,
            "appearance_id": self.appearance_id,
            "level": self.level,
            "xp": self.xp,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "attack": self.attack,
            "defense": self.defense,
            "speed": self.speed,
            "owner_uid": self.owner_id,
            "owner_username": self.owner.username if self.owner else "",
            "owner_role": self.owner.role if self.owner else "studente",
            "created_at": self.created_at.isoformat() if self.created_at else "",
        }


class Progress(Base):
    __tablename__ = "progress"

    id = Column(String(36), primary_key=True, default=new_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    player_name = Column(String(50), default="Studente")
    player_level = Column(Integer, default=1)
    player_xp = Column(Integer, default=0)
    player_gold = Column(Integer, default=0)
    player_energy = Column(Integer, default=100)
    owned_items = Column(JSON, default=list)
    unlocked_skills = Column(JSON, default=list)
    earned_trophies = Column(JSON, default=list)
    equipped_items = Column(JSON, default=dict)
    total_battles_won = Column(Integer, default=0)
    total_bosses_defeated = Column(JSON, default=list)
    total_questions_answered = Column(Integer, default=0)
    total_questions_correct = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    current_dungeon_floor = Column(Integer, default=0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="progress")

    def to_dict(self) -> dict:
        return {
            "player_name": self.player_name or "Studente",
            "player_level": self.player_level or 1,
            "player_xp": self.player_xp or 0,
            "player_gold": self.player_gold or 0,
            "player_energy": self.player_energy or 100,
            "owned_items": self.owned_items or [],
            "unlocked_skills": self.unlocked_skills or [],
            "earned_trophies": self.earned_trophies or [],
            "equipped_items": self.equipped_items or {},
            "total_battles_won": self.total_battles_won or 0,
            "total_bosses_defeated": self.total_bosses_defeated or [],
            "total_questions_answered": self.total_questions_answered or 0,
            "total_questions_correct": self.total_questions_correct or 0,
            "best_streak": self.best_streak or 0,
            "current_dungeon_floor": self.current_dungeon_floor or 0,
        }
