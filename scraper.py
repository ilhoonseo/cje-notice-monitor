import os
import sys
import json
import requests
from datetime import datetime, timezone, timedelta

# Disable insecure request warning since we are disabling SSL verification for compatibility
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
TARGET_URL = "https://www.cje.ac.kr/elder_edu/web/board/brdList.do?menu_cd=000017"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
NOTICES_FILE = os.path.join(DATA_DIR, "notices.json")
STATUS_FILE = os.path.join(DATA_DIR, "status.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def get_korean_now_str():
    # Convert UTC time to KST (UTC+9)
    utc_now = datetime.now(timezone.utc)
    kst_tz = timezone(timedelta(hours=9))
    kst_now = utc_now.astimezone(kst_tz)
    return kst_now.strftime("%Y-%m-%d %H:%M:%S KST")

def scrape_board():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"Scraping notice board: {TARGET_URL}...")
    response = requests.get(TARGET_URL, headers=headers, verify=False, timeout=15)
    response.raise_for_status()
    
    # Parse JSON directly
    data = response.json()
    if "brdList" not in data:
        raise ValueError("Invalid JSON response: 'brdList' key not found.")
        
    return data["brdList"]

def load_local_notices():
    if os.path.exists(NOTICES_FILE):
        try:
            with open(NOTICES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading local notices file: {e}")
    return []

def save_local_notices(notices):
    try:
        with open(NOTICES_FILE, "w", encoding="utf-8") as f:
            json.dump(notices, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(notices)} notices to {NOTICES_FILE}")
    except Exception as e:
        print(f"Error saving notices file: {e}")

def update_status(success, error_msg=None, total_notices=0):
    status_data = {
        "status": "Operational" if success else "Degraded",
        "last_scraped": get_korean_now_str(),
        "last_success": success,
        "error_message": error_msg,
        "total_notices": total_notices
    }
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)
        print(f"Updated status file: {status_data}")
    except Exception as e:
        print(f"Error updating status file: {e}")

def main():
    print(f"=== Web Scraper Started at {get_korean_now_str()} ===")
    
    try:
        # Load existing announcements from storage
        existing_notices = load_local_notices()
        existing_ids = {item["num"] for item in existing_notices if "num" in item}
        print(f"Loaded {len(existing_notices)} existing notices.")
        
        # Scrape current announcements
        current_notices = scrape_board()
        print(f"Successfully scraped {len(current_notices)} notices from web.")
        
        # Filter fields to store clean JSON
        cleaned_current_notices = []
        for item in current_notices:
            cleaned_current_notices.append({
                "num": item.get("num"),
                "rnum": item.get("rnum"),
                "title": item.get("title", "").strip(),
                "writer": item.get("username", "교육대학원").strip(),
                "write_dt": item.get("write_dt", "").strip(),
                "cnt": item.get("cnt", 0),
                "cont_html": item.get("cont", "").strip()
            })
            
        # Determine new notices
        new_notices = []
        
        # If existing list is empty, treat as first run and do not trigger alert spam
        is_first_run = len(existing_notices) == 0
        if is_first_run:
            print("First run detected. Storing notices without notifications.")
        else:
            for item in cleaned_current_notices:
                if item["num"] not in existing_ids:
                    new_notices.append(item)
                    
        print(f"Detected {len(new_notices)} new notices.")
        
        # Gmail notification is handled independently by Google Apps Script.
        for item in new_notices:
            print(f"New notice detected: {item['num']} - {item['title']}")
                
        # Update notices local file
        save_local_notices(cleaned_current_notices)
        
        # Mark as operational
        update_status(success=True, total_notices=len(cleaned_current_notices))
        print("=== Scraper Finished Successfully ===")
        
    except Exception as e:
        print(f"Error occurred during scraper execution: {e}")
        # Mark system status as degraded
        update_status(success=False, error_msg=str(e))
        print("=== Scraper Finished with Errors ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
