from pydantic import BaseModel, ConfigDict


class VaccineAdd(BaseModel):
    disease: str
    vaccine_name: str
    # vaccination_date: date
    # expiration_date: date | None = None
    clinic: str
    country: str
    city: str
    notes: str | None = None

class VaccineID(VaccineAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)

class VaccineUpdate(BaseModel):
    disease: str | None = None
    vaccine_name: str | None = None
    # vaccination_date: date
    # expiration_date: date | None = None
    clinic: str | None = None
    country: str | None = None
    city: str | None = None
    notes: str | None = None
