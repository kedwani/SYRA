"""Custom email backend for Brevo (Sendinblue) using direct API calls."""

import logging
import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage

logger = logging.getLogger(__name__)


class BrevoEmailBackend(BaseEmailBackend):
    """Email backend that sends emails via Brevo API."""

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = None
        self._initialized = False

    def _initialize(self):
        """Initialize the Brevo API configuration."""
        if self._initialized:
            return

        from django.conf import settings

        self.api_key = getattr(settings, "BREVO_API_KEY", None)
        self.api_url = "https://api.brevo.com/v3/smtp/email"

        if not self.api_key:
            logger.warning("Brevo API key not configured")
            return

        self._initialized = True

    def send_messages(self, messages):
        """Send messages via Brevo API."""
        self._initialize()

        if not self.api_key:
            if not self.fail_silently:
                raise Exception("Brevo API key not configured")
            return 0

        sent_count = 0

        for message in messages:
            try:
                self._send(message)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send email via Brevo: {e}")
                if not self.fail_silently:
                    raise

        return sent_count

    def _send(self, message):
        """Send a single email via Brevo API."""
        # Build sender
        sender = message.from_email or "noreply@syra.app"

        if "<" in sender:
            sender_name = sender.split("<")[0].strip()
            sender_email = sender.split("<")[1].replace(">", "").strip()
        else:
            sender_name = "SYRA"
            sender_email = sender

        # Build recipients
        to_emails = []
        for recipient in message.to:
            if "<" in recipient:
                name = recipient.split("<")[0].strip()
                email = recipient.split("<")[1].replace(">", "").strip()
                to_emails.append({"email": email, "name": name})
            else:
                to_emails.append({"email": recipient})

        # Prepare email content
        html_content = None
        text_content = None

        if message.content_subtype == "html":
            html_content = message.body
        else:
            text_content = message.body

        # Build request payload
        payload = {
            "subject": message.subject,
            "sender": {"name": sender_name, "email": sender_email},
            "to": to_emails,
        }

        if html_content:
            payload["htmlContent"] = html_content
        if text_content:
            payload["textContent"] = text_content

        # Send request
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }

        response = requests.post(
            self.api_url, json=payload, headers=headers, timeout=30
        )

        if response.status_code not in [200, 201]:
            error_msg = f"Brevo API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            if not self.fail_silently:
                raise Exception(error_msg)

        logger.info(f"Email sent successfully to {message.to}")
