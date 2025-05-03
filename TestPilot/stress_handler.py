#  internal  function
from TestPilot.utils.candy import try_wrapper
#  internal parameter
#  external function and parameter
from TestPilot.utils.candy import try_wrapper
import asyncio
import aiohttp
import time

@try_wrapper(log_msg="Stress test failed")
async def handle_stress(yaml_data):
    params = yaml_data["cases"][0]["params"]
    url = params["url"]
    concurrency = params.get("concurrency", 10)
    duration = params.get("duration", 10)
    rate = params.get("rate", 1)

    sem = asyncio.Semaphore(concurrency)
    end_time = time.time() + duration

    async def worker():
        async with sem:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(url) as resp:
                    await resp.text()

    tasks = []
    while time.time() < end_time:
        tasks.append(asyncio.create_task(worker()))
        await asyncio.sleep(1/rate)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    
    return results
