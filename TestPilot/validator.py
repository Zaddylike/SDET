#  internal function
from TestPilot.utils.candy import try_wrapper, register_pattern
#  internal parameter
#  external function and paramter
import json
import logging
logging = logging.getLogger(__name__)

COMPARATOR_HANDLE = {}

@try_wrapper()
@register_pattern(COMPARATOR_HANDLE,"equals")
def _equals(actual, expected):
    assert actual == expected, f"Validation failed: expected {expected}, got {actual}"
    return "Pass"

@try_wrapper()
@register_pattern(COMPARATOR_HANDLE,"not_equals")
def _not_equals(actual, expected):
    assert actual != expected, f"Validation failed: should not be {expected}"
    return "Pass"

@try_wrapper()
@register_pattern(COMPARATOR_HANDLE,"exists")
def _exists(actual, expected=None):
    assert actual is not None, f"Validation failed: field does not exist"
    return "Pass"

@try_wrapper()
@register_pattern(COMPARATOR_HANDLE,"not_exists")
def _not_exists(actual, expected=None):
    assert actual is None, f"Validation failed: field should not exist"
    return "Pass"

@try_wrapper()
@register_pattern(COMPARATOR_HANDLE,"contains")
def _contains(actual, expected):
    assert expected in actual, f"Validation failed: {expected} not found in {actual}"
    return "Pass"

@try_wrapper()
@register_pattern(COMPARATOR_HANDLE,"not_contains")
def _not_contains(actual, expected):
    assert expected not in actual, f"Validation failed: {expected} should not be in {actual}"
    return "Pass"

@try_wrapper()
def get_nested_value(response: dict, validate_key: str):
    try:
        if validate_key == 'status_code':
            return response.status_code

        if hasattr(response, 'json'):
            resp_content = response.json()
        else:
            resp_content = response

        # 如果是str, 試著loads一次
        if isinstance(resp_content, str):
            try:
                resp_content = json.loads(resp_content)
            except Exception:
                return None

        keys = validate_key.split('.')
        for key in keys:
            if isinstance(resp_content, dict):
                resp_content = resp_content.get(key)
            else:
                raise KeyError(f"Response type wrong {resp_content}")

        return resp_content
    except Exception as e:
        logging.error(f"[Error] Failed to parse nested value: {e}")
        return None

@try_wrapper()
def validate_response(response, expects: list):
    results = []
    for expect in expects:
        validate_key = expect['field']
        validate_value = expect['value']
        comparator = expect['comparator']
        
        comparator_func = COMPARATOR_HANDLE[comparator]
        if not comparator_func:
            logging.debug(f"Unsupported comparator: {comparator}")
            result = "Unsupported comparator"

        resp_anwser = get_nested_value(response, validate_key)
        result = comparator_func(resp_anwser, validate_value)

        try:
            resp_anwser = get_nested_value(response, validate_key)
            result = comparator_func(resp_anwser, validate_value)
        except Exception as e:
            result = "Fail"
            logging.error(f"Validate response error: {e}", exc_info=True)

        results.append({
            "Expected_key": validate_key,
            "Response_value": resp_anwser,
            "Comparator": comparator,
            "Expected_value": validate_value,
            "Result": result
            })
    return results
