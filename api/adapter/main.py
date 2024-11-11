
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

class DataCollector(object):
    
    def __init__(self) -> None:
        self.storage = []
        
        self._to_dump: list[str] = ["storage"]
        
    def dumps(self, file: TextIOWrapper) -> None:
        data = {}
        for attr in self._to_dump:
            data[attr] = getattr(self, attr)
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
        if v != ".":
            return float(v)
        else:
            return None
    
    @staticmethod
    def parse_data(data: dict, additional_fields: dict | None = None) -> dict:
        data["value"] = DataCollector.parse_value(data["value"])
        
        if additional_fields is not None:
            data.update(additional_fields)
            
        return data
        

    def API_source_materials(self) -> None:
        for data in materials():
            parser = partial(self.parse_data, additional_fields = {"name": data["name"]})
            self.storage.append(
                self.parse_assessment({
                "name": data["name"],
                "data": [i for i in map(parser, data["data"]) if i["value"] is not None][::-1]}
            ))
            
    @property
    def _sources(self) -> Generator[str, None, None]:
        for param in DataCollector.__dict__.keys():
            if param.startswith('API_source_'):
                yield param
                
                
    def request_all_data(self) -> None:
        for source in self._sources:
            getattr(self, source)()
    
    @staticmethod
    def stability_score(storables: list) -> list[float]:
        stability = [0.0] 
        time_inflation = [1/(0.99999999+x) for x in range(len(storables))][::-1]
        for i in range(1, len(storables)):
        
            if storables[i] == storables[i - 1]:
                stability.append(0)
            else:
                denom = max(abs(storables[i]), abs(storables[i - 1]))
                if denom == 0:
                    stability.append(0)
                else:
                    s_i = (storables[i] - storables[i - 1]) / denom
                    stability.append((s_i * time_inflation[i]) + stability[i-1])
        return stability
    
    @staticmethod
    def parse_assessment(data: dict) -> dict:
        stability_score: list[float] = DataCollector.stability_score([value["value"] for value in data["data"]])
        for index, stonc in enumerate(data["data"]):
            stonc["stability"] = stability_score[index]
        return data
        
    
    @property
    def series(self) -> list[Series]:
        import pdb; pdb.set_trace()
        return [Series.model_validate(i) for i in self.storage]
        
    @property
    def time_index_series(self) -> DateIndexedSeries:
        dates = {}
        for collection in self.storage:
            for item in collection["data"]:
                date = str(item["date"])
                if date not in dates:
                    dates[date] = [item]
                if item not in dates[date]:
                    dates[date].append(item)
                
        return DateIndexedSeries(series=dates)