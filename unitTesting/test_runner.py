import logging
import json
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s:%(lineno)d] => %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    )

li = ["1","2","3"]

for i, v in enumerate(li):
    print(i,v)



[ 
('demo_send', [{'Api_name': 'send_get_api', 'Case_name': 'demo_send', 'Loop': 1, 'Run_time': '0.440s', 'Expected_key': 'status_code', 'Response_value': 200, 'Comparator': 'equals', 'Expected_value': 200, 'Result': 'Pass'}]),
('free_spin', [{'Api_name': 'sample_send_post', 'Case_name': 'free_spin', 'Loop': 1, 'Run_time': '0.817s', 'Expected_key': 'status_code', 'Response_value': 200, 'Comparator': 'equals', 'Expected_value': 200, 'Result': 'Pass'}, {'Api_name': 'sample_send_post', 'Case_name': 'free_spin', 'Loop': 1, 'Run_time': '0.817s', 'Expected_key': 'data.awards.award_type', 'Response_value': 'COIN', 'Comparator': 'equals', 'Expected_value': 'COIN', 'Result': 'Pass'}])]

# def get_nested_value(response: dict, validate_key: str):
#     try:
#         current = response
#         for key in validate_key.split('.'):
#             logging.info(f"key:{key}")
#             if isinstance(current, str):
#                 try:
#                     current = json.loads(current)
#                 except Exception:
#                     logging.warning(f"[Warning] Failed to decode str at key {key}")
#                     return None
#             # logging.info(f"current:{current}")
#             if isinstance(current, dict):
#                 current = current.get(key)
#                 # logging.info(f"current:{current}")
#             else:
#                 logging.error(f"[Error] Invalid structure at key '{key}': {current}")
#                 return None
#         # logging.info(current)
#         # logging.info(validate_key)
#         return current
#     except Exception as e:
#         logging.error(f"[Error] Failed to parse nested value: {e}", exc_info=True)
#         return None


# x = {"msgId":201,"serverId":"uat","msgBody":"{\"code\":1,\"reason\":\"登陆成功\",\"userId\":\"1368601\",\"comId\":\"JOY\",\"userName\":\"+852 0911223344556\",\"token\":\"1e09f6d7b28ec5c8a546f0c7470f418b\",\"serverTime\":1745862005,\"isCompleteInfo\":true,\"adminRole\":0,\"isFirstLanding\":false,\"level\":9,\"vipLevel\":0,\"isDelete\":false,\"isCanTransfer\":false,\"isFrozen\":false,\"lineGroup\":\"\",\"nekot\":\"nNegb6s/0Nj1k3VEw5LchFC+ZrXTBVTvMi8zJjttExwnS35rszNzEanow2bsi/Yr829Taugqj6zOBRKtFDG6dQqI8lj4PQIKA369cWie+4GG9e4MWccCBnrhbe4rwNWBSHlaWEw6NP4s+m6puNfMdBS18TIdO0QVj2pIPI9iye7dWg==\"}"}
# result_id = get_nested_value(x,'msgId')
# result = get_nested_value(x,'msgBody.reason')
# logging.info(result_id)
# logging.info(result)


# import requests
# url = "https://wap.qosuat.com/api/spin/spin_wheel"
# headers = {"Content-Type": "application/json"}
# body = {"userId": "1368601","token": "1e09f6d7b28ec5c8a546f0c7470f418b"}
# resp = requests.post(url, headers=headers, json=body)
# resp_status = resp.status_code


#  1
# answser_name = 'status_code'
# answser_anwser = 200
#  2
# answser_name = 'data.awards.award_type'
# answser_anwser = 'COIN'

# jsonify_resp = resp.json()
# resp_anwser = get_nested_value(resp,answser_name)
# print(type(resp))
# assert answser_anwser == resp_anwser, f"錯誤啦 {resp_anwser}"
# print("答對啦")

