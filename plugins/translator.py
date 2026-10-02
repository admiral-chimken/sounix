"""Sounix translator plugin: your local Ollama model first, Google as the backup."""
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
LANGUAGE_NAMES = {code: name for name, code in LANGUAGE_MAP.items()}

SYSTEM = (
    "You are a translation engine. Translate the user's text into the requested "
    "language. Reply with ONLY the translation: no quotes, notes, or explanations."
)
SPECIALIST = {"code", "reasoning"}


def _pick_model(router):
    """Pinned model if you set one, else the largest general model up to 20B."""
    models = [m for m in router.installed() if not (m.tags & SPECIALIST)]
    pinned = router.resolve(router.pinned) if router.pinned else None
    if pinned and not (pinned.tags & SPECIALIST):
        return pinned.name
    pool = [m for m in models if m.params_b <= 20] or models
    if not pool:
        raise RuntimeError("no suitable local model installed")
    return max(pool, key=lambda m: m.params_b).name


def _translate_local(text, language):
    from ai_control import router

    model = _pick_model(router)
    answer, used = router.complete(
        f"Translate into {language}:\n\n{text}",
        system=SYSTEM,
        task="triage",
        model=model,
    )
    answer = answer.strip().strip('"\u201c\u201d').strip()
    if not answer:
        raise RuntimeError("the model gave an empty answer")
    return answer, used


def _translate_google(text, code):
    from deep_translator import GoogleTranslator

    return GoogleTranslator(source="auto", target=code).translate(text)


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

    target_language = LANGUAGE_MAP.get(language_name, language_name)
    language = LANGUAGE_NAMES.get(language_name, language_name).title()

    translated = engine = None
    errors = []

    try:
        translated, model = _translate_local(text, language)
        engine = f"local model: {model}"
    except Exception as error:
        errors.append(f"Local model: {error}")

    if not translated:
        try:
            translated = _translate_google(text, target_language)
            engine = "Google Translate"
        except Exception as error:
            errors.append(f"Google: {error}")

    if not translated:
        return "Sounix: Translation failed.\n\n" + "\n".join(errors)

    return (
        "========== SOUNIX TRANSLATOR ==========\n\n"
        f"Original:\n{text}\n\n"
        f"{language}:\n{translated}\n\n"
        f"({engine})"
    )
