"""Refresh the homelab numbers between the HOMELAB markers in README.md.

Counts stacks in Jaumoso/homelab (selfhosted/ = active, unused/ = retired)
and reads the "built by me" count from the portfolio's stats.json.
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

API = "https://api.github.com/repos/Jaumoso/homelab/contents/{}"
STATS = "https://raw.githubusercontent.com/Jaumoso/portfolio/main/docs/assets/stats.json"
README = Path(__file__).resolve().parent.parent / "README.md"


def get(url: str):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com"):
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def count_dirs(path: str) -> int:
    return sum(1 for item in get(API.format(path)) if item["type"] == "dir")


def main() -> int:
    active = count_dirs("selfhosted")
    retired = count_dirs("unused")
    try:
        own = get(STATS)["own"]
    except Exception:
        own = None

    lines = [
        f"- 📦 **{active}** services running as Docker Compose stacks",
        f"- 🧪 **{retired}** more tried and retired (configs kept)",
    ]
    if own:
        lines.append(f"- 🚀 **{own}** services built by me")
    block = "<!-- HOMELAB:START -->\n" + "\n".join(lines) + "\n<!-- HOMELAB:END -->"

    text = README.read_text()
    new, n = re.subn(r"<!-- HOMELAB:START -->.*?<!-- HOMELAB:END -->", block, text, flags=re.S)
    if n != 1:
        print("HOMELAB markers not found", file=sys.stderr)
        return 1
    if new != text:
        README.write_text(new)
        print("README updated")
    else:
        print("README already up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
