from pydantic import BaseModel


class Vaccine(BaseModel):
    disease: str
    vaccine_name: str
    # vaccination_date: date
    # expiration_date: date | None = None
    clinic: str
    country: str
    city: str
    notes: str | None = None

class VaccineUpdate(BaseModel):
    disease: str | None = None
    vaccine_name: str | None = None
    # vaccination_date: date
    # expiration_date: date | None = None
    clinic: str | None = None
    country: str | None = None
    city: str | None = None
    notes: str | None = None
