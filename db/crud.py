from typing import Generator, TypeVar

from sqlmodel import Session, select

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


def get_ids(session: Session, model: type[Base], batch_size: int = 100, start_id=0) -> Generator[int, None, None]:
    """
    A generator that yields IDs of the given model from the database using id-based pagination.
    """
    while True:
        query = select(model.id).where(model.id > start_id).limit(batch_size)

        rows = session.exec(query).all()

        if not rows:
            break

        yield from rows
        start_id = rows[-1]
