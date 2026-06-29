# embedding-pipeline

Syncs markdown files from a GitHub repository into an Open WebUI Knowledge Base for RAG retrieval.

## Setup

1. Set the following secrets in **GitHub > Settings > Secrets and variables > Actions**:

   | Secret | Description |
   |--------|-------------|
   | `OPEN_WEBUI_API_URL` | Base URL of the Open WebUI instance |
   | `OPEN_WEBUI_API_KEY` | API key for authentication |
   | `KNOWLEDGE_ID` | Target Knowledge Base ID |

2. Set `DOCS_DIR` in the workflow if your markdown files are not in `src/content/docs/`.

3. Push changes to `main` or trigger the workflow manually for an initial bulk upload.

## Approach

On every run the script:

1. Queries Open WebUI for all files currently in the Knowledge Base
2. Walks the local docs folder and collects all `.md` files
3. Compares local files against the remote state using a content hash embedded in the filename
4. Uploads new files, replaces changed files, removes deleted files, skips unchanged files
Chunking, embedding, and vector storage are handled by Open WebUI.

## Sync.py Function List

| Function | Task |
|---|---|
| `fetch_state()` | Asks Open WebUI: "What files do you already have?" Returns a list of filenames and their IDs. If the API is down, returns an empty list so the script does not crash. |
| `upload_file(path)` | Takes a local file, adds a content hash to its name (e.g. `guide_a1b2c3d4e5.md`), and uploads it to Open WebUI. Waits until Open WebUI finishes processing. Returns the new file ID, or None if something went wrong. |
| `add_to_knowledge(file_id)` | Tells Open WebUI: "Take this uploaded file and add it to the Knowledge Base." This is what triggers chunking and embedding on their side. |
| `remove_from_knowledge(file_id)` | Tells Open WebUI: "Remove this file from the Knowledge Base." Uses POST, not DELETE (Open WebUI returns 405 if you use DELETE). |
| `normalize_path(path)` | Turns a file path like `api/v2/reference.md` into a flat key like `api--v2--reference.md`. Slashes become `--`. This avoids name collisions between files in different folders. |
| `file_hash(path)` | Reads a file and returns a short fingerprint (10 characters). If the file content changes, the fingerprint changes. Used to detect whether a file needs re-uploading. |
| `scan_local_files()` | Walks through the docs folder and finds all `.md` files. Returns a dictionary mapping each normalized name to its full file path. |
| `sync_added(path)` | Handles a new file. Uploads it, then adds it to the Knowledge Base. |
| `sync_modified(path, old_id)` | Handles a changed file. Removes the old version first, then uploads the new one. Order matters because Open WebUI rejects duplicates. |
| `sync_deleted(key, file_id)` | Handles a deleted file. Removes it from the Knowledge Base. |
| `main()` | The entry point. Checks that env variables are set. Fetches the remote state. Scans local files. Compares both lists. Calls add/update/delete for each difference. |