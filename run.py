#  internal function
from TestPilot.runner import run_testing

#  internal parameter
from TestPilot.config import setup_logger
from cli.arg_parser import get_cli_args
# external function and parameter
import asyncio
setup_logger()

def main():
    args = get_cli_args()
    asyncio.run(run_testing(args.yaml, None, args.report))


if __name__ == "__main__":
    main()
    