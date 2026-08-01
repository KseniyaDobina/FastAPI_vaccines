from pydantic import BaseModel


class Vaccine(BaseModel):
    title: str
    description: str | None = None
    country: str | None = None
    city: str | None = None
