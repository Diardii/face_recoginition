import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import (
    MAIL_SERVER,
    MAIL_PORT,
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_FROM_NAME
)


# ============================================================
# SEND RESET PASSWORD EMAIL
# ============================================================

def send_reset_email(to_email, reset_link):

    if not MAIL_USERNAME or not MAIL_PASSWORD:

        print(
            "[MAILER ERROR] MAIL_USERNAME / MAIL_PASSWORD "
            "belum di-set. Email tidak dikirim."
        )

        return False

    subject = "Reset Password - Face AI Attendance"

    body = f"""Halo,

Kami menerima permintaan untuk reset password akun Anda.

Klik link berikut untuk membuat password baru
(link berlaku selama 30 menit):

{reset_link}

Jika Anda tidak merasa meminta reset password,
abaikan email ini saja, password Anda tidak akan berubah.

Terima kasih.
"""

    message = MIMEMultipart()

    message["From"] = (
        f"{MAIL_FROM_NAME} <{MAIL_USERNAME}>"
    )

    message["To"] = to_email

    message["Subject"] = subject

    message.attach(
        MIMEText(body, "plain")
    )

    try:

        with smtplib.SMTP(
            MAIL_SERVER,
            MAIL_PORT
        ) as server:

            server.starttls()

            server.login(
                MAIL_USERNAME,
                MAIL_PASSWORD
            )

            server.sendmail(
                MAIL_USERNAME,
                to_email,
                message.as_string()
            )

        return True

    except Exception as error:

        print(
            "[MAILER ERROR]",
            error
        )

        return False