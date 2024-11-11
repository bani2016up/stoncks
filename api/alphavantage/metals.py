import requests
from collections.abc import Generator
import os

api_key = os.getenv('api_key')



def request_data(material: str) -> dict:
    url = f'https://www.alphavantage.co/query?function={material}&interval=monthly&apikey={api_key}'
    r: requests.Response = requests.get(url)
    data = r.json()
    return data


_materials = ['COPPER', 'ALUMINUM', "WHEAT", "CORN", "COTTON", "SUGAR", "COFFEE"]

def materials() -> Generator[dict, None, None]:
    for material in _materials:
        yield request_data(material)



