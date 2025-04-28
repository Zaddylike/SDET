
def get_nested_value(response: dict, field_name: str):
    if field_name == 'status_code':
        print(f"回傳 {response.status_code}")
        return response.status_code
    

    resp_anwser = response.json()
    print(f'resp_answer {response.json()}')
    resp_key = field_name.split('.')

    for key in resp_key:
        if isinstance(resp_anwser, dict):
            resp_anwser = resp_anwser.get(key)
        else:
            raise KeyError(f"Response type wrong {resp_anwser}")
    return resp_anwser

import requests
url = "https://wap.qosuat.com/api/spin/spin_wheel"
headers = {"Content-Type": "application/json"}
body = {"userId": "1368601","token": "1e09f6d7b28ec5c8a546f0c7470f418b"}
resp = requests.post(url, headers=headers, json=body)
resp_status = resp.status_code


#  1
# answser_name = 'status_code'
# answser_anwser = 200
#  2
answser_name = 'data.awards.award_type'
answser_anwser = 'COIN'

jsonify_resp = resp.json()
resp_anwser = get_nested_value(resp,answser_name)
print(type(resp))
assert answser_anwser == resp_anwser, f"錯誤啦 {resp_anwser}"
print("答對啦")