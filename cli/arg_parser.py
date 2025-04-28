import argparse
from TestPilot.utils.candy import try_wrapper


@try_wrapper
def get_cli_args():
    parser = argparse.ArgumentParser(description="Run TestPilot with a YAML test file")
    parser.add_argument("--yaml", required=True, help="path to the yaml test file")
    
    return parser.parse_args()
