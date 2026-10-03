"""Re-sign verified existing Mac bundles and preserve corresponding source inputs."""
import hashlib
import io
import json
import os
import plistlib
import subprocess
import tarfile
import time
from pathlib import Path
from publish_clients import api, download, digest, validate_source, validate_binary, DRAFT

def run(*args):
    subprocess.run(args, check=True)

def launch(executable):
    # A real launch loads Flutter; --version exits before the GUI framework loads.
    with Path('startup.log').open('wb') as output:
        process = subprocess.Popen([str(executable)], stdout=output, stderr=output)
        try:
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    return process.returncode
                time.sleep(0.5)
            return None
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

def main():
    role = os.environ['CANDIDATE_ROLE']
    arch = os.environ['MAC_ARCH']
    assert role in ('customer', 'operator') and arch in ('arm64', 'x86_64')
    assert subprocess.check_output(['uname', '-m'], text=True).strip() == arch
    base = 'ArceusTechRemoteSupport' + ('Operator' if role == 'operator' else '')
    platform = 'macos-' + arch
    previous = 'macos-arm64' if arch == 'arm64' else 'macos-x64'
    release = api(f'releases/{DRAFT}')
    assert release['draft']
    assets = {item['name']:item for item in release['assets']}
    prefix = f'candidate-494d39c-{role}-{previous}-'
    source_name = f'{base}-macOS-{arch}-source.tar.gz'
    zip_name = f'{base}-macOS-{arch}.app.zip'
    incoming = Path('incoming'); incoming.mkdir()
    for name in (source_name, source_name+'.manifest.json', source_name+'.sha256', zip_name, 'SHA256SUMS.txt'):
        download(assets[prefix+name], incoming/name)
    expected = {line.split()[1].lstrip('*').removeprefix('./'):line.split()[0] for line in (incoming/'SHA256SUMS.txt').read_text(encoding='utf-8-sig').splitlines() if line.strip()}
    for name in (source_name, zip_name):
        assert digest(incoming/name) == expected[name]
    assert digest(incoming/source_name) == (incoming/(source_name+'.sha256')).read_text().split()[0]
    manifest = json.loads((incoming/(source_name+'.manifest.json')).read_text())
    validate_source(incoming/source_name, manifest, role=role)
    validate_binary(incoming/zip_name, platform)
    run('ditto', '-x', '-k', str(incoming/zip_name), 'bundle')
    apps = list(Path('bundle').glob('*.app')); assert len(apps) == 1
    app = apps[0]
    info = plistlib.loads((app/'Contents/Info.plist').read_bytes())
    executable = app/'Contents/MacOS'/info['CFBundleExecutable']
    before = launch(executable)
    old_error = Path('startup.log').read_text(errors='replace')
    report = {'role':role, 'architecture':arch, 'os':subprocess.check_output(['sw_vers','-productVersion'],text=True).strip(), 'original_launch_exit':before, 'original_team_id_error': 'different Team IDs' in old_error, 'gui_alive_seconds':15, 'remote_session_test':'not_performed', 'developer_id_signed':False, 'notarized':False}
    print('Original real-launch result:', before, 'Team ID error:', report['original_team_id_error'], flush=True)
    scripts = Path('sign-work'); scripts.mkdir()
    entitlements = None; old_signer = None; review = None
    signer_path = 'client/.github/scripts/sign-macos-app.sh'
    with tarfile.open(incoming/source_name, 'r|gz') as archive:
        for member in archive:
            relative = '/'.join(Path(member.name).parts[1:])
            if relative == signer_path:
                old_signer = archive.extractfile(member).read().decode()
            elif relative == 'client/flutter/macos/Runner/Release.entitlements':
                entitlements = archive.extractfile(member).read()
            elif relative == 'source-offer/resolved/REVIEW_REQUIRED.txt':
                review = archive.extractfile(member).read()
    assert old_signer and entitlements and review
    original = 'sign_args=(--force --options runtime --sign "$identity")\nif [[ "$identity" != "-" ]]; then\n  sign_args+=(--timestamp)\nfi'
    replacement = '# ArceusTech packaging fix: ad-hoc has no Apple Team ID for library validation.\n# Developer ID builds retain hardened runtime and timestamp.\nsign_args=(--force --options 0 --sign "$identity")\nif [[ "$identity" != "-" ]]; then\n  sign_args+=(--options runtime --timestamp)\nfi'
    assert old_signer.count(original) == 1
    fixed_signer = old_signer.replace(original, replacement).encode()
    (scripts/'sign.sh').write_bytes(fixed_signer)
    (scripts/'Release.entitlements').write_bytes(entitlements)
    run('bash', str(scripts/'sign.sh'), str(app), '-', str(scripts/'Release.entitlements'))
    signature = subprocess.check_output(['codesign','-d','--verbose=4',str(app)], stderr=subprocess.STDOUT,text=True)
    assert 'runtime' not in next(line for line in signature.splitlines() if line.startswith('CodeDirectory '))
    assert launch(executable) is None, 'Normal GUI launch exits prematurely after signing fix'
    assert 'different Team IDs' not in Path('startup.log').read_text(errors='replace')
    print('Corrected normal GUI launch stayed alive for 15 seconds', flush=True)
    run('codesign','--verify','--deep','--strict',str(app))
    dist = Path('dist'); dist.mkdir()
    run('ditto','-c','-k','--sequesterRsrc','--keepParent',str(app),str(dist/zip_name))
    validate_binary(dist/zip_name, platform)
    staging = Path('dmg-stage'); staging.mkdir()
    run('ditto',str(app),str(staging/app.name))
    (staging/'Applications').symlink_to('/Applications')
    for name in ('LICENSE','README_INSTALL.md'):
        original_doc = app/'Contents/Resources/OpenSource'/name
        if original_doc.exists():
            (staging/name).write_bytes(original_doc.read_bytes())
    run('hdiutil','create','-volname',app.stem,'-srcfolder',str(staging),'-format','UDZO','-ov',str(dist/f'{base}-macOS-{arch}.dmg'))
    # Preserve every source member, changing only the packaging signer.
    with tarfile.open(incoming/source_name,'r|gz') as source, tarfile.open(str(dist/source_name),'w|gz',compresslevel=6) as output:
        for member in source:
            if member.isfile():
                relative = '/'.join(Path(member.name).parts[1:])
                if relative == signer_path:
                    member.size = len(fixed_signer)
                    output.addfile(member, io.BytesIO(fixed_signer))
                    manifest[relative] = hashlib.sha256(fixed_signer).hexdigest()
                else:
                    output.addfile(member, source.extractfile(member))
            else:
                output.addfile(member)
    (dist/(source_name+'.manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n')
    (dist/(source_name+'.sha256')).write_text(f'{digest(dist/source_name)}  {source_name}\n')
    validate_source(dist/source_name,manifest,role=role)
    Path('source-offer/resolved').mkdir(parents=True)
    Path('source-offer/resolved/REVIEW_REQUIRED.txt').write_bytes(review)
    (dist/'SIGNING-VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
    (dist/'SHA256SUMS.txt').write_text(''.join(f'{digest(path)}  {path.name}\n' for path in sorted(dist.iterdir()) if path.name != 'SHA256SUMS.txt'))
    print('Verified Mac signing repair and matching source archive:', role, arch, flush=True)

if __name__ == '__main__':
    main()
