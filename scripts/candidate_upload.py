"""Keep every native review package in the existing private draft release."""
import os
import json
from pathlib import Path
import subprocess
from urllib.parse import quote

role = os.environ['CANDIDATE_ROLE']
platform = os.environ['CANDIDATE_PLATFORM']
release = json.loads(subprocess.check_output(['gh', 'api', '/repos/arceustechlab-code/ArceusTechRemoteSupport-Sources/releases/402397093'], text=True))
assert release['draft'] is True, 'Refusing to expose internal native packages in a public release'
files = sorted(p for p in Path('dist').glob('*') if p.is_file() and (p.suffix in {'.exe', '.dmg', '.zip', '.gz', '.json', '.sha256'} or p.name == 'SHA256SUMS.txt'))
review = Path('source-offer/resolved/REVIEW_REQUIRED.txt')
if review.is_file():
    files.append(review)
assert files, 'No build output to upload'
for file in files:
    name = f'candidate-494d39c-{role}-{platform}-{file.name}'
    subprocess.run(['gh', 'api', '--method', 'POST', 'https://uploads.github.com/repos/arceustechlab-code/ArceusTechRemoteSupport-Sources/releases/402397093/assets?name=' + quote(name, safe=''), '-H', 'Content-Type: application/octet-stream', '--input', str(file), '--jq', '.name'], check=True)
