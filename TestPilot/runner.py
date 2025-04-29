#  internal  function
from TestPilot.data_loader import loading_yaml, path_shaving, queue_case_files
#  internal parameter
from TestPilot.config import REPORT_HEADERS
from TestPilot.api_handler import handle_api
from TestPilot.ws_handler import handle_websocket
from TestPilot.report_handler import save_to_report
from TestPilot.utils.candy import try_wrapper
#  external function and parameter
import asyncio
import logging

logging = logging.getLogger(__name__)



#  handler_map
#  "ui_web": handle_ui_web,
#  "ui_app": handle_ui_app,
#  "robot": handle_robot,
HANDLER_MAP = {
    "api": handle_api,
    "websocket": handle_websocket,
}


@try_wrapper()
async def run_testing(yaml_path: str, override_type:str = None, report_mode: str = "all"):
    yaml_paths= queue_case_files(yaml_path)
    
    tasks = []

    for yaml_path in yaml_paths:
        yaml_data = loading_yaml(yaml_path)
        case_name = yaml_data.get('meta',{}).get('name','unknown_meta_name')
        testing_type = override_type or yaml_data.get('type', None)

        handler = HANDLER_MAP.get(testing_type)
        if not handler:
            logging.debug("Unsupported test type")
            continue
        
        logging.info(f"[Running] {case_name} ({testing_type})")

        if asyncio.iscoroutinefunction(handler):
            tasks.append(handler(yaml_data))
        else:
            tasks.append(asyncio.to_thread(handler, yaml_data))

    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logging.info(f"[Finish] All tests executed")
