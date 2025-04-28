#  internal  function
from TestPilot.data_loader import loading_yaml, path_shaving
#  internal parameter
from TestPilot.config import REPORT_HEADERS
from TestPilot.api_handler import handle_api
from TestPilot.report_handler import save_to_report
from TestPilot.utils.candy import try_wrapper
#  external function and parameter
import os
import logging
logging = logging.getLogger(__name__)

#  handler_map
HANDLER_MAP = {
    "api": handle_api,
#     "websocket": handle_websocket,
#     "ui_web": handle_ui_web,
#     "ui_app": handle_ui_app,
#     "robot": handle_robot,
}

@try_wrapper
def run_testing(yaml_path: str, override_type:str = None, report_mode: str = "all"):
    yaml_data = loading_yaml(path_shaving(yaml_path))
    case_name = yaml_data.get('meta',{}).get('name','unknown_case')

    testing_type = override_type or yaml_data.get('type', None)
    handler = HANDLER_MAP.get(testing_type)
    if not handler:
        logging.debug("[DEBUG] Unsupported test type")
        raise ValueError(f"不支援的測試類型: {testing_type}")
    
    logging.info(f"[START] Running {case_name} testing flow")
    
    report_name, result_list = handler(yaml_data)
    save_to_report(report_name, REPORT_HEADERS, result_list, report_mode)

    logging.info(f"[END] Testing Done")

    return True