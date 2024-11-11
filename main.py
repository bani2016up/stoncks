from services import portfolio
from utils.templates import create_env
from utils.utils import file_exists_check
from api.adapter.main import DataCollector
import os, json
import argparse
import datetime
from utils.path import input_dir, output_dir
from typing import NoReturn
from services.stoncks_assistant import optimization, Portfolio


def env_check() -> None | NoReturn:
    if not os.path.exists('.env'):
        create_env()
        raise FileNotFoundError(f"Please add your API key to the '.env' file. You can generate it here: https://www.alphavantage.co/support/#api-key")

def file_check(file_path: str) -> NoReturn | None:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist.")


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
        portfolio = Portfolio(30_000)
        print(optimization(dt.time_index_series.series["2013-11-01"], portfolio))

if __name__ == "__main__":
    
    _argparse = argparse.ArgumentParser(description='Collects and analyzes data from various sources.')
    _argparse.add_argument('--api', action='store_true', help='Use api, not file.')
    _argparse.add_argument('--file', type=str, help=f'Filename in input dir.')
    
    args = _argparse.parse_args()
    if not args.api and not args.file:
        raise Exception("Please specify either '--api' or '--file'.")
    
    main(args)

    