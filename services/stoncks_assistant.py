
from collections.abc import Generator
from multiprocessing import Pool
import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.termination.default import DefaultMultiObjectiveTermination
from pymoo.operators.sampling.lhs import LatinHypercubeSampling
from pymoo.operators.crossover.sbx import SimulatedBinaryCrossover
from api.adapter.main import DataCollector
from services.optimization import OptimizationProblem, minimize, OptimizationResponse
from pymoo.core.problem import StarmapParallelization
from api.adapter.schemas import Stoncksable, DateIndexedSeries, Series
from services.portfolio import Portfolio


gens = 500
pop_size = 100

evals = gens * pop_size



termination = DefaultMultiObjectiveTermination(
        xtol=1e-8,
        cvtol=0.00001,
        ftol=1e-6 ,
        period=30,
        n_max_gen=gens,
        n_max_evals=evals
    )

algorithm = NSGA2(
        pop_size=pop_size,
        sampling=LatinHypercubeSampling(),
        crossover=SimulatedBinaryCrossover(prob_var=0.9, eta=1)
        )




def time_scaled_optimization(pool: DataCollector, dates: list[str], portfolio: Portfolio) -> Generator[OptimizationResponse, None, None]:
    values = {}
    series = pool.time_index_series
    for date in dates:
        portfolio.update_stonc_prices(series.series[date])
        old_stoncs = portfolio.current_portfolio.copy()
        values[date] = optimization(series.series[date], portfolio.money())
        portfolio.set_stoncs([])
        portfolio.balance += portfolio.calculate_stock_prices(old_stoncs)
        portfolio.set_stoncs(values[date])
        yield OptimizationResponse(portfolio, date, values[date])

def optimization(pool: list[Stoncksable], balance: float) -> list[Stoncksable]:
    #runner = StarmapParallelization(Pool(24).starmap)
    problem = OptimizationProblem(balance, pool)

    result = minimize(
            problem,
            algorithm,
            termination=termination,
            seed=1,
            verbose=False,
            save_history=False,
        )

    solution_1 =  [round(x) for x in result.X]
    try:
        return list(np.concatenate([[pool[i]] * x for i, x in enumerate(solution_1) if x > 0]).flatten())
    except ValueError:
        return []
