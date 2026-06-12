"""Push the demo-data knowledge docs into the Foundry IQ (Azure AI Search) index.

This is the re-indexing step that makes locally-authored knowledge documents
available to live grounding/retrieval. The FastAPI app's FoundryIQKnowledgeProvider
searches an index whose documents expose: id, title, source, content, decision_type.
This script reads every file in demo-data/, builds one document per file, and
uploads them with mergeOrUpload so re-running is safe (idempotent).

Usage (from repo root, with the API venv / deps available):

    python scripts/index_foundry_docs.py

It reads connection settings from the same .env the app uses:
    FOUNDRY_IQ_ENDPOINT      e.g. https://hxrizxn-search-xxxx.search.windows.net
    FOUNDRY_IQ_API_KEY       an admin key (query keys cannot upload)
    FOUNDRY_IQ_INDEX_NAME    e.g. hxrizxn-demo

Pass --create-index to (re)create the index definition before uploading.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.core.config import get_settings  # noqa: E402

API_VERSION = "2024-07-01"
DEMO_DATA = ROOT / "demo-data"

# Map filename keywords -> decision_type so retrieval can bias by decision kind.
DECISION_TYPE_RULES = [
    (("relationship", "honesty", "trust", "harm", "emotional", "social-fallout", "responsibility", "wellbeing"), "relationship"),
    (("enterprise", "contract", "customer", "reference", "revenue", "runway", "legal"), "startup"),
    (("engineering", "hiring", "capacity", "burnout"), "career"),
    (("relocation", "grad", "school"), "relocation"),
    (("budget", "priorities"), "general"),
    (("startup", "idea"), "startup"),
    (("decision-science",), "general"),
]


def infer_decision_type(name: str) -> str:
    lowered = name.lower()
    for keywords, dtype in DECISION_TYPE_RULES:
        if any(k in lowered for k in keywords):
            return dtype
    return "general"


def slug_key(path: Path) -> str:
    # Azure Search document keys must be letters, digits, _, -, =. Derive from filename.
    return re.sub(r"[^A-Za-z0-9_\-=]", "-", path.stem)


def title_from_content(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def build_documents() -> list[dict]:
    docs: list[dict] = []
    for path in sorted(DEMO_DATA.glob("*")):
        if path.suffix.lower() not in {".md", ".txt", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        docs.append(
            {
                "@search.action": "mergeOrUpload",
                "id": slug_key(path),
                "title": title_from_content(text, path.stem.replace("-", " ").title()),
                "source": f"demo-data/{path.name}",
                "content": text,
                "decision_type": infer_decision_type(path.name),
            }
        )
    return docs


def create_index(endpoint: str, key: str, index_name: str) -> None:
    """(Re)create a minimal index matching what the app selects on."""
    definition = {
        "name": index_name,
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
            {"name": "title", "type": "Edm.String", "searchable": True},
            {"name": "source", "type": "Edm.String", "searchable": False, "retrievable": True},
            {"name": "content", "type": "Edm.String", "searchable": True},
            {"name": "decision_type", "type": "Edm.String", "searchable": True, "filterable": True},
        ],
    }
    url = f"{endpoint}/indexes/{index_name}?api-version={API_VERSION}"
    r = httpx.put(url, json=definition, headers={"api-key": key, "Content-Type": "application/json"}, timeout=30)
    if r.status_code not in (200, 201):
        print(f"  index create/update returned {r.status_code}: {r.text[:300]}")
    else:
        print(f"  index '{index_name}' created/updated.")


def upload(endpoint: str, key: str, index_name: str, documents: list[dict]) -> None:
    url = f"{endpoint}/indexes/{index_name}/docs/index?api-version={API_VERSION}"
    r = httpx.post(url, json={"value": documents}, headers={"api-key": key, "Content-Type": "application/json"}, timeout=60)
    r.raise_for_status()
    results = r.json().get("value", [])
    ok = sum(1 for x in results if x.get("status"))
    print(f"  uploaded {ok}/{len(results)} documents.")
    for x in results:
        if not x.get("status"):
            print(f"    FAILED {x.get('key')}: {x.get('errorMessage')}")


def main() -> None:
    settings = get_settings()
    endpoint = (settings.foundry_iq_endpoint or "").rstrip("/")
    key = settings.foundry_iq_api_key or ""
    index_name = settings.foundry_iq_index_name

    if not (endpoint and key):
        print("FOUNDRY_IQ_ENDPOINT / FOUNDRY_IQ_API_KEY are not set in .env. Aborting.")
        sys.exit(1)
    if not endpoint.startswith("http"):
        endpoint = f"https://{endpoint}"

    print(f"Foundry IQ index: {index_name} @ {endpoint}")

    if "--create-index" in sys.argv:
        print("Creating/updating index definition...")
        create_index(endpoint, key, index_name)

    documents = build_documents()
    print(f"Built {len(documents)} documents from {DEMO_DATA}.")
    upload(endpoint, key, index_name, documents)
    print("Done. Live retrieval will now ground against these documents.")


if __name__ == "__main__":
    main()
