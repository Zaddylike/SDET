import base64, json, logging

#  encode password

def encode_pwd(user_id: str, password: str):
    validate_code = "qazwsx"
    encodedPas = base64.b64encode(password.encode()).decode()
    secondEncode = base64.b64encode((encodedPas + user_id).encode()).decode()
    cryptoPwd = base64.b64encode((secondEncode + validate_code).encode()).decode()
    return cryptoPwd

#  combined the message body

def msgbody_build(msg_id: int, msg_body: str)-> dict:
    try:
        str_body = json.dumps(msg_body)
    except Exception as e:
        logging.debug(f"[DEBUG] 傳送參數轉換JSON錯誤: {e}")
        str_body = str(msg_body)
    msg = {"msgId": msg_id,"msgBody": str_body}
    return msg

# def msgbody_build(msg_id: int, msg_body: str) -> str:
#     return {
#         "msgId": msg_id,
#         "msgbody": json.dumps(msg_body)
#     }