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

@try_wrapper
def loading_yaml(fileName: str):
    with open(fileName, "r", encoding='utf-8') as file:
        yamlCase = yaml.safe_load(file)
        return yamlCase

#  make yaml_path mistake proof

@try_wrapper
def path_shaving(yaml_path: str):
    #  1. removing space and check type
    yaml_path = str(yaml_path).strip()
    #  2. confirm filename extension
    if not yaml_path.endswith('.yaml'):
        yaml_path += '.yaml'
    #  3. standarize path and combine
    yaml_path = os.path.normpath(yaml_path).lstrip('\\/')
    real_yaml_path = os.path.join(DEFAULT_CASE_DIR, yaml_path)
    #  4. confirm file exists
    if not os.path.exists(real_yaml_path):
        raise FileNotFoundError(f"This file not exist: {real_yaml_path}")
    
    return real_yaml_path

#  check .yaml file amount

@try_wrapper
def queue_case_files(path: str):
    if os.path.isdir(path):
        return [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".yaml") or f.endswith(".yml")]
    elif path.endswith(".yaml") or path.endswith(".yml"):
        return [path]
    else:
        raise ValueError("無效的 YAML 路徑")
