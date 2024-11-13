import matplotlib.pyplot

from utils.templates import create_env
from api.adapter.main import DataCollector
import os
import argparse
from utils.path import input_dir, output_dir
from typing import NoReturn
from services.stoncks_assistant import time_scaled_optimization, Portfolio
import matplotlib
import pandas as pd


def env_check() -> None | NoReturn:
    if not os.path.exists('.env'):
        create_env()
        raise FileNotFoundError(f"Please add your API key to the '.env' file. You can generate it here: https://www.alphavantage.co/support/#api-key")

def file_check(file_path: str) -> NoReturn | None:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist.")



def date_range(start_date: str, end_date: str) -> list[str]:
    return [d.strftime("%Y-%m-%d") for d in pd.date_range(start=start_date, end=end_date, freq="MS")]

def main(args: argparse.Namespace) -> None:
    if args.api:
        env_check()
        dt = DataCollector()
        dt.request_all_data()
        with open(f"{output_dir}/dump.json", "w") as f:
            dt.dumps(f)
            
    elif args.file is not None:
        with open(f"{input_dir}/{args.file}", "r") as f:
            data = "\n".join(f.readlines())
        dt = DataCollector.loads(data)
        portfolio = Portfolio(60_000)
        dates = date_range("2000-01-01", "2024-09-01")
        solutions = []
        for solution in time_scaled_optimization(dt.time_index_series, dates, portfolio):
            solutions.append(solution.portfolio.money())
            print(solution)
            
        matplotlib.pyplot.plot(dates, solutions)
        matplotlib.pyplot.show()
        

if __name__ == "__main__":
    
    _argparse = argparse.ArgumentParser(description='Collects and analyzes data from various sources.')
    _argparse.add_argument('--api', action='store_true', help='Use api, not file.')
    _argparse.add_argument('--file', type=str, help=f'Filename in input dir.')
    
    args = _argparse.parse_args()
    if not args.api and not args.file:
        raise Exception("Please specify either '--api' or '--file'.")
    
    main(args)

    