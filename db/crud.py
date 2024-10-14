from collections.abc import Sequence
from typing import TypeVar
from uuid import UUID

from sqlmodel import Session, select

from .orm.models import Base

TModel = TypeVar("ModelType", bound=Base)
TUpdate = TypeVar("UpdateType", bound=Base)


def create_generic(db: Session, model: TModel) -> TModel:
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def update_generic(db: Session, model: TModel, model_update: TUpdate) -> TModel:
    if model is None:
        return None

    fields_payload = model_update.model_dump(exclude_none=True)
    for value in fields_payload:
        setattr(model, value, fields_payload[value])
    db.commit()
    db.refresh(model)


def delete_generic(db: Session, model: TModel) -> TModel:
    db.delete(model)
    db.commit()
    return model


def get_generic(db: Session, model: TModel, model_id: int) -> TModel:
    return db.get(model, model_id)
