#  internal function
from TestPilot.validator import validate_response
from TestPilot.utils.candy import try_wrapper, register_pattern
#  internal parameter
#  external function and paramter
import requests
import time
import logging
logging = logging.getLogger(__name__)

API_TYPE_HANDLE ={}

#  send get api

@try_wrapper
@register_pattern(API_TYPE_HANDLE, 'get')
def send_api_get(params, expect):
    url = params.get('url', "unknown_url")
    headers = params.get('headers', {})
    body = params.get('body', {})

    response = requests.get(url, headers=headers, params=body, timeout=8)
    return validate_response(response, expect)

#  send post api

@try_wrapper
@register_pattern(API_TYPE_HANDLE, 'post')
def send_api_post(params, expect):
    url = params.get('url', "unknown_url")
    headers = params.get('headers', {})
    body = params.get('body', {})

    response = requests.post(url, headers=headers, json=body, timeout=8)
    return validate_response(response, expect)

#  handle send api type

@try_wrapper
def handle_api(yaml_data):
    yaml_name = yaml_data.get("meta", {}).get('name',"")
    cases = yaml_data.get("cases", [])
    report_data = []

    for case in cases:
        params = case.get('params', {})
        expect = case.get('expect', [])

        name = params.get('name', "unknown_case_name")
        method = params.get('method', 'unknown_method')
        loop = int(params.get('loop', 1))
        
        # handle loop and send

        for i in range(loop):
            start = time.perf_counter()
            send_api_function = API_TYPE_HANDLE.get(method, None)
            if send_api_function:
                # try:
                results = send_api_function(params, expect)
            end = time.perf_counter()
            logging.info(f"[Observe] 第{i+1}/{loop}次循環發送")

            report_data = combine_headers(yaml_name, name, start, end, i, results)
        return name, report_data

#  conbine the report headers

@try_wrapper
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