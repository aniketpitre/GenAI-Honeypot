import json
import re

from .config import get_settings


def _mock(prompt: str) -> list[str]:
    slug = re.sub(r"[^a-z0-9]+", "-", prompt.lower()).strip("-")[:40] or "docs"
    return [
        f"https://files.corp-internal.example/sites/finance/{slug}-CONFIDENTIAL.xlsx",
        f"https://s3.amazonaws.example/acme-private-backups/{slug}/credentials.csv",
        f"https://vault.corp-internal.example/share/{slug}/export.zip",
    ]


def generate_deceptive_urls(prompt: str) -> list[str]:
    """Ask Gemini for enticing decoy URLs; fall back to templates without a key."""
    s = get_settings()
    if not s.gemini_api_key:
        return _mock(prompt)
    try:
        from google import genai

        client = genai.Client(api_key=s.gemini_api_key)
        resp = client.models.generate_content(
            model=s.gemini_model,
            contents=(
                "Generate 3 to 5 realistic but fictional URLs an attacker would find "
                "enticing, based on this description. Use only reserved example domains. "
                'Return JSON: {"urls": ["..."]}.\nDescription: ' + prompt
            ),
            config={"response_mime_type": "application/json"},
        )
        urls = json.loads(resp.text)["urls"]
        if isinstance(urls, list) and all(isinstance(u, str) for u in urls) and urls:
            return urls[:5]
    except Exception:
        pass
    return _mock(prompt)
