
import csv
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", None)
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", None)

class GmailMailer:
    def __init__(self, sender_email = SMTP_USERNAME, sender_password = SMTP_PASSWORD):
        if not sender_email or not sender_password:
            raise ValueError("SMTP_USERNAME and SMTP_PASSWORD must be set in the environment variables.")
        
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_host = SMTP_HOST
        self.smtp_port = SMTP_PORT

    def send_email_html(self, recipient_email: str, subject: str, html_content: str) -> bool:
        msg = MIMEMultipart("alternative")
        msg["From"] = self.sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject

        mime_html = MIMEText(html_content, "html")
        msg.attach(mime_html)

        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"[ERROR] send email fail: {e}")
            try:
                server.quit()
            except:
                pass
            return False

    def format_results_fragment(self, results: list) -> str:
        html_parts = []

        if not results:
            html_parts.append("<p>Không tìm thấy paper nào gần đây phù hợp với từ khóa.</p>")
        else:
            for idx, item in enumerate(results, start=1):
                entity = item.get("hit", {}).get("entity", {})
                title = entity.get("title_paper", "N/A")
                novelty = entity.get("novelty", "N/A")
                content = entity.get("content", "N/A")
                pdf_url = entity.get("pdf_url", "N/A")

                paper_html = f"""
                <div class="paper-container">
                  <div class="paper-title">{idx}. {title}</div>
                  <div class="paper-novelty"><strong>Novelty:</strong> {novelty}</div>
                  <div class="paper-content"><strong>Summary:</strong><br>{content}</div>
                  <a href="{pdf_url}">Đọc bài báo trên arXiv</a>
                </div>
                """
                html_parts.append(paper_html)

        return "".join(html_parts)


