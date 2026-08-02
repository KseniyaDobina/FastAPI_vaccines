from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class VaccineBase(Base):
    __tablename__ = 'vaccines'
    id: Mapped[int] = mapped_column(primary_key=True)
    disease: Mapped[str]
    vaccine_name: Mapped[str]
    # vaccination_date: Mapped[datetime]
    # expiration_date: Mapped[datetime | None]
    clinic: Mapped[str]
    country: Mapped[str]
    city: Mapped[str]
    notes: Mapped[str | None] = mapped_column(nullable=True)
