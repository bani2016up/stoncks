
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.termination.default import DefaultMultiObjectiveTermination
from pymoo.operators.sampling.lhs import LatinHypercubeSampling
from pymoo.operators.crossover.sbx import SimulatedBinaryCrossover
from services.optimization import OptimizationProblem, minimize

from api.adapter.schemas import Stoncksable, DateIndexedSeries
from services.portfolio import Portfolio


gens = 1000
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



def time_scaled_optimization(series: DateIndexedSeries, dates: list[str], portfolio: Portfolio) -> dict[str, list[Stoncksable]]:
    values = {}
    for date in dates:
        values[date] = optimization(series.series[date], portfolio)
    return values
        
def optimization(pool: list[Stoncksable], portfolio: Portfolio) -> list[Stoncksable]:
    problem = OptimizationProblem(portfolio.balance, pool)
    
    result = minimize(
            problem,
            algorithm,
            termination=termination,
            seed=1,
            verbose=True,
            save_history=False,
        )

    solution_1 =  [round(x) for x in result.X[0]]
    return [(pool[i], x) for i, x in enumerate(solution_1) if x > 0]