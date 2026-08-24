from datetime import date
from pydantic import BaseModel, ConfigDict, Field

class VaccineCreate(BaseModel):
    # user: str = Field(min_length=3, max_length=100)
    # date_created_note: date
    # date_change_note: date
    disease: str = Field(min_length=3, max_length=100)
    vaccine_name: str = Field(min_length=3, max_length=100)
    dose_number: str = Field(min_length=1, max_length=30)
    vaccination_date: date
    expiration_date: date | None = None
    type_vaccine: str = Field(min_length=1, max_length=100)
    lot: str = Field(min_length=1, max_length=100)
    manufacturer: str = Field(min_length=2, max_length=100)
    clinic: str = Field(min_length=3, max_length=200)
    country: str = Field(min_length=2, max_length=100)
    city: str = Field(min_length=2, max_length=100)
    notes: str | None = Field(default=None, min_length=1, max_length=300)

class VaccineID(VaccineCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class VaccineUpdate(BaseModel):
    # user: str = Field(min_length=3, max_length=100)
    # date_created_note: date
    # date_change_note: date
    disease: str | None = Field(default=None, min_length=3, max_length=100)
    vaccine_name: str | None = Field(default=None, min_length=3, max_length=100)
    dose_number: str = Field(min_length=1, max_length=30)
    vaccination_date: date
    expiration_date: date | None = None
    type_vaccine: str = Field(min_length=1, max_length=100)
    lot: str = Field(min_length=1, max_length=100)
    manufacturer: str = Field(min_length=2, max_length=100)
    clinic: str | None = Field(default=None, min_length=3, max_length=200)
    country: str | None = Field(default=None, min_length=2, max_length=100)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    notes: str | None = Field(default=None, min_length=1, max_length=300)

class VaccineAPIResponse(BaseModel):
    message: str
    vaccine: VaccineID

class ListVaccineUpdateAPIResponse(BaseModel):
    message: str
    vaccines: list[VaccineID]

class MessageAPIResponse(BaseModel):
    message: str
