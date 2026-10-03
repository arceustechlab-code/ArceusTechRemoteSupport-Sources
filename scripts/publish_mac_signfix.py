"""Distribute only verified Mac signing-repair customer packages."""
import publish_clients as publisher
publisher.RUN = 37120988692
publisher.EXPECTED_HEAD_SHA = '56b3dd93fa2f1d502bde5da1214eec853177de57'
publisher.PATCH_REVISION = '56b3dd93fa2f1d502bde5da1214eec853177de57'
publisher.ASSET_PLATFORM_ALIASES.update({'macos-arm64':'macos-arm64-signfix','macos-x86_64':'macos-x86_64-signfix'})
publisher.TAG = 'v2026.10.03-mac-signfix-beta'
publisher.main()
notes = publisher.ROOT / 'RELEASE-NOTES.md'
notes.write_text(notes.read_text() + '\nCorrezione firma ad-hoc: risolto il blocco del framework Flutter per Team ID. Avvio GUI normale mantenuto per 15 secondi sui runner macOS Tahoe ARM64/Intel. Questo non sostituisce il collaudo remoto sui dispositivi reali.\n')
publisher.subprocess.run(['gh','release','edit',publisher.TAG,'--repo',publisher.REPO,'--notes-file',str(notes)],check=True)
