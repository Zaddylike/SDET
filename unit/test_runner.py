import logging, time
from playwright.sync_api import sync_playwright

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s:%(lineno)d] => %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    )

target_domain = "https://manager-oms.qosuat.com/admin/lacekaqwkzvnep/index.html"

def locator_click(page, element, timeout=10000):
    current_element = page.locator(element)
    current_element.wait_for(state="visible", timeout=timeout)
    current_element.click()
    return current_element

def locator_getValue(page, element, timeout=10000):
    text = page.locator(element)
    text.wait_for(state="attached", timeout=timeout)
    result_text = text.text_content()
    print("ok")
    # page.screenshot(path="record.png")
    return result_text


def running_server():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False, args=['--start-maximized'])
    context = browser.new_context(no_viewport=True)
    page = context.new_page()
    page.goto(target_domain)

    return browser, page, context

def user_login(page):
    user_name = locator_click(page, "#username", 8000)
    user_name.fill("qatest0001")
    user_pwd = locator_click(page, "#password", 8000)
    user_pwd.fill("396012")
    locator_click(page, "#login_button", 8000)

def into_bettingrecord(page):
    locator_click(page, '.main-sidebar li[name="statistics"]', 8000)
    locator_click(page, '.main-sidebar li[name="statistics"]  i[name="bet_order_list"]', 8000)
    page.wait_for_timeout(2000)

def filter_condition_search(page):
    user_id = locator_click(page, '.content .seaConditions [name="stype_keyword"]', 8000)
    user_id.fill("1360789")
    locator_click(page, '.content .seaArea .btnGroups button[lay-filter="submit_betRecord"]', 8000)
    page.wait_for_timeout(2000)

def check_result(page):
    text = locator_getValue(page, '[lay-table-id="betRecord_list"]  .layui-table-body .layui-table [data-index="0"] [data-field="win"] .layui-table-cell', 8000 )
    logging.info(text)
    page.wait_for_timeout(2000)

def main():
    browser, page, context = running_server()
    logging.info("running")
    user_login(page)
    into_bettingrecord(page)
    filter_condition_search(page)
    check_result(page)
    
    # ---------------------
    stopping_server(browser, context)

def stopping_server(browser, context):
    context.close()
    browser.close()

if __name__ == "__main__":
    # main()

    # x = []
    # y = None
    # z = {}
    # o = "o"
    # if x:
    #     logging.info('x')
    # if  y:
    #     logging.info('y')
    # if  z:
    #     logging.info('z')
    # if  o:
    #     logging.info(o)
    # if not x:
    #     logging.info('x')
    # if not y:
    #     logging.info('y')
    # if not z:
    #     logging.info('z')
    # if not o:
    #     logging.info(o)
    import json
    # x = '{"/a/":"/1/"}'
    # jx = json.loads(x)
    # js = json.loads(x)
    # print(js)
    # tys = 0
    # while tys <= 1:
    #     try:
    #         raise
    #     except Exception as e:
    #         logging.info('e')
    #     finally:
    #         logging.info("finally")
    #         tys+=1

    time = 0


    # for i in range(3):
    #     try:
    #         if time==2:
    #             print("OK")
    #         else:
    #             raise
    #     except Exception as e:
    #         time+=1
    #         print("NO")
    # for i in range(1):
    #     logging.info(i)
    # params = {"retry":0}
    # loops = int(params.get('retry', 1))
    # logging.info(loops)
    import time,os
    import pyautogui as pag
    # try:
    #     time.sleep(3)
    #     print("start")
    #     index = 0
    #     while True:
    #         # betting = pag.locateCenterOnScreen('./betting.bmp')
    #         # logging.info(f'{betting}座標')
    #         pag.click()
    #         print(f"click {index}tims")
    #         time.sleep(0.8)
    #         index+=1
    # except KeyboardInterrupt:
    #     logging.info("end")
    BASE_DIR = os.getcwd()
    DEFAULT_CASE_DIR = os.path.join(BASE_DIR, 'tests')

    case_path = os.path.join(DEFAULT_CASE_DIR, 'api_case/game_spin_keno')
    if not os.path.isfile(case_path):
        case_path+=".yaml"
    if os.path.isfile(case_path):
        print(case_path)
