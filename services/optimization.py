

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.problems.functional import ElementwiseProblem


import numpy as np
import random

from pymoo.config import Config

from api.adapter.schemas import Stoncksable




Config.warnings["not_compiled"] = False


class OptimizationProblem(ElementwiseProblem):
    def __init__(
        self, balance: float, pool: list[Stoncksable], **kwargs
    ):
        
        self.pool: list[Stoncksable] = pool
        self.balance = balance
        
        lower_bounders = [0 for i in range(len(pool))]
    
        super().__init__(
            n_var=len(pool),
            n_obj=3,
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
        stability = sum([self.pool[index].stability * value for index, value in enumerate(x)])
        
        diversity = max(x) - (sum(x)/len(x)) 
        

        out["F"] = np.array([- revenue, - stability, - diversity])
        out["G"] = np.array([revenue - self.balance])
        