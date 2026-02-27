import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
FROM_NAME = "AI Fashion Studio"


def _send(to_email: str, subject: str, html_body: str) -> bool:
    """Send an email. Returns True on success, False on failure."""
    if not SMTP_USER or not SMTP_PASS:
        print(f"[EMAIL SKIPPED] No SMTP config. Would send to {to_email}: {subject}")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{FROM_NAME} <{SMTP_USER}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


# ─── EMAIL TEMPLATES ──────────────────────────────────────────

def send_welcome_email(to_email: str, name: str) -> bool:
    subject = "✦ Welcome to AI Fashion Studio!"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;background:#0a0a0f;color:#f0ece6;border-radius:16px;overflow:hidden;">
      <div style="background:linear-gradient(135deg,#1a1a2e,#2d1b1b);padding:40px 32px;text-align:center;">
        <h1 style="font-size:2rem;color:#d4af37;margin:0;">✦ AI Fashion Studio</h1>
        <p style="color:#b0a090;margin:8px 0 0;">Your AI-powered style companion</p>
      </div>
      <div style="padding:36px 32px;">
        <h2 style="color:#d4af37;font-size:1.4rem;">Welcome, {name}! 🎉</h2>
        <p style="color:#c0b8b0;line-height:1.7;">You&apos;re now part of AI Fashion Studio. Here&apos;s what you can do:</p>
        <table style="width:100%;border-collapse:collapse;margin:24px 0;">
          <tr><td style="padding:12px;"><span style="font-size:1.5rem;">✦</span></td><td style="color:#c0b8b0;padding:12px;"><strong style="color:#d4af37;">Design Generator</strong> — Turn text prompts into stunning AI fashion designs</td></tr>
          <tr><td style="padding:12px;"><span style="font-size:1.5rem;">📷</span></td><td style="color:#c0b8b0;padding:12px;"><strong style="color:#d4af37;">Photo Stylist</strong> — Upload your photo and get personalized outfit recommendations</td></tr>
          <tr><td style="padding:12px;"><span style="font-size:1.5rem;">🛍️</span></td><td style="color:#c0b8b0;padding:12px;"><strong style="color:#d4af37;">Product Finder</strong> — Discover affordable outfits similar to your AI designs</td></tr>
        </table>
        <div style="text-align:center;margin:32px 0;">
          <a href="http://localhost:5173/design" style="background:linear-gradient(135deg,#d4af37,#c49b2d);color:#1a1200;padding:14px 32px;border-radius:50px;font-weight:700;font-size:1rem;text-decoration:none;display:inline-block;">✦ Start Designing</a>
        </div>
        <p style="color:#786858;font-size:0.85rem;text-align:center;">AI Fashion Studio · Making fashion design accessible for everyone</p>
      </div>
    </div>
    """
    return _send(to_email, subject, html)


def send_design_ready_email(to_email: str, name: str, prompt: str, image_url: str) -> bool:
    subject = "✦ Your AI Fashion Design is Ready!"
    display_url = f"http://localhost:8000{image_url}" if image_url.startswith("/") else image_url
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;background:#0a0a0f;color:#f0ece6;border-radius:16px;overflow:hidden;">
      <div style="background:linear-gradient(135deg,#1a1a2e,#2d1b1b);padding:40px 32px;text-align:center;">
        <h1 style="font-size:2rem;color:#d4af37;margin:0;">✦ Design Ready!</h1>
      </div>
      <div style="padding:36px 32px;">
        <p style="color:#c0b8b0;">Hi <strong style="color:#d4af37;">{name}</strong>,</p>
        <p style="color:#c0b8b0;line-height:1.7;">Your AI fashion design has been generated! 🎨</p>
        <div style="background:#1a1a26;border:1px solid #d4af3733;border-radius:12px;padding:20px;margin:20px 0;">
          <p style="color:#786858;font-size:0.8rem;margin:0 0 8px;text-transform:uppercase;letter-spacing:0.1em;">Your Prompt</p>
          <p style="color:#d4af37;font-style:italic;margin:0;">&ldquo;{prompt}&rdquo;</p>
        </div>
        <img src="{display_url}" alt="Your AI Design" style="width:100%;border-radius:12px;margin:16px 0;" />
        <div style="text-align:center;margin:24px 0;">
          <a href="http://localhost:5173/history" style="background:linear-gradient(135deg,#d4af37,#c49b2d);color:#1a1200;padding:14px 32px;border-radius:50px;font-weight:700;text-decoration:none;display:inline-block;">View in History</a>
        </div>
      </div>
    </div>
    """
    return _send(to_email, subject, html)


def send_recommendation_email(to_email: str, name: str, occasion: str, outfits: list) -> bool:
    subject = f"✦ Your {occasion.title()} Outfit Recommendations are Ready!"
    outfit_rows = "".join([
        f'<div style="padding:12px;border-bottom:1px solid #2a2020;"><strong style="color:#d4af37;">#{o["rank"]} {o["outfit"]}</strong><br/><span style="color:#786858;font-size:0.85rem;">{o["reason"]}</span></div>'
        for o in outfits[:3]
    ])
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;background:#0a0a0f;color:#f0ece6;border-radius:16px;overflow:hidden;">
      <div style="background:linear-gradient(135deg,#1a1a2e,#2d1b1b);padding:40px 32px;text-align:center;">
        <h1 style="font-size:2rem;color:#d4af37;margin:0;">👗 Outfit Recommendations</h1>
      </div>
      <div style="padding:36px 32px;">
        <p style="color:#c0b8b0;">Hi <strong style="color:#d4af37;">{name}</strong>,</p>
        <p style="color:#c0b8b0;line-height:1.7;">Your personalized <strong>{occasion}</strong> outfit recommendations are ready:</p>
        <div style="background:#1a1a26;border:1px solid #d4af3733;border-radius:12px;margin:20px 0;overflow:hidden;">
          {outfit_rows}
        </div>
        <div style="text-align:center;margin:24px 0;">
          <a href="http://localhost:5173/upload" style="background:linear-gradient(135deg,#d4af37,#c49b2d);color:#1a1200;padding:14px 32px;border-radius:50px;font-weight:700;text-decoration:none;display:inline-block;">View Full Recommendations</a>
        </div>
      </div>
    </div>
    """
    return _send(to_email, subject, html)
