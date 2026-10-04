"""Publish the three customer platforms only after the pinned native run passes."""
import hashlib
import json
import subprocess
import publish_clients as publisher

RUN = 37213065132
HEAD = 'd9194f86a526d3173f89db4a3181ccd9ff5f4b0e'
TAG = 'v2026.10.04-mac-keyboard-panel-beta'

def validate_session_source(archive, manifest, role='customer'):
    result = original_validate_source(archive, manifest, role)
    changes = json.loads(publisher.Path('scripts/input-fix-manifest.json').read_text())
    for path, change in changes.items():
        expected = hashlib.sha256(change['after_content'].encode()).hexdigest()
        assert manifest.get(path) == expected, 'Session fix missing: ' + path
    result['session_fix_files_verified'] = len(changes)
    return result

original_validate_source = publisher.validate_source


def verify_build_provenance():
    run = publisher.api(f'actions/runs/{RUN}')
    assert run['head_sha'] == HEAD and run['status'] == 'completed' and run['conclusion'] == 'success'
    jobs = publisher.api(f'actions/runs/{RUN}/jobs?per_page=100')['jobs']
    native = [job for job in jobs if job['name'].startswith(('windows-x64 (', 'macos ('))]
    assert len(native) == 6 and all(job['conclusion'] == 'success' for job in native)
    assert all(any(step['name'] == 'Verify normal GUI startup' and step['conclusion'] == 'success' for step in job['steps']) for job in native)

def configure():
    verify_build_provenance()
    publisher.RUN = RUN
    publisher.EXPECTED_HEAD_SHA = HEAD
    publisher.PATCH_REVISION = HEAD
    publisher.PLATFORMS = {
        'windows-x64': ('ArceusTechRemoteSupport', ['-Setup.exe', '-Windows-x64.zip'], '-Windows-x64-source.tar.gz'),
        'macos-arm64': ('ArceusTechRemoteSupport', ['-macOS-arm64.dmg', '-macOS-arm64.app.zip'], '-macOS-arm64-source.tar.gz'),
        'macos-x86_64': ('ArceusTechRemoteSupport', ['-macOS-x86_64.dmg', '-macOS-x86_64.app.zip'], '-macOS-x86_64-source.tar.gz'),
    }
    publisher.ASSET_PLATFORM_ALIASES.update({platform: platform + '-mac-keyboard-panel-20261004' for platform in publisher.PLATFORMS})
    publisher.TAG = TAG
    publisher.validate_source = validate_session_source

if __name__ == '__main__':
    configure()
    publisher.main()
    notes = publisher.ROOT / 'RELEASE-NOTES.md'
    notes.write_text(notes.read_text() + """

Pannello cliente con area nativa di trascinamento esplicita, separata da Termina assistenza. Il collegamento resta attivo durante lo spostamento. Operatore Mac verso cliente Windows: Command sinistro/destro diventa Ctrl sinistro/destro anche sui clic modificati; Ctrl reale, Option/Alt e Shift restano invariati. La conversione avviene nel punto di invio per tutti i percorsi tastiera; testi Unicode non riscritti. Mac verso Mac e altri sistemi conservano la mappatura esistente; la scelta manuale di scambio modificatori resta prioritaria. Test Rust sulla policy, pressioni/rilasci, shortcut, Unicode e mouse e test Flutter sul trascinamento senza azionare Termina superati.

Correzione della stabilità dell'assistenza: gli aggiornamenti con impostazioni vecchie non possono arrestare o riaprire la sessione cliente. La password visualizzata dopo Avvia è quella del motore locale; il controllo periodico non la rigenera nel profilo cliente. Avvio prima dell'inizializzazione rifiutato con messaggio; distinzione tra assistenza non avviata e connessione al server. La password cliente resta invariata durante la vita della finestra, anche dopo accessi, errori di autenticazione, Stop/Start o perdita di rete. Cambia solo con Rigenera o chiusura dell'app. Rigenera disconnette le sessioni esistenti; resta necessaria la conferma locale del cliente. L'operatore deve inserire ID e password prima della connessione, anche dai recenti. Barra della sessione con icone reali e nomi visibili.

Test del controller e della policy password superati, incluse 1.000 rotazioni automatiche bloccate, aggiornamenti vecchi, Stop/Start rapido e rigenerazione esplicita. Test Flutter per credenziali obbligatorie, annullamento, trasmissione esatta della password e testi/icona della barra superati. Avvio normale delle GUI verificato per 15 secondi nei runner nativi; questo non certifica una sessione remota completa sui dispositivi reali. Firma Mac ad-hoc corretta, nessuna notarizzazione.
""")
    subprocess.run(['gh','release','edit',TAG,'--repo',publisher.REPO,'--title','ArceusTech clienti — pannello mobile e tastiera Mac 2026.10.04','--notes-file',str(notes)],check=True)

