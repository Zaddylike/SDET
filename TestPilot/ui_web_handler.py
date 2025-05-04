#  internal function
from TestPilot.validator import default_result_stamp
from TestPilot.utils.candy import try_wrapper, lock_with
from TestPilot.report_handler import combine_headers
#  internal parameter
#  external function and paramter
import httpx
import asyncio
import time
from playwright.sync_api import sync_playwright
import logging
logging = logging.getLogger(__name__)

target_domain = "https://manager-oms.qosuat.com/admin/lacekaqwkzvnep/index.html"


@try_wrapper(log_msg="Failed to handling ui_web ")
async def handle_ui_web(yaml_data):
    #  1. get parameter and add default docker
    yaml_name = yaml_data.get("meta", {}).get('name','')
    cases = yaml_data.get("cases", [])
    shared_data, report_data= {},[]

    #  2. for-loop to handle case    
    for index, case in enumerate(cases):
        
        params = case.get('params', {})
        expect = case.get('expect', "")
        name = params.get('name', "unknown_case")
        loops = int(params.get('loop', 1))
        max_retry = int(params.get('retry', 0))

        #  3. handle loop and send
        for loop in range(loops):
            params = replace_shread_params(params, shared_data)
            results, keeps = [], {}
            await asyncio.sleep(0.5)

            #  3-1. for-loop to retry 0...max_retry



            #  5. exten the results to report_data
            # report_data.extend(combine_headers(yaml_name, name, start, end, loop, results))

    #  6. return reportname, case total testing-data
    return yaml_name, report_data




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
