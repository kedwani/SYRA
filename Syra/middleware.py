"""
Custom middleware to ensure language is properly activated from session/cookie.
This fixes the issue where Arabic translations don't display in templates.
"""

import logging
from django.utils import translation
from django.conf import settings

logger = logging.getLogger(__name__)


class ForceLanguageMiddleware:
    """
    Middleware to force activate language from session or cookie.
    This ensures Arabic translations work properly.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Try to get language from session first
        language = None

        # Check session
        if hasattr(request, "session") and request.session:
            language = request.session.get("_language")
            if language:
                logger.debug(f"Language from session: {language}")

        # Check cookie
        if not language:
            cookie_lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
            if cookie_lang:
                logger.debug(f"Language from cookie: {cookie_lang}")
                language = cookie_lang

        # Check Accept-Language header as last resort
        if not language:
            accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
            if accept_language:
                # Extract first language preference
                langs = [
                    l.split(";")[0].split("-")[0] for l in accept_language.split(",")
                ]
                if "ar" in langs:
                    language = "ar"
                    logger.debug(f"Language from Accept-Language: {language}")

        # Activate the language if found and valid
        if language:
            if language in [l[0] for l in settings.LANGUAGES]:
                logger.debug(f"Activating language: {language}")
                translation.activate(language)

        response = self.get_response(request)

        # Deactivate language after request to prevent state leakage
        translation.deactivate()

        return response
