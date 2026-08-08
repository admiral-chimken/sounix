import urllib.parse
import webbrowser


def google_search(query):
    query = query.strip()

    if not query:
        return "Sounix: Tell me what you want to search for."

    url = (
        "https://www.google.com/search?q="
        + urllib.parse.quote_plus(query)
    )

    try:
        opened = webbrowser.open(url)

        if opened:
            return f"Sounix: Opening Google search for '{query}'."

        return (
            "Sounix: I could not automatically open your browser.\n"
            f"Search URL:\n{url}"
        )

    except Exception as error:
        return (
            "Sounix: I could not open your browser.\n"
            f"Error: {error}"
        )
