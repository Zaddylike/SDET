#  internal function
from TestPilot.validator import validate_response
from TestPilot.utils.candy import try_wrapper, lock_with
from TestPilot.report_handler import combine_headers
#  internal parameter
from TestPilot.config import http_client, client_lock
#  external function and paramter
import httpx
import asyncio
import time
import logging
logging = logging.getLogger(__name__)

client = httpx.AsyncClient(timeout=10)

#  add params for shared to another case

def add_shared_params(case_params: dict, shared_data: dict):
    body = case_params.get('body',{})
    for k, v in body.items():
        if isinstance(v, str) and v.startswith('$'):
            var = v[1:]
            if var in shared_data:
                body[k] = shared_data[var]
    return case_params

#  parse response inner field

def get_nested_value(response, field: str):
    #  1. parse every layers key
    current = response
    for key in field.split('.'):
        if isinstance(current, list):
            current = current[0]
        if isinstance(current, dict):
            current = current.get(key)
        else:
            logging.error(f"Unexpected structure at '{key}': {current}")
            return "Unexpected fields"

    return str(current)


#  send the api by http
@lock_with(client_lock)
async def send_http(params: dict, expects: list):
    #  1. parse the case params
    method = params.get('method', 'get').upper()
    url = params.get('url')
    headers = params.get('headers', {})
    timeout = params.get('timeout', 8)
    
    #  2. handle the http api type (get,post...)
    query = params.get('body') if method == 'GET' else None
    json_body = params.get('body') if method != 'GET' else None

    #  3. httpx requests
    response = await http_client.request(method, url, headers=headers, params=query, json=json_body)

    #  4. validation and return result
    if expects:
        result = validate_response(response, expects)

    #  5. save the keep-field from response
    keeps = {}
    keep_field = params.get('keep')
    if keep_field:
        val = get_nested_value(response.json(), keep_field)
        if val is not None:
            keeps[keep_field] = val

    return result, keeps


#  handle send http api

@try_wrapper(log_msg="API handling failed")
async def handle_api(yaml_data):
    #  1. get parameter and add default docker
    yaml_name = yaml_data.get("meta", {}).get('name','')
    cases = yaml_data.get("cases", [])
    shared_data, report_data= {},[]

    #  2. for-loop to handle case    
    for index, case in enumerate(cases):
        params = case.get('params', {})
        expect = case.get('expect', [])
        name = params.get('name', "unknown_case")
        method = params.get('method', 'post')
        loops = int(params.get('loop', 1))
        max_retry = int(params.get('retry', 0))

        #  3. handle loop and send
        for loop in range(loops):
            params = add_shared_params(params, shared_data)
            results, keeps = [], {}
            await asyncio.sleep(1.6)

            #  3-1. for-loop to retry 0...max_retry
            start = time.perf_counter()
            for attempt in range(max_retry+1):
                try:
                    results, keeps = await send_http(params, expect)
                    if all(rst['Result'] for rst in results):
                        logging.info(f"[{name}] Success on attempt {attempt+1}/{max_retry+1}")
                        break
                except httpx.RequestError as httpexc:
                    logging.warning(f"[{name}] Attempt {attempt+1}/{max_retry+1} {httpexc}")
                    result_status, error= False, type(httpexc).__name__
                    results = [{
                        "Expected_key": "neenork_error",
                        "Response_value": f"{error}",
                        "Comparator": "Null",
                        "Expected_value": "Null",
                        "Result": result_status
                        }]
                except Exception as exc:
                    logging.warning(f"[{name}] Unexpected error on attempt {attempt+1}/{max_retry+1} : {type(exc).__name__}:{exc}", exc_info=True)
                    result_status, error = False, type(exc).__name__
                    results = [{
                        "Expected_key": "neenork_error",
                        "Response_value": f"{error}",
                        "Comparator": "Null",
                        "Expected_value": "Null",
                        "Result": result_status
                        }]
                    
                if attempt < max_retry:
                    await asyncio.sleep(0.5 * (2 ** attempt))
            end = time.perf_counter()

            #  4. save the keep parameter to shared_data
            keep_field =  params.get('keep')
            if keeps and keep_field:
                shared_data[keep_field] = keeps[keep_field]  

            #  5. exten the results to report_data
            report_data.extend(combine_headers(yaml_name, name, start, end, loop, results))

    #  6. return reportname, case total testing-data
    # save_to_report(yaml_name, REPORT_HEADERS, report_data, 'csv')
    return yaml_name, report_data