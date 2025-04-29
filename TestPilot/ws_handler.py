#  internal function
from TestPilot.report_handler import save_to_report
#  internal parameter
from TestPilot.utils.candy import try_wrapper, register_pattern, wbsk_timer
from TestPilot.utils.tools import msgbody_build
#  external function and paramter
import websockets
import time
import json
import asyncio
import copy
import logging
logging = logging.getLogger(__name__)

SEND_TYPE_LIST={}

def get_nested_value(response: dict, validate_key: str):
    try:
        current = response
        # 解析每層 key
        for key in validate_key.split('.'):
            if isinstance(current, str):
                try:
                    current = json.loads(current)
                except Exception:
                    logging.warning(f"[Warning] Failed to decode str at key {key}")
                    return None
            
            if isinstance(current, dict):
                current = current.get(key)
            else:
                logging.error(f"[Error] Invalid structure at key '{key}': {current}")
                return None

        return current
    except Exception as e:
        logging.error(f"[Error] Failed to parse nested value: {e}", exc_info=True)
        return None

@try_wrapper()
@register_pattern(SEND_TYPE_LIST, 'websocket') 
async def send_api_websocket(params, websocket=None, expects=None):
    results = []
    keeps = {}

    url = params.get('url')
    msg_id = params.get('msg_id')
    msg_body = params.get('msg_body')
    retry = params.get('retry', 0)
    keep = params.get('keep', None)

    ws = websocket or await websockets.connect(url, ping_interval=None, ping_timeout=60)

    msg = msgbody_build(msg_id, msg_body)
    await ws.send(json.dumps(msg))

    tys = 0
    while tys <= retry:
        try:
            resp = await asyncio.wait_for(ws.recv(), timeout=12)
            jsonify_resp = json.loads(resp)

            if jsonify_resp.get('msgId') != msg_id:
                continue
            if not expects:
                return results, keeps
            
            all_pass = True
            for expect in expects:
                validate_key = expect.get('field')
                expected_value = expect.get('value')
                comparator = expect.get('comparator')
                
                actual_value = get_nested_value(jsonify_resp, validate_key)
                result = {
                    "Expected_key": validate_key,
                    "Response_value": actual_value,
                    "Comparator": comparator,
                    "Expected_value": expected_value,
                    "Result": "Pass" if actual_value == expected_value else "Fail"
                }

                if result["Result"] == "Fail":
                    all_pass = False
                    
                results.append(result)

            if keep:
                keep_value = get_nested_value(jsonify_resp, keep)
                if keep_value is not None:
                    keeps[keep] = keep_value
                
            if all_pass:
                return results, keeps

        except Exception as e:
                logging.error(f"[Error] Failed to receive/parse websocket message: {e}", exc_info=True)        
        tys+=1
    return results, keeps

#  add params for shared

def add_shared_params(case_params: dict, shared_data: dict):
    try:
        for k, v in case_params['msg_body'].items():
            if isinstance(v, str) and v.startswith('$'):
                var_name = v[1:]
                if var_name in shared_data:
                    case_params['msg_body'][k] = shared_data[var_name]
        return case_params
    except Exception as e:
        logging.warning(f"Failed to add shared params: {e}", exc_info=True)

#  handle send websocket api


REPORT_HEADERS = [
    "Api_name",
    "Case_name",
    "Loop",
    "Run_time",
    "Response_value",
    "Expected_value",
    "Result"
    ]
# @try_wrapper
async def handle_websocket(yaml_data):
    yaml_name = yaml_data.get("meta", {}).get('name','')
    cases = yaml_data.get("cases", [])
    
    shared_data = {}
    keep_data = {}
    report_data = []

    for case in cases:
        params = case.get('params', {})
        params_copy = copy.deepcopy(params)
        expect = case.get('expect', None)

        name = params.get('name', "unknown_case_name")
        loops = int(params.get('loop', 1))
        keep = params.get('keep')

        # handle loop and send
        for loop in range(loops):
                add_shared_params(params_copy, shared_data)
                if not shared_data.get("websocket"):
                    shared_data["websocket"] = await websockets.connect(params_copy.get("url"), ping_interval=None, ping_timeout=60)

                start = time.perf_counter()
                results, keep_data = await send_api_websocket(params_copy, shared_data["websocket"], expect)
                # logging.info(results)

                end = time.perf_counter()
                logging.info(f"{name} ({loop+1}/{loops})")

                if isinstance(keep_data, dict) and (keep in keep_data):
                        shared_data[keep] = keep_data[keep]

                report_data.extend(combine_headers(yaml_name, name, start, end, loop, results))
        #  reportname, case total testing-data by one
    return name, report_data

#  combine the response data

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
