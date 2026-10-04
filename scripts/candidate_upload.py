"""Upload only the current role/platform to the existing internal draft, retrying transport failures."""
import os
import json
import time
from pathlib import Path
import subprocess
from urllib.parse import quote

role = os.environ['CANDIDATE_ROLE']
platform = os.environ['CANDIDATE_PLATFORM']
assert role in {'customer', 'operator'}
assert platform in {'macos-x86_64-credentials-ui-20261004', 'macos-arm64-credentials-ui-20261004', 'windows-x64-credentials-ui-20261004'}
endpoint = '/repos/arceustechlab-code/ArceusTechRemoteSupport-Sources/releases/402397093'
env = dict(os.environ, GODEBUG='http2client=0')
release = json.loads(subprocess.check_output(['gh', 'api', endpoint], text=True, env=env))
assert release['draft'] is True, 'Internal packages must stay in draft'
files = sorted(p for p in Path('dist').glob('*') if p.is_file() and (p.suffix in {'.exe', '.dmg', '.zip', '.gz', '.json', '.sha256'} or p.name == 'SHA256SUMS.txt'))
review = Path('source-offer/resolved/REVIEW_REQUIRED.txt')
if review.is_file():
    files.append(review)
assert files
for file in files:
    name = f'candidate-494d39c-{role}-{platform}-{file.name}'
    for attempt in range(5):
        # This exact internal candidate may have been partially uploaded by the failed attempt.
        current = json.loads(subprocess.check_output(['gh', 'api', endpoint], text=True, env=env))
        assert current['draft'] is True
        for asset in current['assets']:
            if asset['name'] == name:
                subprocess.run(['gh', 'api', '--method', 'DELETE', f"/repos/arceustechlab-code/ArceusTechRemoteSupport-Sources/releases/assets/{asset['id']}"], check=True, env=env)
        result = subprocess.run(['gh', 'api', '--method', 'POST', 'https://uploads.github.com/repos/arceustechlab-code/ArceusTechRemoteSupport-Sources/releases/402397093/assets?name=' + quote(name, safe=''), '-H', 'Content-Type: application/octet-stream', '--input', str(file), '--jq', '.name'], env=env)
        if result.returncode == 0:
            break
        if attempt == 4:
            raise RuntimeError(f'Upload failed after five attempts: {name}')
        time.sleep(5 * (attempt + 1))
