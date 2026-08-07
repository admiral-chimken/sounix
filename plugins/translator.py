COMMAND = "translate"


from deep_translator import GoogleTranslator


COMMAND = "translate"


LANGUAGE_MAP = {
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "italian": "it",
    "portuguese": "pt",
    "japanese": "ja",
    "korean": "ko",
    "chinese": "zh-CN",
    "arabic": "ar",
    "russian": "ru",
    "hindi": "hi",
    "dutch": "nl",
}


def run(args):
    if not args:
        return (
            "Sounix Translator\n\n"
            "Use:\n"
            "translate <text> to <language>\n\n"
            "Example:\n"
            "translate hello to spanish"
        )

    lower_args = args.lower()

    if " to " not in lower_args:
        return (
            "Sounix: Please use:\n"
            "translate <text> to <language>"
        )

    split_position = lower_args.rfind(" to ")

    text = args[:split_position].strip()
    language_name = args[split_position + 4:].strip().lower()

    if not text or not language_name:
        return (
            "Sounix: Please use:\n"
            "translate <text> to <language>"
        )

    target_language = LANGUAGE_MAP.get(
        language_name,
        language_name,
    )

    try:
        translated = GoogleTranslator(
            source="auto",
            target=target_language,
        ).translate(text)
        print("Translated =", repr(translated))
        return (
            "========== SOUNIX TRANSLATOR ==========\n\n"
            f"Original:\n{text}\n\n"
            f"{language_name.title()}:\n{translated}"
        )

    except Exception as error:
        return (
            "Sounix: Translation failed.\n\n"
            f"Error: {error}"
        )
