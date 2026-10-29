"""Generate the honeypot's fake filesystem content (Gemini) and plant canary
"breadcrumbs" in it. Runs as a one-shot job / init container."""
import argparse
import datetime
import json
import logging
import os
import random
import sys
from pathlib import Path

import httpx

log = logging.getLogger("generator")

MOCK_CONTENT = {
    "/var/log/auth.log": "Oct 12 03:14:07 web01 sshd[2211]: Failed password for root from 185.220.101.4 port 51122 ssh2\n"
                         "Oct 12 08:02:31 web01 sshd[2390]: Accepted publickey for sysadmin from 10.0.4.17 port 50122 ssh2\n",
    "/home/sysadmin/.bash_history": "sudo apt update && sudo apt upgrade -y\nsystemctl status nginx\ntail -f /var/log/nginx/error.log\n",
    "/home/sysadmin/todo.txt": "- rotate ssh keys\n- check backups\n- renew TLS cert\n",
}


def gemini_generate(prompt: str, model: str) -> str:
    from google import genai

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return client.models.generate_content(model=model, contents=prompt).text


def plant_breadcrumbs(
    content: dict[str, str], breadcrumbs: list[dict], api_url: str, admin_token: str,
    transport: httpx.BaseTransport | None = None,
) -> int:
    """Create (idempotently) one canary token per breadcrumb and append its line
    to the target file. Returns the number planted."""
    planted = 0
    with httpx.Client(base_url=api_url, headers={"Authorization": f"Bearer {admin_token}"},
                      timeout=10, transport=transport) as client:
        for b in breadcrumbs:
            r = client.post("/api/v1/tokens", json={
                "name": b["name"], "type": b.get("type", "url"), "external_key": b["external_key"],
            })
            r.raise_for_status()
            line = b["line"].format(url=r.json()["value"])
            body = content.setdefault(b["file"], "")
            content[b["file"]] = body + ("" if body.endswith("\n") or not body else "\n") + line + "\n"
            planted += 1
    return planted


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--persona", default="persona_config.json")
    p.add_argument("--output", required=True, help="directory the honeypot seed is written to")
    p.add_argument("--mock", action="store_true", help="skip Gemini; use canned content")
    p.add_argument("--no-breadcrumbs", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    config = json.loads(Path(args.persona).read_text())
    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    use_mock = args.mock or not os.environ.get("GEMINI_API_KEY")
    if use_mock:
        log.warning("no GEMINI_API_KEY (or --mock): using canned content")

    run_id = f"RunID:{random.randint(100000, 999999)} Date:{datetime.datetime.now().isoformat()}"
    content: dict[str, str] = {}
    for f in config["files"]:
        if use_mock:
            content[f["path"]] = MOCK_CONTENT.get(f["path"], "")
            continue
        try:
            content[f["path"]] = gemini_generate(f["prompt"] + "\n" + run_id, model)
        except Exception as exc:  # keep the honeypot bootable if the LLM is down
            log.error("generation failed for %s (%s); using canned content", f["path"], exc)
            content[f["path"]] = MOCK_CONTENT.get(f["path"], "")

    crumbs = config.get("breadcrumbs", [])
    if crumbs and not args.no_breadcrumbs:
        api_url, token = os.environ.get("API_URL"), os.environ.get("ADMIN_TOKEN")
        if not (api_url and token):
            log.error("API_URL/ADMIN_TOKEN not set: skipping %d breadcrumbs", len(crumbs))
        else:
            try:
                n = plant_breadcrumbs(content, crumbs, api_url, token)
                log.info("planted %d breadcrumbs", n)
            except Exception as exc:
                log.error("breadcrumb planting failed: %s", exc)
                return 1

    out = Path(args.output)
    for path, text in content.items():
        dest = out / path.lstrip("/")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)
        log.info("wrote %s (%d bytes)", dest, len(text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
