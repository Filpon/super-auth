from datetime import date

from typing import Optional
from pydantic import BaseModel


class EventBaseSchema(BaseModel):
    """
    Events base validating

    """
    name: str
    date: date
    client_info: Optional[str] = None


class EventCreateSchema(EventBaseSchema):
    """
    Events creation validating

    """


class EventFetchSchema(EventBaseSchema):
    """
    Events fetching validating

    """
    id: int

    class Config:  # pylint: disable=C0115,R0903
        from_attributes = True
