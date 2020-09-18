from __future__ import annotations

from sqlalchemy.sql import expression

from app.models.db import BaseModel, TimedBaseModel, db


class User(TimedBaseModel):
    __tablename__ = "users"
    id = db.Column(db.BigInteger, primary_key=True, index=True, unique=True)

    first_name = db.Column(db.Unicode, nullable=True)
    last_name = db.Column(db.Unicode, nullable=True)
    username = db.Column(db.Unicode, nullable=True)
    mc_username = db.Column(db.Unicode, nullable=True)

    is_superuser = db.Column(db.Boolean, server_default=expression.false())
    start_conversation = db.Column(db.Boolean, server_default=expression.false())


class UserRelatedModel(BaseModel):
    __abstract__ = True

    user_id = db.Column(
        db.ForeignKey(f"{User.__tablename__}.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
