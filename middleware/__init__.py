import logging

from django.utils import translation


class SubdomainLanguageMiddleware(object):
    """
    Set the language for the site based on the subdomain the request
    is being served on. For example, serving on 'fr.domain.com' would
    make the language French (fr).
    """
    LANGUAGES = [
        "en", "es",
    ]

    def process_request(self, request):
        host = request.get_host()

        print ">>> MIDDLEWARE : HOST :", host

        lang = old_lang = translation.get_language()
        print ">>> OLD LANG :", old_lang

        if host:
            # if "manualesdediscipulado" in host:
            #     lang = "es"
            # elif "discipleshipworkbooks" in host:
            #     lang = "en"

            translation.activate(lang)

            request.LANGUAGE_CODE = lang

            print ">>> REQUEST : LANGUAGE_CODE :", request.LANGUAGE_CODE
