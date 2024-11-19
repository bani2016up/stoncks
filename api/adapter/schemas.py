import datetime
from typing import List
from pydantic import BaseModel, field_validator


type DataStoncksables = dict[str, list[Stoncksable]]

class Stoncksable(BaseModel):
    name: str
    date: str
    value: float
    stability: float = 0.0




class Series(BaseModel):
    name: str
    data: List[Stoncksable]


class DateIndexedSeries(BaseModel):
    series: DataStoncksables
