

from typing import Optional

from api.adapter.schemas import Stoncksable


class Portfolio(object):
    
    def __init__(self, balance: float, current_portfolio: Optional[list[Stoncksable]] | None = None):
        self.current_portfolio: list[Stoncksable] = current_portfolio if current_portfolio else []
        self.current_pool: list[str] = [stock.name for stock in self.current_portfolio]
        self.balance: float = balance
        
    def set_stoncs(self, stocks: list[Stoncksable]) -> None:
        self.current_portfolio = stocks
        self.current_pool = [stock.name for stock in self.current_portfolio]
        self.balance -= self.stock_prices()
        
    def update_stonc_prices(self, stocks: list[Stoncksable]) -> None:
        updated_prices = {stock.name: stock.value for stock in stocks}
        for stock in self.current_portfolio:
            if stock.name in updated_prices:
                stock.value = updated_prices[stock.name]
        
    def stock_prices(self) -> float:
        return self.calculate_stock_prices(self.current_portfolio)
    
    @staticmethod
    def calculate_stock_prices(stocks: list[Stoncksable]) -> float:
        return sum([stock.value for stock in stocks])
    
    
    def money(self) -> float:
        return self.stock_prices() + self.balance
    
    def __repr__(self) -> str:
        return f"Portfolio with {len(self.current_portfolio)} stocks, balance: {self.money()} $"