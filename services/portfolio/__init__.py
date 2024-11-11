

from typing import Optional

from api.adapter.schemas import Stoncksable


class Portfolio(object):
    
    def __init__(self, balance: float, current_portfolio: Optional[list[Stoncksable]] | None = None):
        self.current_portfolio: list[Stoncksable] = current_portfolio if current_portfolio else []
        self.balance: float = balance