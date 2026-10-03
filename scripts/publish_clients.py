"""Verify the existing native customer builds and publish an explicitly labelled beta.

Operator packages and Sciter/x86 packages remain in the original private draft.
No binaries are rebuilt or edited here.
"""
import hashlib
import json
import socket
import struct
import subprocess
import tarfile
import time
import zipfile
from pathlib import Path, PurePosixPath

REPO = 'arceustechlab-code/ArceusTechRemoteSupport-Sources'
RUN = 37109995106
DRAFT = 402397093
PREFIX = 'candidate-494d39c-customer-'
TAG = 'v2026.10.03-client-beta-494d39c'
PLATFORMS = {
    'windows-x64': ('ArceusTechRemoteSupport', ['-Setup.exe', '-Windows-x64.zip'], '-Windows-x64-source.tar.gz'),
    'macos-arm64': ('ArceusTechRemoteSupport', ['-macOS-arm64.dmg', '-macOS-arm64.app.zip'], '-macOS-arm64-source.tar.gz'),
    'macos-x86_64': ('ArceusTechRemoteSupport', ['-macOS-x86_64.dmg', '-macOS-x86_64.app.zip'], '-macOS-x86_64-source.tar.gz'),
}
ROOT = Path('verified-clients')


def api(path):
    return json.loads(subprocess.check_output(['gh', 'api', f'/repos/{REPO}/{path}'], text=True))


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def download(asset, target):
    with target.open('wb') as output:
        subprocess.run(['gh', 'api', f'/repos/{REPO}/releases/assets/{asset["id"]}', '-H', 'Accept: application/octet-stream'], stdout=output, check=True)
    assert target.stat().st_size == asset['size'], f'Truncated download: {target.name}'
    if asset.get('digest'):
        assert asset['digest'] == 'sha256:' + digest(target), f'GitHub digest mismatch: {target.name}'


def validate_source(archive, manifest, role='customer'):
    """Check every source byte without extracting untrusted paths."""
    found = set()
    documents = {}
    keys = ('config/public-build.json', 'source-offer/resolved/inventory.json', 'LICENSE', 'upstream-lock.json')
    with tarfile.open(archive, 'r|gz') as source:
        for member in source:
            parts = PurePosixPath(member.name).parts
            assert parts and parts[0] == 'ArceusTechRemoteSupport' and '..' not in parts, member.name
            if member.isdir():
                continue
            assert member.isfile(), f'Unexpected archive member: {member.name}'
            name = '/'.join(parts[1:])
            assert name in manifest and name not in found, f'Unexpected or duplicate source: {name}'
            found.add(name)
            stream = source.extractfile(member)
            if name in keys:
                content = stream.read()
                documents[name] = content
                actual = hashlib.sha256(content).hexdigest()
            else:
                actual = hashlib.file_digest(stream, 'sha256').hexdigest()
            assert actual == manifest[name], f'Source hash mismatch: {name}'
    assert found == set(manifest), 'Incomplete corresponding source'
    config = json.loads(documents['config/public-build.json'])
    assert config['ROLE'] == role and config['CONFIGURED'] is True
    assert config['ID_SERVER'] == '89.58.39.204:21116'
    assert config['RELAY_SERVER'] == '89.58.39.204:21117'
    assert config['PUBLIC_KEY'] == 'JQ9meE0iqQTmW3D18f9p6EjbB9PR2JtyN7vQ1j01DEw='
    assert config['SOURCE_URL'].startswith('https://github.com/' + REPO + '/releases')
    assert b'GNU AFFERO GENERAL PUBLIC LICENSE' in documents['LICENSE']
    inventory = json.loads(documents['source-offer/resolved/inventory.json'])
    assert len(inventory) > 500
    assert not any(item['review_required'] for item in inventory), 'Missing dependency notices'
    assert not any('default_net-' in item['component'] for item in inventory), 'Obsolete unlicensed dependency'
    assert any(name.startswith('work/dependency-sources/') for name in found), 'Dependency sources missing'
    assert any('bridge_generated.rs' in name for name in found), 'Generated bridge missing'
    return {'source_files': len(found), 'components_with_notices': len(inventory), 'config': config}


def validate_binary(path, platform):
    with zipfile.ZipFile(path) as bundle:
        assert bundle.testzip() is None, 'Corrupt application ZIP'
        names = bundle.namelist()
        assert not any('sciter' in name.lower() for name in names), 'Unexpected proprietary engine'
        license_names = [name for name in names if name.endswith('/LICENSE') or name == 'LICENSE']
        assert any(b'GNU AFFERO GENERAL PUBLIC LICENSE' in bundle.read(name) for name in license_names)
        notices = [name for name in names if name.endswith('THIRD-PARTY-LICENSES.txt')]
        assert notices and len(bundle.read(notices[0])) > 10000
        native = [name for name in names if name.endswith('liblibrustdesk.dylib')] if platform.startswith('macos') else [name for name in names if name.endswith('/ArceusTechRemoteSupport.exe') or name == 'ArceusTechRemoteSupport.exe']
        assert len(native) == 1, 'Native application missing or ambiguous'
        with bundle.open(native[0]) as stream:
            header = stream.read(4096)
        if platform.startswith('macos'):
            assert header[:4] == b'\xcf\xfa\xed\xfe', 'Not a 64-bit Mach-O'
            cpu = struct.unpack_from('<I', header, 4)[0]
            assert cpu == (0x100000C if platform == 'macos-arm64' else 0x1000007), 'Wrong macOS architecture'
        else:
            assert header[:2] == b'MZ'
            offset = struct.unpack_from('<I', header, 0x3c)[0]
            assert header[offset:offset+4] == b'PE\0\0' and struct.unpack_from('<H', header, offset+4)[0] == 0x8664, 'Wrong Windows architecture'


