import asyncio
import csv
import json
import logging
from pathlib import Path

import websockets

from TestPilot.utils.candy import try_wrapper
from TestPilot.utils.tools import msgbody_build
from TestPilot.config import REPORT_HEADERS
from TestPilot.report_handler import save_to_report

logger = logging.getLogger(__name__)


_DATA_DIR = Path(__file__).parents[1] / "data"
ACCOUNTS_CSV = _DATA_DIR / "accounts.csv"
ACCOUNT_LOCK = asyncio.Lock()
AVAILABLE_ACCOUNTS = []

async def load_accounts():
    global AVAILABLE_ACCOUNTS
    if not AVAILABLE_ACCOUNTS:
        with ACCOUNTS_CSV.open(newline="", encoding="utf-8") as f:
            AVAILABLE_ACCOUNTS = list(csv.reader(f))

async def allocate_accounts(count: int):
    await load_accounts()
    async with ACCOUNT_LOCK:
        if count > len(AVAILABLE_ACCOUNTS):
            raise RuntimeError(f"Requested {count} robots but only {len(AVAILABLE_ACCOUNTS)} accounts available.")
        selected = AVAILABLE_ACCOUNTS[:count]
        del AVAILABLE_ACCOUNTS[:count]
        return selected

# 
async def send_ws_retry(ws, msg_id: int, body: dict,
    max_retry: int, timeout: float = 6.0) -> dict:
    last_exc = None
    for attempt in range(max_retry + 1):
        try:
            payload = msgbody_build(msg_id, body)
            await ws.send(json.dumps(payload))
            logging.info(payload)
            raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
            data = json.loads(raw)
            if data.get("msgId") == msg_id:
                return data
            raise ValueError(f"Mismatched msgId: expected {msg_id}, got {data.get('msgId')}")
        except Exception as exc:
            last_exc = exc
            logger.warning(f"[msgId={msg_id}] Attempt {attempt+1}/{max_retry+1} failed: {type(exc).__name__}: {exc}")
            if attempt < max_retry:
                await asyncio.sleep(0.5 * (2 ** attempt))
    logger.error(f"[msgId={msg_id}] All {max_retry+1} attempts failed.")
    raise last_exc

# 
async def run_single_robot(yaml_data: dict, credentials: list):
    cases     = yaml_data.get("cases", [])
    play_mode = yaml_data.get('robot').get("play", False)
    shared    = {}
    user_name, password = credentials
    async with websockets.connect('wss://web.qosuat.com/ws/', ping_interval=None, ping_timeout=60) as ws:
        # 
        logging.info(play_mode)
        for case in cases:
            params = case.get("params", {})
            expects = case.get("expect", [])
            name    = params.get("name", "<unnamed>")
            msg_id  = int(params.get("msg_id", 0))
            body    = dict(params.get("body", {}))
            loops   = int(params.get("loop", 1))
            retries = int(params.get("retry", 0))
            keep    = params.get("keep")
            logging.info(msg_id)
            if msg_id == 201:
                body.update({"userName": user_name, "password": password})

            for i in range(loops):
                try:
                    data = await send_ws_retry(ws, msg_id, body, retries)
                    logging.info(f"{data}")
                    logger.info(f"[{name}] Success on loop {i+1}")
                    if keep and (val := data.get(keep)) is not None:
                        shared[keep] = val
                except Exception as exc:
                    logger.error(f"[{name}] Loop {i+1} failed: {type(exc).__name__}: {exc}")
                    continue

        # 
        if play_mode and (user_id := shared.get("user_id")):
            await robot_play(ws, user_id, shared)

    return shared

