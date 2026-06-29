"""
sync.py
Syncs markdown files from a local docs folder into an Open WebUI Knowledge Base.

On every run the script queries Open WebUI to discover which files are already
indexed, compares that against the local filesystem, and uploads new or modified
files while removing deleted ones. Chunking and embedding are handled by Open WebUI.

Signal words for the code reviewer: TODO, CHECK
"""

import hashlib
import os
import sys
import requests
from dotenv import load_dotenv


load_dotenv()

API_URL      = os.getenv("OPEN_WEBUI_API_URL")
API_KEY      = os.getenv("OPEN_WEBUI_API_KEY")
KNOWLEDGE_ID = os.getenv("KNOWLEDGE_ID")

# Docs root. Set via DOCS_DIR env variable in the workflow.
# Defaults to src/content/docs (Astro Starlight layout).
DOCS_DIR = os.getenv(
    "DOCS_DIR",
    os.path.join(os.path.dirname(__file__), "src", "content", "docs"),
)

HEADERS = {"Authorization": f"Bearer {API_KEY}"}


# Talks to the Open WebUI API to read/write files and knowledge entries.

def fetch_state() -> dict[str, str]:
    """
    Fetch the current {normalized_filename: file_id} mapping from Open WebUI.

    Used to compare against the local filesystem to determine what was
    added, modified, or deleted since the last run.

    Returns an empty dict on failure so that new uploads can still proceed.
    """
    r = requests.get(
        f"{API_URL}/api/v1/knowledge/{KNOWLEDGE_ID}",
        headers=HEADERS,
    )
    if not r.ok:
        print(f"[WARN] Could not fetch state: {r.status_code} {r.text}")
        return {}

    # Build a lookup dict: normalized filename -> Open WebUI file ID.
    # This lets us quickly check if a local file already exists remotely.
    state: dict[str, str] = {}
    for f in r.json().get("files", []):
        name = f["meta"]["name"]
        state[name] = f["id"]
    return state


def upload_file(path: str) -> str | None:
    """
    Upload a file to Open WebUI's file store.

    We force synchronous processing so the file is fully processed before
    we try to add it to the knowledge base.
    Returns the file_id assigned by Open WebUI, or None on failure.
    """
    # Build a filename that includes a content hash so we can detect changes later.
    # Example: "guide.md" becomes "guide_a1b2c3d4e5.md".
    base = normalize_path(path)
    name_part, ext = os.path.splitext(base)
    file_name = f"{name_part}_{file_hash(path)}{ext}"

    try:
        with open(path, "rb") as file_obj:
            response = requests.post(
                f"{API_URL}/api/v1/files/",
                headers=HEADERS,
                # Force synchronous processing. The file must be fully chunked
                # and embedded before we add it to the knowledge base.
                params={
                    "process": "true",
                    "process_in_background": "false",
                },
                files={"file": (file_name, file_obj, "text/plain")},
                timeout=120,
            )
    except OSError as exc:
        print(f"[ERROR] Could not open {path}: {exc}")
        return None
    except requests.RequestException as exc:
        print(f"[ERROR] Upload request failed for {path}: {exc}")
        return None

    if not response.ok:
        print(f"[ERROR] Upload failed for {path}: {response.status_code} {response.text}")
        return None

    try:
        return response.json()["id"]
    except (ValueError, KeyError) as exc:
        print(f"[ERROR] Upload response for {path} did not contain a valid file id: {exc}")
        return None


def add_to_knowledge(file_id: str) -> bool:
    """Add an uploaded file to the Knowledge Base (triggers embedding in Open WebUI)."""
    r = requests.post(
        f"{API_URL}/api/v1/knowledge/{KNOWLEDGE_ID}/file/add",
        headers=HEADERS,
        json={"file_id": file_id},
    )
    if not r.ok:
        print(f"[ERROR] file/add failed for {file_id}: {r.status_code} {r.text}")
    return r.ok


def remove_from_knowledge(file_id: str, delete_file: bool = True) -> bool:
    """
    Remove a file from the Knowledge Base.

    If delete_file=True, the backend also deletes the stored file record.
    """
    # Open WebUI uses POST for removal. DELETE returns 405 Method Not Allowed.
    try:
        response = requests.post(
            f"{API_URL}/api/v1/knowledge/{KNOWLEDGE_ID}/file/remove",
            headers=HEADERS,
            params={"delete_file": str(delete_file).lower()},
            json={"file_id": file_id},
            timeout=60,
        )
    except requests.RequestException as exc:
        print(f"[ERROR] file/remove request failed for {file_id}: {exc}")
        return False

    if not response.ok:
        print(f"[ERROR] file/remove failed for {file_id}: {response.status_code} {response.text}")
        return False

    return True


# Local filesystem scanning and path normalisation.

