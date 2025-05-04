#  internal function
from TestPilot.report_handler import combine_headers
from TestPilot.utils.candy import try_wrapper, register_pattern, lock_with
from TestPilot.utils.tools import msgbody_build
from TestPilot.validator import validate_response, default_result_stamp
#  internal parameter
from TestPilot.config import ws_lock
#  external function and paramter
import websockets
import time
import json
import asyncio
import logging
logging = logging.getLogger(__name__)

SEND_TYPE_LIST={}

def report_value_stamp (exp_key:str ="-", reps_value:str ="-",comparator:str ="-",exp_value:str ="-"):
    return {
        "Expected_key":   exp_key,
        "Response_value": reps_value,
        "Comparator":     comparator,
        "Expected_value": exp_value,
        "Result":         True
    }

#  add params for shared
def add_shared_params(case_params: dict, shared_data: dict):
    body = case_params.get('body',{})
    for k, v in body.items():
        if isinstance(v, str) and v.startswith('$'):
            var = v[1:]
            if var in shared_data:
                body[k] = shared_data[var]
    return case_params

#  parse response inner dict
def get_nested_value(response: dict, field: str):
    current = response
    # parse layers key
    for key in field.split('.'):
        if isinstance(current, str):
            try:
                current = json.loads(current)
            except Exception:
                logging.warning(f"Unable to JSON-decode string when accessing: {key}")
                return None
        
        if isinstance(current, dict):
            current = current.get(key)
        else:
            logging.error(f"Unexpected structure at '{key}': {current}")
            return "Unexpected fields"

    return current

#  send websocket api
@register_pattern(SEND_TYPE_LIST, 'websocket')
@lock_with(ws_lock)
async def send_ws(params, ws=None, expects=None):
    #  1. build msg body
    msg = msgbody_build(params['msg_id'], params.get('body'))

    #  1-1. ws send
    await ws.send(json.dumps(msg))

    #  2. recv & parse
    response = await asyncio.wait_for(ws.recv(), timeout=params.get('timeout', 6))

    logging.info(f"WEBSOCKET Send WebSocket response: {msg.get("msgId")}")

    #  3. validation and return result
    if expects:
        jsonify_resp= json.loads(response)
        result = validate_response(jsonify_resp, expects)
    else:
        result = default_result_stamp()

    #  4. save the keep-field from response
    keeps = {}
    keep_field = params.get('keep', None)
    if keep_field:
        val = get_nested_value(response.json(), keep_field)
        if val is not None:
            keeps[keep_field] = val

    return result, keeps

#  handle send websocket api
@try_wrapper(log_msg="WebSocket handling failed")
async def handle_websocket(yaml_data):

    #  1. get parameter and add default docker
    yaml_name = yaml_data.get("meta", {}).get('name','')
    cases = yaml_data.get("cases", [])
    shared_data, report_data= {},[]

    #  2. for-loop to handle case
    for index, case in enumerate(cases):
        params = case.get('params', {})
        expect = case.get('expect', [])
        name = params.get('name', "unknown_case")
        loops = int(params.get('loop', 1))
        max_retry = int(params.get('retry', 0))

        #  2-1. if ws not init , connect it
        if "ws" not in shared_data:
            shared_data["ws"] = await websockets.connect(params["url"], ping_interval=None, ping_timeout=60)
        ws = shared_data["ws"]
        logging.info(f'Running case-{index}:{name}')

        #  3. for-loop to handle loop-times, retries-times
        for loop in range(loops):
            add_shared_params(params, shared_data)
            keep_data, results= {},[]
            # 3-1. for-loop to retry 0...max_retry
            start = time.perf_counter()
            for attempt in range(max_retry+1):
                try:
                    results, keep_data = await send_ws(params, ws, expect)

                    if all(rst['Result'] for rst in results):
                        logging.info(f"[{name}] Success on Attempt {attempt+1}/{max_retry+1}")
                        break
                except (OSError, asyncio.TimeoutError, websockets.WebSocketException) as e:
                    logging.warning(f"[{name}] Attempt {attempt+1}/{max_retry+1} : {e}", exc_info=True)
                    results = default_result_stamp(exp_key=f"{type(e).__name__}", resp_value=e, result=False)
                except Exception as exc:
                    logging.warning(f"[{name}] Unexpected Error {attempt+1}/{max_retry+1} : {exc}", exc_info=True)
                    results = default_result_stamp(exp_key="request_error", resp_value=f"{type(exc).__name__}", result=False)

                if attempt < max_retry:
                    await asyncio.sleep(0.5 * (2 ** attempt))
            end = time.perf_counter()

            #  4. save the keep parameter to shared_data
            keep_field = params.get('keep', '')
            if isinstance(keep_data, dict) and (keep_field in keep_data):
                    shared_data[keep_field] = keep_data[keep_field]

            #  5. exten the results to report_data
            report_data.extend(combine_headers(yaml_name, name, start, end, loop, results))

    #  6. return reportname, case total testing-data
    return yaml_name, report_data
