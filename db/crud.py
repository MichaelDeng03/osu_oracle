from typing import TypeVar

from sqlmodel import Session

from db.orm.models import Base

TModel = TypeVar("TModel", bound=Base)
TUpdate = TypeVar("TUpdate", bound=Base)


def create_generic(db: Session, model: TModel) -> TModel:
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def update_generic(db: Session, model: TModel, model_update: TUpdate) -> TModel:
    fields_payload = model_update.model_dump(exclude_none=True)
    for value in fields_payload:
        setattr(model, value, fields_payload[value])
    db.commit()
    db.refresh(model)
    return model


def delete_generic(db: Session, model: TModel) -> TModel:
    db.delete(model)
    db.commit()
    return model


def get_generic(db: Session, model: type[TModel], id: int) -> TModel | None:
    return db.get(model, id)


def create_or_ignore(db: Session, model: TModel) -> TModel:
    existing = get_generic(db, type(model), model.id)
    if existing:
        return existing
    return create_generic(db, model)
