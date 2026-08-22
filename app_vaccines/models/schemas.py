from pydantic import BaseModel, ConfigDict, Field

class VaccineCreate(BaseModel):
    disease: str = Field(min_length=3, max_length=100)
    vaccine_name: str = Field(min_length=3, max_length=100)
    # vaccination_date: date
    # expiration_date: date | None = None
    clinic: str = Field(min_length=3, max_length=200)
    country: str = Field(min_length=2, max_length=100)
    city: str = Field(min_length=2, max_length=100)
    notes: str | None = Field(default=None, min_length=1, max_length=300)

class VaccineID(VaccineCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class VaccineUpdate(BaseModel):
    disease: str | None = Field(default=None, min_length=3, max_length=100)
    vaccine_name: str | None = Field(default=None, min_length=3, max_length=100)
    # vaccination_date: date
    # expiration_date: date | None = None
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
