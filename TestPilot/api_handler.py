#  internal function
from TestPilot.validator import validate_response
from TestPilot.utils.candy import try_wrapper, register_pattern
from TestPilot.report_handler import save_to_report
#  internal parameter
from TestPilot.config import REPORT_HEADERS, DEFAULT_CASE_DIR
#  external function and paramter
import requests
import time
import logging
logging = logging.getLogger(__name__)

API_TYPE_HANDLE ={}

#  send get api

@try_wrapper()
@register_pattern(API_TYPE_HANDLE, 'get')
def send_api_get(params, expect):
    url = params.get('url', "unknown_url")
    headers = params.get('headers', {})
    body = params.get('body', {})

    response = requests.get(url, headers=headers, params=body, timeout=8)
    return validate_response(response, expect)

#  send post api

@try_wrapper()
@register_pattern(API_TYPE_HANDLE, 'post')
def send_api_post(params, expect):
    url = params.get('url', "unknown_url")
    headers = params.get('headers', {})
    body = params.get('body', {})

    response = requests.post(url, headers=headers, json=body, timeout=8)
    return validate_response(response, expect)

#  handle send http api

@try_wrapper()
async def handle_api(yaml_data):
    yaml_name = yaml_data.get("meta", {}).get('name','')
    cases = yaml_data.get("cases", [])
    results = []
    report_data = []
    for case in cases:
        params = case.get('params', {})
        expect = case.get('expect', [])

        name = params.get('name', "unknown_case_name")
        method = params.get('method', 'post')
        loops = int(params.get('loop', 1))
        retrys = params.get('retry', 0)

        # handle loop and send
        for loop in range(loops):
            time.sleep(1)
            for tys in range(retrys+1):
                start = time.perf_counter()
                try:
                    send_api_function = API_TYPE_HANDLE.get(method, None)
                    if send_api_function:
                        results =  send_api_function(params, expect)
                except Exception as e:
                    logging.error(f"Failed to send api: {e},and retry ({tys}/{retrys})")
                    if tys == retrys:
                        results = [{
                            "Expected_key": "send_error",
                            "Response_value": "Null",
                            "Comparator": "Null",
                            "Expected_value": "Null",
                            "Result": "Fail"
                        }]
                end = time.perf_counter()
                logging.info(f"{name} ({loop+1}/{loops})")
                break
            report_data.extend(combine_headers(yaml_name, name, start, end, loop, results))

        save_to_report(name, REPORT_HEADERS, report_data, 'csv')
        return name, report_data

#  conbine the report headers

@try_wrapper()
def combine_headers(api_name, case_name, start, end, i, results=None):
    rows = []
    for result in results:
        row={
            "Api_name": api_name,
            "Case_name": case_name,
            "Loop": i+1,
            "Run_time": f"{end - start:.3f}s",
            "Expected_key": result.get("Expected_key", "Null"),
            "Response_value": result.get("Response_value", "Null"),
            "Comparator": result.get("Comparator", "Null"),
            "Expected_value": result.get("Expected_value", "Null"),
            "Result": result.get("Result", "Fail"),
            }
        rows.append(row)
    return rows