"""Download the most recent chapkit workspace artifact that holds a data.csv (CH-06).

Lists the service's artifacts (written to <out_dir>/artifacts.json for the record), then,
newest first (ids are ULIDs, so ordered by creation), downloads each through
`/api/v1/artifacts/{id}/$download` until one is a zip containing data.csv, and extracts
it to <out_dir>/workspace/. That file is the data the model's script was given.

Usage: fetch_last_workspace.py <base_url> <out_dir>
"""

import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

base, out = sys.argv[1].rstrip("/"), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
with urllib.request.urlopen(f"{base}/api/v1/artifacts") as r:
    summaries = json.load(r)
(out / "artifacts.json").write_text(json.dumps(summaries, indent=2))

for item in sorted(summaries, key=lambda s: s["id"], reverse=True):
    try:
        with urllib.request.urlopen(f"{base}/api/v1/artifacts/{item['id']}/$download") as r:
            blob = r.read()
        z = zipfile.ZipFile(io.BytesIO(blob))
    except Exception:
        continue
    if any(Path(n).name == "data.csv" for n in z.namelist()):
        z.extractall(out / "workspace")
        print(f"artifact {item['id']}: {len(z.namelist())} files extracted")
        break
else:
    sys.exit("no artifact with a data.csv found")
