import logging, time ,json
from playwright.sync_api import sync_playwright
from functools import reduce

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s:%(lineno)d] => %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    )

# target_domain = "https://manager-oms.qosuat.com/admin/lacekaqwkzvnep/index.html"

# def locator_click(page, element, timeout=10000):
#     current_element = page.locator(element)
#     current_element.wait_for(state="visible", timeout=timeout)
#     current_element.click()
#     return current_element

# def locator_getValue(page, element, timeout=10000):
#     text = page.locator(element)
#     text.wait_for(state="attached", timeout=timeout)
#     result_text = text.text_content()
#     print("ok")
#     # page.screenshot(path="record.png")
#     return result_text


# def running_server():
#     playwright = sync_playwright().start()
#     browser = playwright.chromium.launch(headless=False, args=['--start-maximized'])
#     context = browser.new_context(no_viewport=True)
#     page = context.new_page()
#     page.goto(target_domain)

#     return browser, page, context

# def user_login(page):
#     user_name = locator_click(page, "#username", 8000)
#     user_name.fill("qatest0001")
#     user_pwd = locator_click(page, "#password", 8000)
#     user_pwd.fill("396012")
#     locator_click(page, "#login_button", 8000)

# def into_bettingrecord(page):
#     locator_click(page, '.main-sidebar li[name="statistics"]', 8000)
#     locator_click(page, '.main-sidebar li[name="statistics"]  i[name="bet_order_list"]', 8000)
#     page.wait_for_timeout(2000)

# def filter_condition_search(page):
#     user_id = locator_click(page, '.content .seaConditions [name="stype_keyword"]', 8000)
#     user_id.fill("1360789")
#     locator_click(page, '.content .seaArea .btnGroups button[lay-filter="submit_betRecord"]', 8000)
#     page.wait_for_timeout(2000)

# def check_result(page):
#     text = locator_getValue(page, '[lay-table-id="betRecord_list"]  .layui-table-body .layui-table [data-index="0"] [data-field="win"] .layui-table-cell', 8000 )
#     logging.info(text)
#     page.wait_for_timeout(2000)

# def main():
#     browser, page, context = running_server()
#     logging.info("running")
#     user_login(page)
#     into_bettingrecord(page)
#     filter_condition_search(page)
#     check_result(page)
    
#     # ---------------------
#     stopping_server(browser, context)

# def stopping_server(browser, context):
#     context.close()
#     browser.close()

# if __name__ == "__main__":
#     # main()



sample_data = {
        "msgId":201,
        "msgBody": {
            "reason": "login success"
    }
}


data = {
    "response": {
        "body": '{"user": {"email": "watson@example.com"}}'  # ← 字串格式的 JSON
    }
}

real_data = {
    "msgId":201,
    "serverId":"uat","msgBody":"{\"code\":1,\"reason\":\"login success\",\"userId\":\"1368601\",\"comId\":\"JOY\",\"userName\":\"+852 0911223344556\",\"token\":\"1e09f6d7b28ec5c8a546f0c7470f418b\",\"serverTime\":1746322250,\"isCompleteInfo\":true,\"adminRole\":0,\"isFirstLanding\":false,\"level\":9,\"vipLevel\":0,\"isDelete\":false,\"isCanTransfer\":false,\"isFrozen\":false,\"lineGroup\":\"\",\"nekot\":\"7hR/45BKZSPDxitRqCYy1EyfNom1l5pL70ycsgnIzBVDXx4/l/KQZjgcpR4iafxq89NUgElrEr1+fKKPWrsuTC5GgXwWWIN4W4AqMrVF6TXT/GbiQPVNpjNBUu/t5YQqKTk1+GOsXdQR74Q6GAPIqANKcxaUVia6yhSt27pgULGMyA==\"}"
    }

sample_data = {
        "msgId":201,
        "msgBody": {
            "reason": "login success"
    }
}

def _nested_value(data: dict, field: str):
    try:
        def resolver(data, key):
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except Exception:
                    logging.debug(f"[get_nested_value] Failed to decode string at key: {key}")
                    return None
            return data.get(key) if isinstance(data, dict) else None

        return reduce(resolver, field.split("."), data)

    except Exception as e:
        logging.warning(f"[get_nested_value] Failed to extract '{field}': {e}", exc_info=True)
        return None
    
def get_nested_value(real_data, field):
    try:
        def jsonify_value(data,key):
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except Exception:
                    return None
            return data.get(key) if isinstance(data, dict) else None
        return reduce(jsonify_value, field.split("."), real_data)
    except Exception as e:
        logging.error(e)


logging.info(get_nested_value(sample_data,'msgBody.reason'))

# from datetime import datetime
# today_time = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
# logging.info(today_time)