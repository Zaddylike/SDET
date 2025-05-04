#  internal function
from TestPilot.utils.candy import try_wrapper, lock_with
#  internal parameter
from TestPilot.config import DEFAULT_REPORT_DIR
from TestPilot.config import save_lock
#  external function and paramter
import os
import asyncio
import pandas as pd
from datetime import datetime
import logging
logging = logging.getLogger(__name__)


#  conbine the report headers

def combine_headers(current_time, api_name, case_name, start, end, i, results=None):
    return [{
        "Time": current_time,
        "Api_name": api_name,
        "Case_name": case_name,
        "Loop": i+1,
        "Run_time": f"{end - start:.3f}s",
        "Expected_key": result.get("Expected_key", "Null"),
        "Response_value": result.get("Response_value", "Null"),
        "Comparator": result.get("Comparator", "Null"),
        "Expected_value": result.get("Expected_value", "Null"),
        "Result": "Pass" if result.get("Result","Null") else "Fail",
    } for result in results]

#  standard the report_name

def standard_report_name(reportname: str):
    today = datetime.today().strftime("%Y%m%d") #%H%M%S
    return f"{today}_{reportname}_report"

#  save the report

@try_wrapper(log_msg="Failed to save report")
@lock_with(save_lock)
async def save_to_report(report_name: str, headers: list, result_list: list, mode="all"):
    #  1. create reports folder to save report if not exists
    if not os.path.exists(DEFAULT_REPORT_DIR):
        os.makedirs(DEFAULT_REPORT_DIR)
    
    #  2. handle the report path
    report_name = standard_report_name(report_name)
    csv_path = os.path.join(DEFAULT_REPORT_DIR, f"{report_name}.csv")
    xlsx_path = os.path.join(DEFAULT_REPORT_DIR, f"{report_name}.xlsx")

    #  3. assign the save mission for diffenert type
    if mode in ("all", "csv"):
        await asyncio.to_thread(save_as_csv, csv_path, headers, result_list)
    # if mode in ("all", "xlsx"):
    #     await asyncio.to_thread(save_as_xlsx, csv_path, headers, result_list)


#  save report by csv

def save_as_csv(csv_path, headers, result_list):
    new_data = pd.DataFrame(result_list).reindex(columns=headers)
    try:
        if os.path.exists(csv_path):
            old_data = pd.read_csv(csv_path)
            combined = pd.concat([old_data, new_data], ignore_index=True)
        else:
            combined = new_data
        combined.to_csv(csv_path, index=False, encoding="utf-8-sig")

    except Exception as e:
        logging.error(f"Failed to save CSV: {e}", exc_info=True)


#  save report by xlsx

def save_as_xlsx(xlsx_path, headers, result_list):
    new_data = pd.DataFrame(result_list).reindex(columns=headers)
    try:
        if os.path.exists(xlsx_path):
            old_data = pd.read_excel(xlsx_path)
            combined = pd.concat([old_data, new_data], ignore_index=True)
        else:
            combined = new_data
        combined.to_excel(xlsx_path, index=False)
        
    except Exception as e:
        logging.error(f"Failed to save XLSX: {e}", exc_info=True)