#  handle robot
@try_wrapper("Robot handler encountered a fatal error")
async def handle_robot(yaml_data: dict):

    # 
    count = int(yaml_data.get("robot",{}).get("gangbang", 1))
    accounts = await allocate_accounts(count)
    logging.info(accounts)
    # 
    tasks = [run_single_robot(yaml_data, cred) for cred in accounts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # 
    report_rows = []
    for idx, res in enumerate(results, start=1):
        if isinstance(res, Exception):
            report_rows.append({
                "RobotIndex": idx,
                "Status": f"Error: {type(res).__name__}",
            })
        else:
            report_rows.append({
                "RobotIndex": idx,
                "Status": "Completed",
            })
    # await save_to_report("robot_fleet", ["RobotIndex", "Status"], report_rows, mode="csv")

    return {"robots_launched": count, "results": results}


def convert_card_type(type_number):
    card_types = {
        1: "High Card",
        2: "One Pair",
        3: "Two Pair",
        4: "Three of a Kind",
        5: "Straight",
        6: "Flush",
        7: "Full House",
        8: "Four of a Kind",
        9: "Straight Flush",
        10: "Royal Flush"
    }
    return card_types.get(type_number, "Unknown")
MSG_Handlerlist = {}
notplayAction_Handler = {}
user_points = {}
# 將yaml的格式轉換成發送web socket api的format

def msgbody_build(msg_id: int, msg_body: str) -> str:
    return {
        "msgId": msg_id,
        "msgbody": json.dumps(msg_body)
    }

# 執行websocket的api發送，分為單次跟Retry

async def sendmsg_handler(websocket, msg_id: int, msg_body: str, msg_expect=None, retry=True, timeout=20):

        msg = msgbody_build(msg_id, msg_body)
        await websocket.send(json.dumps(msg))
        tys = 0
        while tys <= retry:
            try:
                reps = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                jsonify_Reps = json.loads(reps)

                reps_Msgid = jsonify_Reps.get("msgId", 0)
                reps_Msgbody = json.loads(jsonify_Reps.get("msgBody", "{}"))

                if msg_expect == None or (reps_Msgid == msg_expect[0] and msg_expect[1] in reps_Msgbody.get('reason', '')):
                    logging.info(f"[RECV] MsgId: {reps_Msgid} {reps_Msgbody['reason']}")
                    return True, reps_Msgbody
                if not retry:
                    return False, None
            except Exception as e:
                logging.error(f"[Error] Failed to receive/parse websocket message: {e}", exc_info=True)        
                tys+=1
            # await asyncio.sleep(0.1)

# msg回傳底牌轉換成數字，需優畫

def convert_card_readable(card_numbers):
    def filter_Cardtype(num):
        # 方塊 2-A: 2-14
        if 2 <= num <= 14:
            rank = num if num <= 10 else {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}[num]
            return '♦', str(rank)
        # 梅花 2-A: 18-30
        elif 18 <= num <= 30:
            rank = num - 16 if num <= 26 else {27: 'J', 28: 'Q', 29: 'K', 30: 'A'}[num]
            return '♣', str(rank)
        # 紅心 2-A: 34-46
        elif 34 <= num <= 46:
            rank = num - 32 if num <= 42 else {43: 'J', 44: 'Q', 45: 'K', 46: 'A'}[num]
            return '♥', str(rank)
        # 黑桃 2-A: 50-62
        elif 50 <= num <= 62:
            rank = num - 48 if num <= 58 else {59: 'J', 60: 'Q', 61: 'K', 62: 'A'}[num]
            return '♠', str(rank)
        else:
            return '?', str(num)
            
    handcard_Log = []
    handcard_Suits = []
    handcard_Points = []
    handcard_Changemap = {'A':14, 'K':13, 'Q':12, 'J':11}
    try:
        for card in card_numbers:
            suit, point = filter_Cardtype(card)
            handcard_Suits.append(suit)
            if point in handcard_Changemap:
                handcard_Points.append(handcard_Changemap[point])
            else:
                handcard_Points.append(int(point))
            handcard_Log.append(f"{suit} {point}")
        sorted_Cards = sorted(zip(handcard_Points, handcard_Log, handcard_Suits), reverse = True)
        handcard_Points, handcard_Log, handcard_Suits = zip(*sorted_Cards)
        return list(handcard_Points), list(handcard_Log), list(handcard_Suits)
    except Exception as e:
        logging.info(f"[ERROR] 解析底牌: {e}")
        return [], [], []

# 機器人操作決策， 未來會想訓練model來判斷，目前就先簡單判斷

async def decide_robot_action(points, msg_body):
    # 每次操作的id流水
    cmd_id = msg_body.get('commandId', 0)
    # 跟注所需金額
    call_count = msg_body.get("callCount", 0)
    # 加注所需金額
    raise_count = msg_body.get("raisCount", 0)
    # 還沒調查
    min_raise = msg_body.get("minRaise", 2)
    # 還沒調查
    min_call = msg_body.get("minCall", 2)
    
    # action rule => {1:"弃牌", 2:"让牌", 3:"跟注", 4:"加注", 5:"全下", 6:"延时"}
    # AK, AQ, AJ, A10, KQ, KJ, K10, QJ, Q10, J10 or AA, KK, QQ, JJ, 1010
    if (points[0]>=10 and points[1]>=10) or (points[0]==points[1] and points[0] >= 10):
        action_Type = 4

    # 55, 66, 77, 88, 99
    elif (points[0]==points[1]) and (5 <= points[0] < 10):
        action_Type = 3

    # 44, 33, 22
    elif points[0]==points[1] and 2 <= points[0] < 5:
        action_Type = 3

    # 98, 87, 76, 65, 54, 43, 32 
    elif points[0]<10 and (points[0]-points[1]) < 1:
        action_Type = 2
    # 普通偏弱排型
    elif points[0]<10 and (points[0]-points[1]) < 2:
        action_Type = 2
    # 弱到直接棄牌下一局
    else:
        action_Type = 1
    

    if raise_count > 5 and action_Type == 4:
        action_Type = 3

    score = 0
    if action_Type == 3:
        score = min_call
    elif action_Type == 4:
        score = min_raise

    return action_Type, score, cmd_id

# match&case維護成本過高， 參考decorator寫法

def register_handler(msg_id):
    def wrapper(func):
        MSG_Handlerlist[msg_id] = func
        return func
    return wrapper

# 手牌資訊&心跳
@register_handler(913)
async def handle_913(websocket, msg_body, user_id, shared_data):
    try:
        if isinstance(msg_body, list) and len(msg_body) > 0:
            cards = msg_body[0].get('cards', [])
            if cards:
                points, card_readable, suits = convert_card_readable(cards)
                user_points[user_id] = points
                logging.info(f"[Observe] Robot:{user_id},的手牌是: {card_readable}")
        else:
            raise Exception(f"[ERROR] 玩家沒拿到2張牌阿!! ")
    except Exception as e:
        logging.warning(f"[ERROR] MsgId 913: {e}", exc_info=True)
        # send heart-beat
    try:
        heartbeat_request = {
            "msgId": 202,
            "msgBody": json.dumps({})
            }
        await websocket.send(json.dumps(heartbeat_request))
    except Exception as e:
        logging.warning(f"[ERROR] MsgId 202: {e}", exc_info=True)
    await asyncio.sleep(0.1)
# NLH, MTT 手牌操作
@register_handler(217)
async def handle_217(websocket, msg_body, user_id, shared_data):
    try:
        #牌力邏輯
        #1003093 1003091 1003088 1003082
        if msg_body.get('userId') == user_id:
            points = user_points.get(user_id)
            logging.info(points)
            if not points or len(points) < 2:
                logging.warning(f"[Observe] Robot:{user_id} 還沒到拿牌階段， 跳過。")
                return

            actionType, score, cmd_id = await decide_robot_action(points, msg_body)
            action_Map = {1:"弃牌", 2:"让牌", 3:"跟注", 4:"加注", 5:"全下", 6:"延时"}
            action = {
                "gameOpType": actionType,
                "score": score,
                "commandId": cmd_id
            }
            #Json -> dict
            msg = msgbody_build(218, action)
            sleep_time = random.uniform(1, 2)  # 隨機等待1-3秒
            await asyncio.sleep(sleep_time)
            actName = action_Map.get(action["gameOpType"], "無動作")
            logging.info(f"[Observe] Robot:{user_id} 的行動: {actName}")

            await websocket.send(json.dumps(msg))
    except Exception as e:
        logging.warning(f"[ERROR] MsgId 217: {e}", exc_info=True)
# 公共牌
@register_handler(219)
async def handle_219(websocket, msg_body, user_id, shared_data):
    try:
        center_cards = msg_body.get('centerCard', [])
        if center_cards:
            community_cards = convert_card_readable(center_cards)
            logging.info(f"[Observe] 公共牌: {community_cards}")
    except Exception as e:
        logging.warning(f"[ERROR] MsgId 219: {e}", exc_info=True)
# 
@register_handler(221)
async def handle_221(websocket, msg_body, user_id, shared_data):
    try:
        winners = msg_body.get('winners', [])
        for winner in winners:
            win_userid = winner.get('userId')
            win_amount = winner.get('winScore', 0)
            logging.info(f"[Observe] Robot:{win_userid} 贏得 {win_amount} 籌碼")
    except Exception as e:
        logging.warning(f"[ERROR] MsgId 221: {e}", exc_info=True)
#
@register_handler(216)
async def handle_216(websocket, msg_body, user_id, shared_data):
    try:
        # 公共牌信息
        community_cards = msg_body.get('publicCards', [])
        if community_cards:
            logging.info(f"[Observe] 公共牌: {community_cards}")
        
        # 當前池底
        pot = msg_body.get('pot', 0)
        if pot:
            logging.info(f"[Observe] 當前池底: {pot}")
    except Exception as e:
        logging.warning(f"[ERROR] MsgId 216: {e}", exc_info=True)
#
@register_handler(220)
async def handle_220(websocket, msg_body, user_id, shared_data):
    try:
        winners = msg_body.get('winners', [])
        for winner in winners:
            player_id = winner.get('userId')
            win_amount = winner.get('winMoney', 0)
            cards = winner.get('cards', [])
            card_type = winner.get('cardType', '')
            logging.info(f"[Observe] Robot:{player_id} 贏得 {win_amount}，手牌: {cards}，牌型: {card_type}")
    except Exception as e:
        logging.warning(f"[ERROR] MsgId 220: {e}", exc_info=True)
#
@register_handler(218)
async def handle_218(websocket, msg_body, user_id, shared_data):
    try:
        player_id = msg_body.get('userId')
        action = msg_body.get('action', {})
        bet_amount = action.get('bet', 0)
        if bet_amount:
            logging.info(f"[Observe] Robot:{player_id} 下注金額: {bet_amount}")
    except Exception as e:
        logging.warning(f"[ERROR] MsgId 218: {e}", exc_info=True)
#Rebuy
@register_handler(356)
async def handle_356(websocket, msg_body, user_id, shared_data):
    try:
        is_canbuy = msg_body.get('isCanRebuy')
        if is_canbuy:
            rebuy_id = 341
            rebuy_body = {"gameType": 908,"matchId": 3038}
            repsStatus, reps_msgBody = await sendmsg_handler(websocket, rebuy_id, rebuy_body, [341, "报名成功"], retry=True)
            if repsStatus:
                logging.info(f"操作[MTT_Re-Buy]成功")
    except Exception as e:
        logging.warning(f"[ERROR] MsgId 218: {e}", exc_info=True)
#BJ下注
@register_handler(2122)
async def handle_2122(websocket, msg_body, user_id, shared_data):
    try:
        logging.info(msg_body)
        game_id = shared_data['game_id']
        msgid_bet = 2135
        msgbody_bet = {"gameID": game_id,"amount": 100}
        repsStatus, reps_msgBody = await sendmsg_handler(websocket, msgid_bet, msgbody_bet, [2135, "Success"], False)
        logging.info(f"Player {user_id} 操作[下注]成功")
        msgid_bet = 2121
        msgbody_bet = {"gameID": game_id}
        repsStatus, reps_msgBody = await sendmsg_handler(websocket, msgid_bet, msgbody_bet, [2121, "Success"], False)
        if repsStatus:
            logging.info(f"[Observe] Robot:{user_id} 操作[確認下注]成功")
        else:
            logging.warning(f"[Observe] Robot:{user_id} 操作[確認下注]失敗")
            
    except Exception as e:
        logging.warning(f"[ERROR] MsgId 2135: {e}", exc_info=True)


# 工廠化所有機器人的各種操作函式，日後好維護

async def robot_play(websocket, user_id, shared_data):
    while True:
        try:
            reps = await websocket.recv()
            jsonify_Reps = json.loads(reps)
            msg_id = jsonify_Reps.get("msgId")
            msg_body = json.loads(jsonify_Reps.get('msgBody', '{}'))
        except Exception as e:
            logging.error(f"機器人解析RECV時遇到ERROR:{e}")
            raise Exception(e)
        handler_Action = MSG_Handlerlist.get(msg_id, None)
        if handler_Action:
            await handler_Action(websocket, msg_body, user_id, shared_data)
        else:
            logging.debug(f"[DEBUG] 未處理過的 MsgId: {msg_id}")

#  add params for shared

def add_shared_params(case_params: dict, shared_data: dict):
    try:
        for k, v in case_params['body'].items():
            if isinstance(v, str) and v.startswith('$'):
                var_name = v[1:]
                if var_name in shared_data:
                    case_params['body'][k] = shared_data[var_name]
                    # logging.info(f"[共享參數]:{shared_data}")
        return case_params
    except Exception as e:
        logging.warning(f"[WARNING] 新增共享參數ERROR:{e}")

def register_NotPlay_handler(msg_id):
    def wrapper(func):
        notplayAction_Handler[msg_id] = func
        return func
    return wrapper

@register_NotPlay_handler(201)
async def handle_201(websocket, body, expect, retry, shared_data):
    state, reps = await sendmsg_handler(websocket, 201, body, expect, retry)
    if state:
        shared_data["user_id"] = reps.get("userId")
        logging.info(f"{shared_data["user_id"]} 已成功登入!!")
    return state, reps

@register_NotPlay_handler(208)
async def handle_208(websocket, body, expect, retry, shared_data):
    for pos in range(8):
        body["pos"] = pos if "pos" in body else pos
        logging.info(f" {shared_data["user_id"]} 嘗試坐下 {pos}")
        state, reps = await sendmsg_handler(websocket, 208, body, expect, retry)

        if state and reps.get("reason") == "success！":
            logging.info(f" {shared_data['user_id']} [入座成功] MsgId: {208}, Pos: {pos}")
            break
        await asyncio.sleep(0.3)

    return state, reps

@register_NotPlay_handler(2102)
async def handle_2102(websocket, body, expect, retry, shared_data):
    for pos in range(8):
        body["pos"] = pos if "pos" in body else pos
        logging.info(f" {shared_data["user_id"]} 嘗試坐下 {pos}")
        state, reps = await sendmsg_handler(websocket, 2102, body, expect, retry)

        if state and reps.get("reason") == "success！":
            logging.info(f" {shared_data['user_id']} [入座成功] MsgId: {2102}, Pos: {pos}")
            break
        await asyncio.sleep(0.3)

    return state, reps

