from datetime import date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class VaccineBase(Base):
    __tablename__ = 'vaccines'
    id: Mapped[int] = mapped_column(primary_key=True)
    # user: Mapped[str]
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
