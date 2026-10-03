"""Load prompts from the repo-root `prompts/` folder (never inline in code).

Every rendered prompt starts with `prompts/safety.md`. Each prompt file contains
an `{{input}}` placeholder inside a fenced block, which is filled with the JSON payload.
"""

import json
import os
from functools import lru_cache
from pathlib import Path

SAFETY_PROMPT = "safety"
INPUT_PLACEHOLDER = "{{input}}"


def prompts_dir() -> Path:
    """`PROMPTS_DIR` if set; else repo-root `prompts/` (local) or `/app/prompts` (Docker image)."""
    if env := os.environ.get("PROMPTS_DIR"):
        return Path(env)
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "prompts"
        if (candidate / f"{SAFETY_PROMPT}.md").is_file():
            return candidate
    return here.parents[3] / "prompts"


@lru_cache
def load_prompt(name: str) -> str:
    path = prompts_dir() / f"{name}.md"
    return path.read_text(encoding="utf-8")


def render(name: str, payload: dict) -> str:
    """Safety preamble + the named prompt with its input filled in."""
    body = load_prompt(name)
    data = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    if INPUT_PLACEHOLDER in body:
        body = body.replace(INPUT_PLACEHOLDER, data)
    else:
        body = f"{body}\n\n## Input\n\n```json\n{data}\n```\n"
    return f"{load_prompt(SAFETY_PROMPT)}\n\n---\n\n{body}"
