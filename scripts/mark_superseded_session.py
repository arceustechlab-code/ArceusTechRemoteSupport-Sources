"""Mark the previous customer beta as superseded only after the new downloads are public."""
import json
import subprocess
from pathlib import Path
from publish_clients import api, REPO
from publish_session_clients import TAG

current = api('releases/tags/' + TAG)
assert not current['draft'] and current['prerelease']
required = {'ArceusTechRemoteSupport-Setup.exe','ArceusTechRemoteSupport-macOS-arm64.dmg','ArceusTechRemoteSupport-macOS-x86_64.dmg'}
assert required <= {a['name'] for a in current['assets']}
previous = api('releases/tags/v2026.10.04-session-beta')
assert not previous['draft']
header = f"SUPERATA: usare la [nuova beta con password stabile, ID/password obbligatori e barra leggibile](https://github.com/{REPO}/releases/tag/{TAG}).\\n\\n".replace('\\n','\n')
body = previous['body'] or ''
if not body.startswith(header):
    body = header + body
notes = Path('superseded-session-notes.md')
notes.write_text(body)
subprocess.run(['gh','release','edit',previous['tag_name'],'--repo',REPO,'--title','SUPERATA — ArceusTech clienti 2026.10.04 session beta','--notes-file',str(notes)],check=True)
