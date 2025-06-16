import json 
from datetime import datetime as time 
from sentimental_analysis import clean 
import os

def log_content(entry, reasons): 
    log_entry = entry.copy()
    log_entry["cleaned_text"] = clean(entry['text'])
    log_entry["reason"] = "; ".join(reasons) if reasons else "NOT FLAGGED"
 
    CONTENT_LOG = "content_log_cleaned.json"

    #double checking file is correct format 
    if os.path.exists(CONTENT_LOG): 
        try: 
            with open(CONTENT_LOG, 'r') as f: 
                data = json.load(f) 
        except Exception:
            data = [] 
    else: 
        
        data = []

    data.append(log_entry) 
    try: 
        with open(CONTENT_LOG, 'w') as f: 
            json.dump(data, f, indent =2)
    except Exception as e: 
        print(f"Unable to write content log: {e}")

