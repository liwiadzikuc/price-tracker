import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
#ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO")

def send_verification_email(recipient_email: str, code: str):
    subject = "Kod weryfikacyjny - Price Tracker"
    body = f"""
    Twój kod weryfikacyjny to: {code}

    Wpisz go na stronie, aby aktywować konto.
    """

    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, recipient_email, msg.as_string())
        logger.info(f"Wysłano kod weryfikacyjny na {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Błąd wysyłania maila: {e}")
        return False

def send_price_alert_email(recipient_email: str,product_name: str, price: float, target_price: float, product_url: str):
    if not all([SMTP_SERVER, SMTP_USER, SMTP_PASSWORD]):
        logger.error("Brak pełnej konfiguracji SMTP. Nie można wysłać e-maila.")
        return

    subject = f"🚨 ALERT CENOWY: {product_name} za {price} zł!"
    body = f"""
    Cena produktu spadła poniżej Twojego progu docelowego!

    Nazwa produktu: {product_name}
    Aktualna cena: {price:.2f} zł
    Cena docelowa: {target_price:.2f} zł

    Sprawdź ofertę tutaj: {product_url}

    Pozdrawiamy,
    Price Tracker Bot
    """

    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls() 
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, recipient_email, msg.as_string())
        logger.info(f"Wysłano alert e-mail dla {product_name}")
        return True
    except Exception as e:
        logger.error(f"Błąd podczas wysyłania e-maila dla {product_name}: {e}")
        return False