def main():
    ROOT.mkdir(exist_ok=True)
    # Continue the already-running build; never launch duplicate native builds.
    deadline = time.monotonic() + 2700
    while True:
        run = api(f'actions/runs/{RUN}')
        assert run['head_sha'] == 'f3acda446e75eb4266978e01db42bb6692c07ffa'
        if run['status'] == 'completed':
            assert run['conclusion'] == 'success', 'Existing native build failed; release left unpublished'
            break
        assert time.monotonic() < deadline, 'Native build still running; retry distribution after completion'
        print('Waiting for existing native build', RUN, flush=True)
        time.sleep(30)
    source_release = api(f'releases/{DRAFT}')
    assert source_release['draft'], 'Original internal release must remain private'
    assets = {asset['name']: asset for asset in source_release['assets']}
    report = {'source_commit': '494d39c40759098e568658cf5d877c2ea3f788ad', 'native_run': RUN, 'release_type': 'beta', 'remote_session_test': 'not_performed', 'windows_signed': False, 'macos_notarized': False, 'windows_x86': 'internal; Sciter licensing compatibility unresolved', 'platforms': {}}
    publish = []
    for platform, (base, binaries, source_suffix) in PLATFORMS.items():
        prefix = PREFIX + platform + '-'
        output_names = [base + suffix for suffix in binaries]
        source_name = base + source_suffix
        required = output_names + [source_name, source_name + '.manifest.json', source_name + '.sha256', 'SHA256SUMS.txt']
        folder = ROOT / platform
        folder.mkdir(exist_ok=True)
        for name in required:
            key = prefix + name
            assert key in assets, f'Expected build output missing: {key}'
            download(assets[key], folder / name)
        expected = dict((line.split()[1].lstrip('*').removeprefix('./'), line.split()[0]) for line in (folder / 'SHA256SUMS.txt').read_text(encoding='utf-8-sig').splitlines() if line.strip())
        for name in output_names + [source_name]:
            assert digest(folder / name) == expected[name], f'Build checksum mismatch: {name}'
        assert digest(folder / source_name) == (folder / (source_name + '.sha256')).read_text().split()[0]
        source_report = validate_source(folder / source_name, json.loads((folder / (source_name + '.manifest.json')).read_text()))
        zip_name = next(name for name in output_names if name.endswith('.zip'))
        validate_binary(folder / zip_name, platform)
        source_report['sha256'] = {name: digest(folder / name) for name in required if name != 'SHA256SUMS.txt'}
        report['platforms'][platform] = source_report
        publish.extend(folder / name for name in required if name != 'SHA256SUMS.txt')
        print('Verified', platform, source_report['source_files'], 'source files', flush=True)
    for port in (21115, 21116, 21117):
        with socket.create_connection(('89.58.39.204', port), timeout=10):
            pass
    report['server_tcp_ports'] = [21115, 21116, 21117]
    verification = ROOT / 'RELEASE-VERIFICATION.json'
    verification.write_text(json.dumps(report, indent=2) + '\n')
    checksums = ROOT / 'SHA256SUMS.txt'
    checksums.write_text(''.join(f'{digest(path)}  {path.name}\n' for path in publish + [verification]))
    notes = ROOT / 'RELEASE-NOTES.md'
    notes.write_text('''ArceusTech Remote Support — client beta, nuovo logo e server preconfigurato.

Download cliente: Windows 64 bit (installer o ZIP), macOS Apple Silicon e macOS Intel (DMG o app ZIP). Le versioni operatore restano private. Windows 32 bit resta interno in attesa della verifica di compatibilità della licenza Sciter.

Questa è una beta per il collaudo: compilazioni, architetture, checksum, sorgenti corrispondenti, avvisi OSS e porte TCP del server verificati. Una sessione remota completa fra due computer e i permessi di acquisizione/controllo macOS restano da verificare. Windows non firmato; macOS senza notarizzazione.

I sorgenti corrispondenti sono gli allegati specifici *-source.tar.gz. I link automatici “Source code” di GitHub contengono il repository dei download, non i sorgenti dell'app. Licenze e istruzioni di ricostruzione sono negli archivi. Non è dichiarata affiliazione con RustDesk.
''')
    # A separate customer release prevents any exposure of operator or old packages.
    existing = [release for release in api('releases?per_page=100') if release['tag_name'] == TAG]
    if existing:
        assert existing[0]['draft'], 'Release already public; refusing to replace published files'
    else:
        subprocess.run(['gh', 'release', 'create', TAG, '--repo', REPO, '--draft', '--prerelease', '--title', 'ArceusTech Remote Support — client beta 494d39c', '--notes-file', str(notes)], check=True)
    for path in publish + [verification, checksums]:
        subprocess.run(['gh', 'release', 'upload', TAG, str(path), '--repo', REPO, '--clobber'], check=True)
    release = next(release for release in api('releases?per_page=100') if release['tag_name'] == TAG)
    expected_names = {path.name for path in publish + [verification, checksums]}
    assert {asset['name'] for asset in release['assets']} == expected_names, 'Unexpected release contents'
    assert not any('Operator' in name or 'Windows-x86' in name for name in expected_names)
    subprocess.run(['gh', 'release', 'edit', TAG, '--repo', REPO, '--draft=false', '--prerelease', '--notes-file', str(notes)], check=True)
    print('Public customer beta:', f'https://github.com/{REPO}/releases/tag/{TAG}')


if __name__ == '__main__':
    main()
