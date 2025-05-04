#  internal function
from TestPilot.utils.candy import try_wrapper, register_pattern
#  internal parameter
#  external function and paramter
import json
import logging
import httpx
from functools import reduce
logging = logging.getLogger(__name__)

COMPARATOR_HANDLE = {}


@register_pattern(COMPARATOR_HANDLE,"equals")
def _equals(actual, expected):
    assert actual == expected, f"Validation failed: expected [ {expected} ], got [ {actual} ]"
    return "Pass"

@register_pattern(COMPARATOR_HANDLE,"not_equals")
def _not_equals(actual, expected):
    assert actual != expected, f"Validation failed: should not be {expected}"
    return "Pass"

@register_pattern(COMPARATOR_HANDLE,"exists")
def _exists(actual, expected=None):
    assert actual is not None, f"Validation failed: field does not exist"
    return "Pass"

@register_pattern(COMPARATOR_HANDLE,"not_exists")
def _not_exists(actual, expected=None):
    assert actual is None, f"Validation failed: field should not exist"
    return "Pass"

@register_pattern(COMPARATOR_HANDLE,"contains")
def _contains(actual, expected):
    assert expected in actual, f"Validation failed: {expected} not found in {actual}"
    return "Pass"

@register_pattern(COMPARATOR_HANDLE,"not_contains")
def _not_contains(actual, expected):
    assert expected not in actual, f"Validation failed: {expected} should not be in {actual}"
    return "Pass"

@register_pattern(COMPARATOR_HANDLE,"read")
def _read(actual, expected):
    return "Pass"

def get_nested_value(response, validate_key: str):
    if isinstance(response, httpx.Response):
        current = response.json()
    else:
        current = response
        
    def jsonify_value(current,key):
        if isinstance(current, str):
            try:
                current = json.loads(current)
            except Exception:
                return None
        return current.get(key) if isinstance(current, dict) else None
    
    return reduce(jsonify_value, validate_key.split('.'), current)

def default_result_stamp (exp_key:str ="Null", resp_value:str ="Null",comparator:str ="Null",exp_value:str ="Null",result:bool=True):
    return [{
        "Expected_key":   exp_key,
        "Response_value": resp_value,
        "Comparator":     comparator,
        "Expected_value": exp_value,
        "Result":         result
    }]


@try_wrapper(log_msg="Failed to validate response")
def validate_response(response, expects: list):
    results = []
    for expect in expects:
        validate_key = expect.get('field')
        validate_value = expect.get('value', "Null")
        comparator = expect.get('comparator')

        comparator_func = COMPARATOR_HANDLE[comparator]
        if not comparator_func:
            logging.debug(f"Unsupported comparator: {comparator}")
            result = "Unsupported comparator"
        try:
            # logging.info(response)
            if validate_key == "status_code":
                resp_anwser = response.status_code
            else:
                resp_anwser = get_nested_value(response, validate_key)
            # logging.info(resp_anwser)
            result = comparator_func(resp_anwser, validate_value)
        except Exception as e:
            result = False
            logging.error(f"Validate response error: {e}", exc_info=True)

        results.append({
            "Expected_key": validate_key,
            "Response_value": resp_anwser,
            "Comparator": comparator,
            "Expected_value": validate_value,
            "Result": result
            })
    return results
