from datetime import date

from sqlalchemy import ForeignKey, MetaData, String
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
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    # date_created_note: Mapped[date]
    # date_change_note: Mapped[date]
    disease: Mapped[str] = mapped_column(String(100))
    vaccine_name: Mapped[str] = mapped_column(String(100))
    dose_number: Mapped[str] = mapped_column(String(30))
    vaccination_date: Mapped[date]
    expiration_date: Mapped[date | None]
    type_vaccine: Mapped[str] = mapped_column(String(100))
    lot: Mapped[str] = mapped_column(String(100))
    manufacturer: Mapped[str] = mapped_column(String(100))
    clinic: Mapped[str] = mapped_column(String(200))
    country: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(String(300), nullable=True)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    keycloak_id: Mapped[str] = mapped_column(String(255), unique=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
