import requests
import time

def get_json(url, headers=None, params=None, api_base="https://api.github.com"):
    full_url = url if url.startswith("http") else f"{api_base}{url}"

    try:
        r = requests.get(full_url, headers=headers, params=params, timeout=30)
    except requests.RequestException:
        return None

    # Rate limit or abuse detection
    if r.status_code in (403, 429):
        time.sleep(5)
        return None

    # Empty response
    if not r.text or r.text.strip() == "":
        return None

    # HTML instead of JSON (abuse page, login page, etc.)
    if r.text.lstrip().startswith("<"):
        return None

    try:
        return r.json()
    except ValueError:
        return None
