"""Stage current operator packages under clean filenames in a private draft only."""
import json
import subprocess
import struct
import zipfile
import time
from pathlib import Path
from publish_clients import REPO, RUN, DRAFT, api, digest, download, validate_source, validate_binary

TAG = 'operator-2026.10.03-494d39c'
BASE = 'ArceusTechRemoteSupportOperator'
ASSET_PLATFORM_ALIASES = {'macos-x86_64': 'macos-x64', 'windows-x64': 'windows-x64-licensefix', 'windows-x86': 'windows-x86-licensefix'}
PACKAGES = {
    'windows-x64': ['-Setup.exe', '-Windows-x64.zip'],
    'windows-x86': ['-Windows-x86-Setup.exe', '-Windows-x86.zip'],
    'macos-arm64': ['-macOS-arm64.dmg', '-macOS-arm64.app.zip'],
    'macos-x86_64': ['-macOS-x86_64.dmg', '-macOS-x86_64.app.zip'],
}


def main():
    deadline = time.monotonic() + 2700
    while True:
        run = api(f'actions/runs/{RUN}')
        assert run['head_sha'] == 'f3acda446e75eb4266978e01db42bb6692c07ffa'
        if run['status'] == 'completed':
            assert run['conclusion'] == 'success', 'Native build failed'
            break
        assert time.monotonic() < deadline, 'Native build still in progress'
        print('Waiting for existing operator native builds', flush=True)
        time.sleep(30)
    while True:
        windows = api('actions/runs/37115254879')
        assert windows['head_sha'] == '2fb14423c0af98444380ddb54615e17edd9c958d'
        if windows['status'] == 'completed':
            assert windows['conclusion'] == 'success', 'Remediated Windows builds must succeed'
            break
        assert time.monotonic() < deadline, 'Windows builds still in progress'
        print('Waiting for existing Windows operator native builds', flush=True)
        time.sleep(30)
    internal = api(f'releases/{DRAFT}')
    assert internal['draft'], 'Candidate release must remain private'
    assets = {asset['name']: asset for asset in internal['assets']}
    root = Path('operator-packages')
    root.mkdir(exist_ok=True)
    files = []
    for platform, suffixes in PACKAGES.items():
        prefix = 'candidate-494d39c-operator-' + ASSET_PLATFORM_ALIASES.get(platform, platform) + '-'
        source = BASE + '-' + ({'windows-x64': 'Windows-x64', 'windows-x86': 'Windows-x86', 'macos-arm64': 'macOS-arm64', 'macos-x86_64': 'macOS-x86_64'}[platform]) + '-source.tar.gz'
        names = [BASE + suffix for suffix in suffixes] + [source, source + '.manifest.json', source + '.sha256', 'SHA256SUMS.txt', 'REVIEW_REQUIRED.txt']
        folder = root / platform
        folder.mkdir(exist_ok=True)
        for name in names:
            assert prefix + name in assets, prefix + name
            download(assets[prefix + name], folder / name)
        expected = dict((line.split()[1].lstrip('*').removeprefix('./'), line.split()[0]) for line in (folder / 'SHA256SUMS.txt').read_text(encoding='utf-8-sig').splitlines() if line.strip())
        for name in [BASE + suffix for suffix in suffixes] + [source]:
            assert digest(folder / name) == expected[name], name
        assert digest(folder / source) == (folder / (source + '.sha256')).read_text().split()[0]
        if platform != 'windows-x86':
            validate_source(folder / source, json.loads((folder / (source + '.manifest.json')).read_text()), role='operator')
        if platform.startswith('macos'):
            validate_binary(folder / (BASE + suffixes[1]), platform)
        elif platform == 'windows-x64':
            with zipfile.ZipFile(folder / (BASE + suffixes[1])) as bundle:
                assert bundle.testzip() is None, 'Corrupt Windows operator ZIP'
                assert not any('sciter' in name.lower() for name in bundle.namelist())
                executable = [name for name in bundle.namelist() if name == BASE + '.exe' or name.endswith('/' + BASE + '.exe')]
                assert len(executable) == 1, 'Operator executable missing or ambiguous'
                with bundle.open(executable[0]) as stream:
                    header = stream.read(4096)
                assert header[:2] == b'MZ'
                offset = struct.unpack_from('<I', header, 0x3c)[0]
                assert header[offset:offset+4] == b'PE\0\0'
                assert struct.unpack_from('<H', header, offset+4)[0] == 0x8664

        # Preserve the native review notes instead of claiming real-session validation.
        review = folder / (platform + '-REVIEW_REQUIRED.txt')
        review.write_bytes((folder / 'REVIEW_REQUIRED.txt').read_bytes())
        files.extend(folder / name for name in names if name not in ('SHA256SUMS.txt', 'REVIEW_REQUIRED.txt'))
        files.append(review)
        print('Verified operator build checksums:', platform, flush=True)
    checksums = root / 'SHA256SUMS.txt'
    checksums.write_text(''.join(f'{digest(path)}  {path.name}\n' for path in files))
    notes = root / 'OPERATOR-DOWNLOADS.md'
    notes.write_text('''Operatori ArceusTech Remote Support — build 494d39c con nuovo logo e server preconfigurato.

Bozza privata per il titolare del repository: Windows 64/32 bit nella sessione utente e macOS Apple Silicon/Intel. Windows non include il passaggio automatico a SYSTEM; alcune finestre UAC e schermate protette non sono controllabili remotamente. Installer, ZIP, sorgenti corrispondenti e checksum inclusi. Windows 32 bit resta interno: compatibilità Sciter/AGPL non risolta. Avvisi di revisione originali allegati. Nessuna firma Windows o notarizzazione macOS; sessioni remote reali da collaudare.

Per i clienti usare esclusivamente le release cliente separate v2026.10.03-client-beta-494d39c (Mac) e v2026.10.03-windows-user-beta (Windows 64 bit). Questa bozza operatore non deve essere pubblicata.
''')
    existing = [release for release in api('releases?per_page=100') if release['tag_name'] == TAG]
    if existing:
        assert existing[0]['draft'], 'Operator release must stay private'
    else:
        subprocess.run(['gh', 'release', 'create', TAG, '--repo', REPO, '--draft', '--prerelease', '--title', 'ArceusTech operatori — 494d39c (privato)', '--notes-file', str(notes)], check=True)
    for path in files + [checksums, notes]:
        subprocess.run(['gh', 'release', 'upload', TAG, str(path), '--repo', REPO, '--clobber'], check=True)
    release = next(release for release in api('releases?per_page=100') if release['tag_name'] == TAG)
    assert release['draft'] is True
    assert {asset['name'] for asset in release['assets']} == {path.name for path in files + [checksums, notes]}
    print('Operator packages staged in PRIVATE draft:', release['html_url'])


if __name__ == '__main__':
    main()
