

import math
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.problems.functional import ElementwiseProblem


import numpy as np
import random

from pymoo.config import Config

from api.adapter.schemas import Stoncksable
from services import portfolio
from services.portfolio import Portfolio




Config.warnings["not_compiled"] = False


class OptimizationProblem(ElementwiseProblem):
    def __init__(
        self, balance: float, pool: list[Stoncksable], **kwargs
    ):
        
        self.pool: list[Stoncksable] = pool
        self.balance: float = balance

        
    
        super().__init__(
            n_var=len(pool),
            n_obj=1,
            n_ieq_constr=1,
            xl=np.concatenate(
                [[0 for i in range(len(pool))]]
            ),
            xu=np.concatenate(
                [[50 for i in range(len(pool))]]
            ),
            vtype=int,
            **kwargs
        )

    def _evaluate(self, x, out, *args, **kwargs):

        revenue = sum([self.pool[index].value * value for index, value in enumerate(x)])
        stability = np.mean([self.pool[index].stability * value for index, value in enumerate(x)])
        
        #diversity = max(x) - (sum(x)/len(x)) 
        

        out["F"] = np.array([- stability])
        out["G"] = np.array([revenue - self.balance])
        
        
class OptimizationResponse:
    
    def __init__(self, portfolio: Portfolio, date: str, _suggestions: list[Stoncksable]):
        self.portfolio: Portfolio = portfolio
        self.date: str = date
        self._suggestions = _suggestions
        
    @property
    def suggestions(self) -> str:
        counts = {}
        for s in self._suggestions:
            if s.name in counts:
                continue
            counts[s.name] = self._suggestions.count(s)
        return ", ".join([f"{k} X{v}" for k, v in counts.items()])
        
    def __repr__(self) -> str:
        return f"Portfolio on {self.date}: {self.portfolio.money()}$. Suggestions: {self.suggestions}"