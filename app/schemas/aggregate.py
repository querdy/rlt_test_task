from datetime import datetime

from pydantic import BaseModel, field_validator


class RequestAggregateSchema(BaseModel):
    dt_from: datetime
    dt_upto: datetime
    group_type: str

    @classmethod
    @field_validator('dt_from', 'dt_upto')
    def date_validator(cls, v: str) -> datetime:
        return datetime.fromisoformat(v)


class ResponseAggregateSchema(BaseModel):
    dataset: list[int]
    labels: list[str]
