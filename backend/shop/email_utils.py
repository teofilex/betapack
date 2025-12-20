import os
import resend
from django.conf import settings

# Postavi Resend API key
resend.api_key = os.environ.get('RESEND_API_KEY', '')


def send_email_via_resend(subject, message, recipient_email, from_email=None):
    """
    Šalje email preko Resend API-ja.

    Args:
        subject (str): Naslov emaila
        message (str): Sadržaj emaila (plain text)
        recipient_email (str): Email primaoca
        from_email (str, optional): Email pošiljaoca. Defaults to settings.DEFAULT_FROM_EMAIL

    Returns:
        bool: True ako je uspešno poslat, False ako ne
    """
    if not resend.api_key:
        print('[RESEND] API key nije postavljen!')
        return False

    if not from_email:
        from_email = settings.DEFAULT_FROM_EMAIL

    try:
        params = {
            "from": from_email,
            "to": [recipient_email],
            "subject": subject,
            "html": f"<pre>{message}</pre>",  # Konvertuj plain text u HTML sa preformatiranim tekstom
        }

        print(f'[RESEND] Sending email to {recipient_email}...')
        response = resend.Emails.send(params)
        print(f'[RESEND] Email sent successfully! ID: {response}')
        return True

    except Exception as e:
        print(f'[RESEND] Error sending email: {e}')
        return False
