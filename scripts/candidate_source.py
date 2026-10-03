"""Fetch the exact reviewed source archive; never extract unsafe members."""
import hashlib
import os
from pathlib import Path
import subprocess
import tarfile

ROOT = Path.cwd().resolve()
ARCHIVE = Path(os.environ['RUNNER_TEMP']) / 'arceus-source-494d39c.tar.gz'
with ARCHIVE.open('wb') as output:
    subprocess.run(['gh', 'api', '/repos/arceustechlab-code/ArceusTechRemoteSupport-Sources/releases/assets/607466771', '-H', 'Accept: application/octet-stream'], stdout=output, check=True)
assert hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == '5662d27b07ed2564f684d2bf8e3731e50baf4ec8842e4eed99655951d24e93bc', 'Source checksum mismatch'
with tarfile.open(ARCHIVE, 'r:gz') as archive:
    members = archive.getmembers()
    for member in members:
        parts = Path(member.name).parts
        assert parts and parts[0] == 'ArceusTechRemoteSupport', member.name
        target = ROOT.joinpath(*parts[1:]).resolve()
        assert target == ROOT or ROOT in target.parents, member.name
        assert member.isfile() or member.isdir(), member.name
    for member in members:
        member.name = str(Path(*Path(member.name).parts[1:]))
        archive.extract(member, ROOT, filter='data')
print('Verified source 494d39c extracted')
