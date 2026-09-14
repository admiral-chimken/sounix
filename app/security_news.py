"""
security_news.py
------------------------
Feature #10 (part 2) for Sounix: fetches recent cybersecurity news
headlines and CVE (vulnerability) listings from real public sources,
then asks the AI to summarize them.

This only READS publicly published information -- it does not scan,
probe, or interact with any website beyond fetching its content.
"""

import feedparser
import requests

from ollama_client import ask_ollama

NEWS_FEED_URL = "https://feeds.feedburner.com/TheHackersNews"
CVE_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def get_recent_headlines(limit=5):
    try:
        feed = feedparser.parse(NEWS_FEED_URL)
        headlines = []
        for entry in feed.entries[:limit]:
            title = entry.get("title", "Untitled")
            headlines.append(title)
        return headlines
    except Exception:
        return []


def get_recent_cves(limit=5):
    try:
        params = {"resultsPerPage": limit}
        response = requests.get(CVE_API_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        cves = []
        for item in data.get("vulnerabilities", []):
            cve_id = item.get("cve", {}).get("id", "Unknown ID")
            descriptions = item.get("cve", {}).get("descriptions", [])
            desc_text = ""
            for d in descriptions:
                if d.get("lang") == "en":
                    desc_text = d.get("value", "")
                    break
            cves.append(f"{cve_id}: {desc_text[:150]}")
        return cves
    except Exception:
        return []


def security_news_report():
    headlines = get_recent_headlines()
    cves = get_recent_cves()

    if not headlines and not cves:
        return (
            "Sounix: Could not fetch security news or CVE data right now "
            "-- check your internet connection and try again."
        )

    raw_summary = "Recent cybersecurity headlines:\n"
    raw_summary += "\n".join(f"- {h}" for h in headlines) if headlines else "- (none available)"
    raw_summary += "\n\nRecent CVEs (vulnerabilities):\n"
    raw_summary += "\n".join(f"- {c}" for c in cves) if cves else "- (none available)"

    prompt = (
        "Here is real, current cybersecurity news and vulnerability data:\n\n"
        f"{raw_summary}\n\n"
        "Summarize the 2-3 most notable items in plain language for someone "
        "learning cybersecurity. Don't invent details not present above."
    )

    return ask_ollama(prompt)
