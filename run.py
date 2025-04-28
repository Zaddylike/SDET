#  internal function
from TestPilot.runner import run_testing

#  internal parameter
from TestPilot.config import setup_logger
from cli.arg_parser import get_cli_args




if __name__ == "__main__":
    setup_logger()
    args = get_cli_args()
    run_testing(args.yaml)
    