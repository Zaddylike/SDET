import logging, time ,json
from playwright.sync_api import sync_playwright
from functools import reduce

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s:%(lineno)d]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

import os

DEFAULT_CASE_DIR = 'tests'
path = 'tests/nextgen/nextgen_ui_login.yaml'

X = os.path.normpath(path)
logging.info(X)

# 絕對路徑化，避免 './', '../' 這種情況
abs_path = os.path.abspath(path)
default_abs = os.path.abspath(DEFAULT_CASE_DIR)
logging.info(path)
# 判斷 abs_path 是否在 default_abs 目錄下
if abs_path.startswith(default_abs):
    print('已經在 DEFAULT_CASE_DIR 下')
else:
    path = os.path.join(DEFAULT_CASE_DIR, path)
