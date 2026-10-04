"""Publish the three customer platforms only after the pinned native run passes."""
import hashlib
import json
import subprocess
import publish_clients as publisher

RUN = 37204249219
HEAD = 'cfea17d703e2915087e390ce5e846ad67b243fd3'
TAG = 'v2026.10.04-credentials-ui-beta'

def validate_session_source(archive, manifest, role='customer'):
    result = original_validate_source(archive, manifest, role)
    changes = json.loads(publisher.Path('scripts/session-fix-manifest.json').read_text())
    for path, change in changes.items():
        expected = hashlib.sha256(change['after_content'].encode()).hexdigest()
        assert manifest.get(path) == expected, 'Session fix missing: ' + path
    result['session_fix_files_verified'] = len(changes)
    return result

original_validate_source = publisher.validate_source

def configure():
    publisher.RUN = RUN
    publisher.EXPECTED_HEAD_SHA = HEAD
    publisher.PATCH_REVISION = HEAD
    publisher.PLATFORMS = {
        'windows-x64': ('ArceusTechRemoteSupport', ['-Setup.exe', '-Windows-x64.zip'], '-Windows-x64-source.tar.gz'),
        'macos-arm64': ('ArceusTechRemoteSupport', ['-macOS-arm64.dmg', '-macOS-arm64.app.zip'], '-macOS-arm64-source.tar.gz'),
        'macos-x86_64': ('ArceusTechRemoteSupport', ['-macOS-x86_64.dmg', '-macOS-x86_64.app.zip'], '-macOS-x86_64-source.tar.gz'),
    }
    publisher.ASSET_PLATFORM_ALIASES.update({platform: platform + '-credentials-ui-20261004' for platform in publisher.PLATFORMS})
    publisher.TAG = TAG
    publisher.validate_source = validate_session_source

if __name__ == '__main__':
    configure()
    publisher.main()
    notes = publisher.ROOT / 'RELEASE-NOTES.md'
    notes.write_text(notes.read_text() + """

Correzione della stabilità dell'assistenza: gli aggiornamenti con impostazioni vecchie non possono arrestare o riaprire la sessione cliente. La password visualizzata dopo Avvia è quella del motore locale; il controllo periodico non la rigenera nel profilo cliente. Avvio prima dell'inizializzazione rifiutato con messaggio; distinzione tra assistenza non avviata e connessione al server. La password cliente resta invariata durante la vita della finestra, anche dopo accessi, errori di autenticazione, Stop/Start o perdita di rete. Cambia solo con Rigenera o chiusura dell'app. Rigenera disconnette le sessioni esistenti; resta necessaria la conferma locale del cliente. L'operatore deve inserire ID e password prima della connessione, anche dai recenti. Barra della sessione con icone reali e nomi visibili.

Test del controller e della policy password superati, incluse 1.000 rotazioni automatiche bloccate, aggiornamenti vecchi, Stop/Start rapido e rigenerazione esplicita. Test Flutter per credenziali obbligatorie, annullamento, trasmissione esatta della password e testi/icona della barra superati. Avvio normale delle GUI verificato per 15 secondi nei runner nativi; questo non certifica una sessione remota completa sui dispositivi reali. Firma Mac ad-hoc corretta, nessuna notarizzazione.
""")
    subprocess.run(['gh','release','edit',TAG,'--repo',publisher.REPO,'--title','ArceusTech clienti — password stabile e nuova barra 2026.10.04','--notes-file',str(notes)],check=True)

