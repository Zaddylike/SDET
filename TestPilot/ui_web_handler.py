#  internal function
from TestPilot.validator import default_result_stamp
from TestPilot.utils.candy import try_wrapper, register_pattern
from TestPilot.report_handler import combine_headers
#  internal parameter
#  external function and paramter
import httpx
import asyncio
import time
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import logging
logging = logging.getLogger(__name__)

action_pattern = {}

@try_wrapper(log_msg="Failed to handling ui_web ")
async def handle_ui_web(yaml_data):
    #  1. get parameter and add default docker
    yaml_name = yaml_data.get("meta", {}).get('name','')
    cases = yaml_data.get("cases", [])
    headless = yaml_data.get("meta", {}).get('headless')
    args = yaml_data.get("meta", {}).get('args')

    #  2. connct the playwright and running case
    async with async_playwright() as playwright:
        browser =  await playwright.chromium.launch(headless=headless, args=args)
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        try:
            for index, case in enumerate(cases):
                function = action_pattern.get(case.get('action'))
                if not function:
                    logging.debug(f"Unsupported action {case.get('action')}")
                    continue
                await function(page, case)
                await asyncio.sleep(0.5)

        except  Exception as e:
            logging.error(f"Unexpected Error: {e}", exc_info=True)

    await context.close()
    await browser.close()

    return yaml_name

@register_pattern(action_pattern, "go")   
async def _go(page, case):
    logging.info(f"go web to : {case.get('target')}")
    await page.goto(case.get('target'))

@register_pattern(action_pattern, "fill")
async def _fill(page, case, timeout=8000):
    selector = case.get("selector")
    value = case.get("value", "")

    if not selector:
        logging.warning("缺少 selector")
        return
    
    selector = page.locator(selector)
    await selector.wait_for(state="visible", timeout=timeout)
    
    # logging.info(f"fill {selector} with {value}")
    await selector.click()
    await selector.fill(str(value))

@register_pattern(action_pattern, "click")
async def _click(page, case, timeout=8000):
    selector = case.get("selector")

    if not selector:
        logging.warning("缺少 selector")
        return
    
    selector = page.locator(selector)
    await selector.wait_for(state="visible", timeout=timeout)
    await asyncio.sleep(1)
    # logging.info(f"click {selector}")
    await selector.click()


@register_pattern(action_pattern, "getvalue")
async def _getvalue(page, case, timeout=8000):
    selector = page.locator(case.get("selector"))

    await selector.wait_for(state="attached", timeout=timeout)

    # page.screenshot(path="record.png")
    value = await selector.text_content()
    logging.info(value)
    return selector.text_content()

@register_pattern(action_pattern, "wait")
async def _wait(page, case, timeout=8000):
    selector = case.get("selector")
    timeout = case.get("value", 8000)
    state = case.get('state', 'visible')

    selector = page.locator(case.get("selector"))
    await selector.wait_for(state=state, timeout=timeout)

