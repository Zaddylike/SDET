#  internal  function
from TestPilot.data_loader import loading_yaml, case_queue
from TestPilot.api_handler import handle_api
from TestPilot.ws_handler import handle_websocket
from TestPilot.ui_web_handler import handle_ui_web
from TestPilot.stress_handler import handle_stress
from TestPilot.robot_handler import handle_robot
from TestPilot.utils.candy import try_wrapper
from TestPilot.report_handler import save_to_report
#  internal parameter
from TestPilot.config import REPORT_HEADERS
#  external function and parameter
import asyncio
import logging
logging = logging.getLogger(__name__)

#  handler_map
    #  "ui_app": handle_ui_app,
    # "stress": handle_stress,

HANDLER_MAP = {
    "api": handle_api,
    "websocket": handle_websocket,
    "stress": handle_stress,
    "robot": handle_robot,
    "ui_web": handle_ui_web,
}


@try_wrapper(log_msg="Task distribution failed")
async def run_testing(yaml_path: str, override_type:str = None, report_mode: str = "all"):
    yaml_queue = case_queue(yaml_path)
    tasks = []
    #  1. for-loop to gather distribution
    for yaml_path in yaml_queue:
        yaml_data = loading_yaml(yaml_path)
        meta_name = yaml_data.get('meta',{}).get('name','unknown_name')
        testing_type = override_type or yaml_data.get('type', None)

        #  2. find the testing type from pattern list
        handler = HANDLER_MAP.get(testing_type)
        if not handler:
            logging.debug("Unsupported test type")
            continue
        
        #  3. append handler and yaml_data to the tasks list
        logging.info(f"[Running] {meta_name} ({testing_type})")
        tasks.append(handler(yaml_data))

    # sem = asyncio.Semaphore(5)  # 同時最多 5 個
    # async def guarded_handle(yaml):
    #     async with sem:
    #         return await handle_ui_web(yaml)
    # await asyncio.gather(*(guarded_handle(y) for y in yamls))

    if tasks:
        results= await asyncio.gather(*tasks, return_exceptions=True)

    # for index, value in enumerate(results):
    #     yaml_name, report_data = value
    #     await save_to_report(yaml_name, REPORT_HEADERS, report_data)
        
    logging.info(f"All Test case  execution completed")
