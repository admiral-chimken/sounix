import subprocess
import urllib.parse


def google_search(query):
    url = (
        "https://www.google.com/search?q="
        + urllib.parse.quote_plus(query)
    )

    subprocess.Popen(["xdg-open", url])

    return f"Sounix: Opening Google search for '{query}'."

