"""Apply reviewed session fixes only to the exact original source blobs."""
import hashlib
import json
from pathlib import Path

def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

root = Path.cwd()
manifest = json.loads((root / 'scripts/session-fix-manifest.json').read_text())
for name, entry in manifest.items():
    path = root / name
    if entry['before'] is None:
        assert not path.exists(), 'Unexpected existing source: ' + name
        path.parent.mkdir(parents=True, exist_ok=True)
    else:
        assert git_blob(path.read_bytes()) == entry['before'], 'Unexpected source: ' + name
    path.write_bytes(entry['after_content'].encode())
print('Reviewed session fix applied to', len(manifest), 'exact source files.')
