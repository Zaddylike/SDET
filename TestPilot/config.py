#  internal function
#  internal parameter
#  external function and paramter
import os
import asyncio
import httpx

#  Setting: logging style

def setup_logger():
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s:%(lineno)d]  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

#  Setting: Default Path

BASE_DIR = os.getcwd()
DEFAULT_CASE_DIR = os.path.join(BASE_DIR, 'tests')
DEFAULT_REPORT_DIR = os.path.join(BASE_DIR, 'report')

# default report header 

REPORT_HEADERS = [
    "Time",
    "Api_name",
    "Case_name",
    "Loop",
    "Run_time",
    "Expected_key",
    "Response_value",
    "Comparator",
    "Expected_value",
    "Result"
    ]

#  http client

http_client = httpx.AsyncClient(timeout=8)

#  asyncio lock 

save_lock = asyncio.Lock()
ws_lock = asyncio.Lock()
http_lock = asyncio.Lock()
client_lock = asyncio.Lock()
