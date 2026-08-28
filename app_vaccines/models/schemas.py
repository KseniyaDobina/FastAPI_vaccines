from datetime import date
from pydantic import BaseModel, ConfigDict, Field, model_validator

class VaccineCreate(BaseModel):
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

    @model_validator(mode="after")
    def validate_expiration_date(self):
        if (
                self.expiration_date is not None
                and self.expiration_date <= self.vaccination_date
        ):
            raise ValueError(
                "expiration_date должна быть позже, чем vaccination_date"
            )

        return self

class VaccineID(VaccineCreate):
    id: int
    user_id: int
    # date_created_note: date
    # date_change_note: date
    model_config = ConfigDict(from_attributes=True)

class VaccineUpdate(BaseModel):
    disease: str | None = Field(default=None, min_length=3, max_length=100)
    vaccine_name: str | None = Field(default=None, min_length=3, max_length=100)
    dose_number: str | None = Field(default=None, min_length=1, max_length=30)
    vaccination_date: date | None = None
    expiration_date: date | None = None
    type_vaccine: str | None = Field(default=None, min_length=1, max_length=100)
    lot: str | None = Field(default=None, min_length=1, max_length=100)
    manufacturer: str | None = Field(default=None, min_length=2, max_length=100)
    clinic: str | None = Field(default=None, min_length=3, max_length=200)
    country: str | None = Field(default=None, min_length=2, max_length=100)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    notes: str | None = Field(default=None, min_length=1, max_length=300)

    @model_validator(mode="after")
    def validate_dates(self):
        if (
                self.vaccination_date is not None
                and self.expiration_date is not None
                and self.expiration_date <= self.vaccination_date
        ):
            raise ValueError(
                "expiration_date должна быть позже, чем vaccination_date"
            )

        return self

class MessageAPIResponse(BaseModel):
    message: str

class CurrentUser(BaseModel):
    sub: str
    username: str | None = None
    email: str | None = None

class UserResponse(BaseModel):
    id: int
    username: str | None = None
    email: str | None = None

    model_config = ConfigDict(from_attributes=True)
