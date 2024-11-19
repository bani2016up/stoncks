
from collections.abc import Generator
import datetime
from functools import partial
from io import TextIOWrapper
import json
from tkinter import S
from turtle import pd
from typing import Any
from api.alphavantage.metals import materials
from api.adapter.schemas import Series, DateIndexedSeries
import numpy as np

class DataCollector(object):

    def __init__(self) -> None:
        self.storage = []

        self._to_dump: list[str] = ["storage"]

    def dumps(self, file: TextIOWrapper) -> None:
        data = {attr: getattr(self, attr) for attr in self._to_dump}
        json.dump(data, file)

    @staticmethod
    def loads(obj: str) -> "DataCollector":
        params: dict = json.loads(obj)
        new_instance = DataCollector()
        for key, value in params.items():
            setattr(new_instance, key, value)
        return new_instance

    @staticmethod
    def parse_value(v):
        return float(v) if v != "." else None

    @staticmethod
    def parse_data(data: dict, additional_fields: dict | None = None) -> dict:
        data["value"] = DataCollector.parse_value(data["value"])

        if additional_fields is not None:
            data |= additional_fields

        return data


    def calculate_stability(self, data):
        prices = [item['value'] for item in data if item['value'] is not None]
        if len(prices) < 2:
            return 0  # Not enough data to calculate stability

        price_changes = np.diff(prices) / prices[:-1]
        stability = np.std(price_changes)
        return stability


    def API_source_materials(self) -> None:
        for data in materials():
            parser = partial(self.parse_data, additional_fields = {"name": data["name"]})
            parsed_data = [i for i in map(parser, data["data"]) if i["value"] is not None][::-1]
            stability = self.calculate_stability(parsed_data)
            self.storage.append(
               {
                "name": data["name"],
                "data": parsed_data,
                "stability": stability
               }
            )


    @property
    def _sources(self) -> Generator[str, None, None]:
        for param in DataCollector.__dict__.keys():
            if param.startswith('API_source_'):
                yield param


    def request_all_data(self) -> None:
        for source in self._sources:
            getattr(self, source)()


    @property
    def series(self) -> list[Series]:
        return [Series.model_validate(i) for i in self.storage]

    @property
    def time_index_series(self) -> DateIndexedSeries:
        dates = {}
        for collection in self.storage:
            for item in collection["data"]:
                date = str(item["date"])
                if date not in dates:
                    dates[date] = []
                item_with_stability = item.copy()
                item_with_stability["stability"] = collection["stability"]
                if item_with_stability not in dates[date]:
                    dates[date].append(item_with_stability)

        return DateIndexedSeries(series=dates)
