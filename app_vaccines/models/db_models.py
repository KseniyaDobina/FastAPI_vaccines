from datetime import date

from sqlalchemy import ForeignKey, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Vaccine(Base):
    __tablename__ = "vaccines"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    # date_created_note: Mapped[date]
    # date_change_note: Mapped[date]
    disease: Mapped[str]
    vaccine_name: Mapped[str]
    dose_number: Mapped[str]
    vaccination_date: Mapped[date]
    expiration_date: Mapped[date | None]
    type_vaccine: Mapped[str]
    lot: Mapped[str]
    manufacturer: Mapped[str]
    clinic: Mapped[str]
    country: Mapped[str]
    city: Mapped[str]
    notes: Mapped[str | None] = mapped_column(nullable=True)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    keycloak_id: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str | None]
    email: Mapped[str | None]