def normalize_path(path: str) -> str: # CHECK: Is this approach OK??
    """
    Return a collision-safe identifier for a file path.

    Strips the DOCS_DIR prefix and replaces slashes with --
    so files in subdirectories never share the same key.

    E.g. "<DOCS_DIR>/api/v2/reference.md" -> "api--v2--reference.md"
         "<DOCS_DIR>/guide.md"             -> "guide.md"
    """
    # Turn "/abs/path/to/docs/api/v2/ref.md" into "api/v2/ref.md"
    path = os.path.relpath(path, DOCS_DIR)
    # Replace slashes with "--" so nested paths become flat, unique keys.
    return path.replace(os.sep, "--")


def file_hash(path: str) -> str:
    """
    detect whether a markdown file changed
    embed that fingerprint into the uploaded filename
    avoid unnecessary re-uploads
    See: https://git-scm.com/book/en/v2/Git-Internals-Git-Objects
    See: https://en.wikipedia.org/wiki/Content-addressable_storage
    """
    h = hashlib.md5()
    with open(path, "rb") as f:
        # Read in 8 KB chunks to keep memory usage low on large files.
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:10]


def scan_local_files() -> dict[str, str]:
    """
    Walk DOCS_DIR recursively and return a {normalized_filename: full_path} map
    for every .md file found.
    """
    local: dict[str, str] = {}
    # os.walk yields (directory_path, subdirectories, filenames) for every
    # folder inside DOCS_DIR, including nested ones.
    for root, _, files in os.walk(DOCS_DIR):
        for file in files:
            # Only pick up markdown files, ignore everything else.
            if file.endswith(".md"):
                full_path = os.path.join(root, file)
                key = normalize_path(full_path)
                local[key] = full_path
    return local


# High-level sync actions: add, update, or delete a single file.

def sync_added(path: str):
    """Upload a new file and add it to the Knowledge Base."""
    print(f"[ADD] {path}")
    file_id = upload_file(path)
    if not file_id:
        return
    if add_to_knowledge(file_id):
        print(f"[OK]  {path} uploaded as {file_id}")


def sync_modified(path: str, old_id: str):
    """Remove the old version first, then upload the new one.
    Open WebUI rejects uploads with duplicate content, so we must delete first."""
    print(f"[UPDATE] {path}")
    # Delete the outdated version before uploading. Order matters here.
    # If removal fails, skip the upload to avoid duplicate content errors.
    if not remove_from_knowledge(old_id, delete_file=True):
        print(f"[WARN] Could not remove old file {old_id}, skipping update for {path}")
        return

    file_id = upload_file(path)
    if not file_id:
        print(f"[WARN] Upload failed for {path} after removing old file")
        return

    if add_to_knowledge(file_id):
        print(f"[OK]  {path} updated to {file_id}, replacing {old_id}")


def sync_deleted(key: str, file_id: str):
    print(f"[DELETE] {key}")
    if remove_from_knowledge(file_id, delete_file=True):
        print(f"[OK]  {key} removed")

# Script entry point. Compares local files vs. remote state and syncs the diff.

def main():
    """
    Compares the local DOCS_DIR folder against the live state in Open WebUI
    and syncs any differences. No arguments needed.
    """
    # Stop early if required config is missing, instead of crashing mid-run.
    if not all([API_URL, API_KEY, KNOWLEDGE_ID]):
        print("[ERROR] Missing env: OPEN_WEBUI_API_URL, OPEN_WEBUI_API_KEY, or KNOWLEDGE_ID")
        sys.exit(1)

    # "state" is what Open WebUI currently has (remote_name -> file_id).
    # "local" is what's on disk (normalized_name -> full_path).
    state = fetch_state()
    local = scan_local_files()

    # Restructure state so we can look up by base key (without hash).
    # remote_name is e.g. "guide_a1b2c3d4e5.md", we split into ("guide", "a1b2c3d4e5").
    remote_by_key: dict[str, tuple[str, str, str]] = {}
    for remote_name, file_id in state.items():
        name_part, ext = os.path.splitext(remote_name)
        # Split on the last underscore to separate the base key from the hash.
        if "_" in name_part:
            base, remote_hash = name_part.rsplit("_", 1)
            base_key = f"{base}{ext}"
        else:
            # Legacy entry without hash, treat as always outdated.
            base_key = remote_name
            remote_hash = ""
        remote_by_key[base_key] = (file_id, remote_hash, remote_name)

    # First pass: upload new files, replace changed ones, skip unchanged ones.
    for key, path in local.items():
        if key not in remote_by_key:
            sync_added(path)
        else:
            file_id, remote_hash, remote_name = remote_by_key[key]
            local_hash = file_hash(path)
            if local_hash == remote_hash:
                print(f"[SKIP] {path} unchanged")
            else:
                sync_modified(path, file_id)

    # Second pass: anything in Open WebUI that no longer exists locally gets removed.
    for key, (file_id, _, remote_name) in remote_by_key.items():
        if key not in local:
            sync_deleted(key, file_id)


if __name__ == "__main__":
    main()