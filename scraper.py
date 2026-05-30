import os
import sys
import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

# Disable insecure request warning since we are disabling SSL verification for compatibility
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
TARGET_URL = "https://www.cje.ac.kr/elder_edu/web/board/brdList.do?menu_cd=000017"
RECIPIENT_EMAIL = "bjkanggr@gmail.com"
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

def clean_html(html_content):
    """Utility to convert HTML notice body to clean plain text for email preview."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    # Get text and replace multiple newlines/spaces
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def send_email(subject, body_html, body_text):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    
    if not sender_email or not sender_password:
        print("Warning: SENDER_EMAIL or SENDER_PASSWORD environment variable not set. Email not sent.")
        print(f"Skipped email subject: {subject}")
        return False

    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = RECIPIENT_EMAIL
        
        # Attach parts
        part1 = MIMEText(body_text, "plain", "utf-8")
        part2 = MIMEText(body_html, "html", "utf-8")
        message.attach(part1)
        message.attach(part2)

        # Set up SMTP Server (Gmail SMTP server)
        smtp_server = "smtp.gmail.com"
        port = 587  # For starttls
        
        print(f"Connecting to SMTP server {smtp_server}:{port}...")
        server = smtplib.SMTP(smtp_server, port, timeout=15)
        server.starttls()  # Secure the connection
        
        print("Logging in to SMTP server...")
        server.login(sender_email, sender_password)
        
        print(f"Sending email to {RECIPIENT_EMAIL}...")
        server.sendmail(sender_email, RECIPIENT_EMAIL, message.as_string())
        server.quit()
        
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send email notification: {e}")
        return False

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
            print("First run detected. Storing notices without sending email notifications.")
        else:
            for item in cleaned_current_notices:
                if item["num"] not in existing_ids:
                    new_notices.append(item)
        
        # [테스트용 임시 주입] 이메일 발송을 테스트하기 위해 임시로 새 공지를 리스트에 추가합니다.
        new_notices.append({
            "num": 999999,
            "title": "[시스템 연동 테스트] 청주교대 대학원 알리미 메일 발송 성공",
            "writer": "알리미 관리 시스템",
            "write_dt": "2026-05-30",
            "cont_html": "<p>이 메일은 <strong>이메일 연동 시스템이 성공적으로 가동 중임</strong>을 검증하기 위한 <strong>시스템 테스트 메일</strong>입니다.<br>이 메일이 정상적으로 도착했다면 모니터링 및 SMTP 메일 발송 연동이 무사히 안착된 것입니다! 수고하셨습니다.</p>"
        })
                    
        print(f"Detected {len(new_notices)} new notices.")
        
        # Send notifications for new notices
        email_failures = 0
        for item in new_notices:
            title = item["title"]
            num = item["num"]
            writer = item["writer"]
            date = item["write_dt"]
            body_clean = clean_html(item["cont_html"])
            
            subject = f"[청주교대 대학원 새 공지] {title}"
            
            # HTML Email Body
            body_html = f"""
            <html>
                <body style="font-family: 'Malgun Gothic', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background-color: #f4f6f9;">
                    <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #e1e8ed; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                        <div style="background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 24px 20px; text-align: center;">
                            <h2 style="margin: 0; font-size: 20px; font-weight: 600;">청주교육대학교 교육전문대학원</h2>
                            <p style="margin: 4px 0 0 0; opacity: 0.9; font-size: 14px;">새로운 공지사항이 등록되었습니다.</p>
                        </div>
                        <div style="padding: 24px 20px;">
                            <h3 style="margin-top: 0; color: #111827; font-size: 18px; border-bottom: 2px solid #f3f4f6; padding-bottom: 12px;">{title}</h3>
                            
                            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 14px;">
                                <tr>
                                    <td style="padding: 6px 0; color: #6b7280; width: 80px;">작성자</td>
                                    <td style="padding: 6px 0; color: #1f2937; font-weight: 500;">{writer}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 6px 0; color: #6b7280;">등록일</td>
                                    <td style="padding: 6px 0; color: #1f2937; font-weight: 500;">{date}</td>
                                </tr>
                            </table>
                            
                            <div style="background-color: #f9fafb; border-left: 4px solid #10b981; padding: 15px; margin-bottom: 24px; border-radius: 4px; font-size: 14px; white-space: pre-wrap; word-break: break-all; color: #4b5563;">
                                {body_clean[:600]}...
                            </div>
                            
                            <div style="text-align: center; margin: 30px 0 10px 0;">
                                <a href="{TARGET_URL}" target="_blank" style="background-color: #10b981; color: white; padding: 12px 28px; text-align: center; text-decoration: none; display: inline-block; font-size: 15px; font-weight: bold; border-radius: 6px; box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);">
                                    전체 게시판 보러가기
                                </a>
                            </div>
                        </div>
                        <div style="background-color: #f9fafb; padding: 15px; text-align: center; font-size: 12px; color: #9ca3af; border-top: 1px solid #f3f4f6;">
                            본 메일은 청주교대 대학원 알리미 서비스에 의해 자동 발송되었습니다.
                        </div>
                    </div>
                </body>
            </html>
            """
            
            # Plain text Email Body (Fallback)
            body_text = f"""
            [청주교육대학교 교육전문대학원 - 새 공지사항 등록 알림]
            
            ■ 제목: {title}
            ■ 작성자: {writer}
            ■ 등록일: {date}
            
            --------------------------------------------------
            내용 요약:
            {body_clean[:500]}...
            --------------------------------------------------
            
            공지사항 전체를 보시려면 아래 링크를 클릭해 주세요.
            게시판 링크: {TARGET_URL}
            """
            
            email_success = send_email(subject, body_html, body_text)
            if not email_success:
                email_failures += 1
                
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
