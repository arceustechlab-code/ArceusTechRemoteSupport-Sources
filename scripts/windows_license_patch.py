"""Apply the authorized standard-user Windows profile to the pinned source.

No SYSTEM impersonation helper is linked. Normal user-session support remains.
Only upstream-declared Boost terms and original embedded NVIDIA header grants
are collected; this does not assign a license to an unlicensed dependency.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path.cwd()


def main():
    manifest = ROOT / 'client/Cargo.toml'
    old = 'impersonate_system = { git = "https://github.com/rustdesk-org/impersonate-system" }'
    data = manifest.read_text()
    assert data.count(old) == 1
    manifest.write_text(data.replace(old + '\n', ''))
    lock = ROOT / 'client/Cargo.lock'
    data = lock.read_text()
    parts = data.split('[[package]]')
    removed = [block for block in parts[1:] if re.search(r'^name = "impersonate_system"$', block, re.M)]
    assert len(removed) == 1
    data = parts[0] + ''.join('[[package]]' + block for block in parts[1:] if block not in removed)
    assert data.count(' "impersonate_system",\n') == 1
    lock.write_text(data.replace(' "impersonate_system",\n', ''))
    platform = ROOT / 'client/src/platform/windows.rs'
    data = platform.read_text()
    pattern = r'pub fn run_as_system\(arg: &str\) -> ResultType<\(\)> \{.*?\n\}'
    replacement = '''// ArceusTech modification: standard-user profile, 2026-10-03.
pub fn run_as_system(_arg: &str) -> ResultType<()> {
    bail!("SYSTEM execution is not included in the ArceusTech standard-user support profile")
}'''
    data, count = re.subn(pattern, lambda _: replacement, data, flags=re.S)
    assert count == 1 and 'impersonate_system::' not in data
    platform.write_text(data)
    terms = ROOT / 'source-offer/declared-license-terms.json'
    registry = json.loads(terms.read_text())
    bsl = ROOT / 'scripts/BSL-1.0.txt'
    text = bsl.read_text()
    assert 'Boost Software License' in text
    registry['licenses']['BSL-1.0'] = {'url': 'https://raw.githubusercontent.com/spdx/license-list-data/31ba1a50e5397e00a304dbadc76531740e89ee48/text/BSL-1.0.txt', 'text': text, 'sha256': hashlib.sha256(text.encode()).hexdigest()}
    terms.write_text(json.dumps(registry, indent=2) + '\n')
    helper = ROOT / 'scripts/verified_notices.py'
    data = helper.read_text()
    needle = "    path = Path(path)\n    target = ROOT / 'source-offer/resolved/recovered' / label\n"
    assert data.count(needle) == 1
    extra = '''    # Preserve the complete original permissive grants embedded in NV codec headers.
    if label == 'vcpkg/ffnvcodec':
        paths = []
        provenance = []
        for header in sorted(path.rglob('*.h')):
            source = header.read_text(encoding='utf-8')
            if not source.lstrip().startswith('/*'):
                continue
            grant = source[source.index('/*'):source.index('*/') + 2] + '\\n'
            if 'Permission is hereby granted' not in grant or 'THE SOFTWARE IS PROVIDED' not in grant:
                continue
            target.mkdir(parents=True, exist_ok=True)
            output = target / ('LICENSE-header-' + header.name + '.txt')
            output.write_text(grant, encoding='utf-8')
            paths.append(output)
            provenance.append({'method': 'original embedded header grant', 'source': str(header.relative_to(path)), 'header_sha256': hashlib.sha256(header.read_bytes()).hexdigest(), 'grant_sha256': hashlib.sha256(grant.encode()).hexdigest()})
        if paths:
            (target / 'PROVENANCE.json').write_text(json.dumps(provenance, indent=2) + '\\n')
        return paths
'''
    data = data.replace(needle, needle + extra)
    data = data.replace("choices = {'MIT': 'MIT'", "choices = {'BSL-1.0': 'BSL-1.0', 'MIT': 'MIT'")
    helper.write_text(data)
    doc = ROOT / 'docs/WINDOWS_STANDARD_USER.md'
    doc.write_text('''# Windows standard-user support profile

Authorized on 3 October 2026: normal user-session remote support; no automatic SYSTEM impersonation. The impersonate_system dependency and its sole call are removed. Existing normal UAC code remains, but SYSTEM bootstrap is unavailable. Protected desktops, the sign-in screen and some UAC/admin windows cannot be controlled remotely in this profile.

Upstream-declared BSL-1.0 terms are included with the original manifests of clipboard-win and error-code. Original embedded permissive grants from NVIDIA codec headers are preserved. No license is invented for impersonate_system. Server identity, remote protocol, logo and profile separation remain unchanged. Native builds and actual remote-session tests determine runtime status.
''')
    print('Standard-user Windows source prepared; SYSTEM helper removed; original/declared notices retained.')


if __name__ == '__main__':
    main()
