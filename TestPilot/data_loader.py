#  internal funciton
from TestPilot.utils.candy import try_wrapper
#  internal parameters
from TestPilot.config import DEFAULT_CASE_DIR

#  external function and parameters
import yaml
import os
import logging
logging = logging.getLogger(__name__)


#  reading .yaml file and return 
@try_wrapper(log_msg="Failed to load YAML file")
def loading_yaml(fileName: str):
    with open(fileName, "r", encoding='utf-8') as file:
        yamlCase = yaml.safe_load(file)
        return yamlCase

#  check .yaml file amount
@try_wrapper(log_msg="Failed to queue case files")
def case_queue(path: str):
    path = os.path.normpath(path)
    abs_path = os.path.abspath(path)
    abs_default = os.path.abspath(DEFAULT_CASE_DIR)

    if os.path.commonpath([abs_path, abs_default]) == DEFAULT_CASE_DIR:
        pass
    else:
        path = os.path.join(DEFAULT_CASE_DIR, path)

    if os.path.isdir(path):
        return [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".yaml") or f.endswith(".yml")]
    elif path.endswith(".yaml") or path.endswith(".yml"):
        return [path]
    elif not os.path.isfile(path):
        path+=".yaml"

    if not os.path.isfile(path):
        raise FileNotFoundError(f"{path}")
    
    return [path]