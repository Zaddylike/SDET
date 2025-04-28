#  internal function
#  internal parameter
from TestPilot.config import DEFAULT_REPORT_DIR
from TestPilot.utils.candy import try_wrapper
#  external function and paramter
import os
from datetime import datetime
import pandas as pd
import logging
logging = logging.getLogger(__name__)

#  

@try_wrapper
def standard_report_name(reportname: str):
    today = datetime.today().strftime("%Y%m%d") #%H%M%S
    return f"{today}_{reportname}_report"

#  

@try_wrapper
def save_to_report(report_name: str, headers: list, result_list: list, mode="all"):

    #  create reports folder to save report
    
    if not os.path.exists(DEFAULT_REPORT_DIR):
        os.makedirs(DEFAULT_REPORT_DIR)
    
    #  spec the report name

    report_name = standard_report_name(report_name)
    try:
        csv_path = os.path.join(DEFAULT_REPORT_DIR, f"{report_name}.csv")
        xlsx_path = os.path.join(DEFAULT_REPORT_DIR, f"{report_name}.xlsx")
    except Exception as e:
        logging.error(f"Failed to parse report path: {e}", exc_info=True)

    if mode in ("all", "csv"):
        save_as_csv(csv_path, headers, result_list)
    if mode in ("all", "xlsx"):
        save_as_xlsx(xlsx_path, headers, result_list)
    
    # os.system(f"start {xlsx_path}")

# save as csv

@try_wrapper
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

# save as xlsx

@try_wrapper
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
