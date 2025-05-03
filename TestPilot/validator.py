#  internal function
from TestPilot.utils.candy import try_wrapper, register_pattern
#  internal parameter
#  external function and paramter
import json
import logging
logging = logging.getLogger(__name__)

COMPARATOR_HANDLE = {}


@register_pattern(COMPARATOR_HANDLE,"equals")
def _equals(actual, expected):
    assert actual == expected, f"Validation failed: expected {expected}, got {actual}"
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

def get_nested_value(response: dict, validate_key: str):
    if validate_key == 'status_code':
        return response.status_code

    if hasattr(response, 'json'):
        current = response.json()
    else:
        current = response
    # logging.info(current)
    # 如果是str, 試著loads一次
    for key in validate_key.split('.'):
        if isinstance(current, list):
            current = current[0]
        if isinstance(current, dict):
            current = current.get(key)
        else:
            logging.error(f"Unexpected structure at '{key}': {current}", exc_info=True)
            return "Unexpected fields"

    return str(current)

@try_wrapper(log_msg="Failed to validate response")
def validate_response(response, expects: list):
    results = []
    for expect in expects:
        validate_key = expect['field']
        validate_value = expect.get('value', "Null")
        comparator = expect['comparator']
        
        comparator_func = COMPARATOR_HANDLE[comparator]
        if not comparator_func:
            logging.debug(f"Unsupported comparator: {comparator}")
            result = "Unsupported comparator"

        try:
            resp_anwser = get_nested_value(response, validate_key)
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
