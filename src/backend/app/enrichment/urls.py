"""URL and domain extraction."""

import re
from urllib.parse import urlparse

URL_PATTERN = re.compile(
    r"https?://[^\s<>\"')\]]+",
    re.IGNORECASE,
)


def extract_urls_and_domains(text: str) -> dict:
    """Extract URLs and their domains from text.

    Returns {"urls": [...], "domains": [...]}
    """
    if not text:
        return {"urls": [], "domains": []}

    urls = list(set(URL_PATTERN.findall(text)))
    # Clean trailing punctuation
    urls = [url.rstrip(".,;:!?") for url in urls]

    domains = []
    for url in urls:
        try:
            parsed = urlparse(url)
            if parsed.hostname:
                domain = parsed.hostname.lower()
                if domain.startswith("www."):
                    domain = domain[4:]
                if domain not in domains:
                    domains.append(domain)
        except ValueError:
            continue

    return {"urls": urls, "domains": domains}
