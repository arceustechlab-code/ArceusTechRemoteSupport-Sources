"""Publish the three customer platforms only after the pinned native run passes."""
import hashlib
import json
import subprocess
import publish_clients as publisher

RUN = 37209126360
HEAD = '368cf230b65256ebfd354fdd2dfdca72ac210364'
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


def verify_build_provenance():
    """Reuse five successful jobs; the sixth is rebuilt only for upload transport recovery."""
    prior = publisher.api('actions/runs/37204249219')
    assert prior['head_sha'] == 'cfea17d703e2915087e390ce5e846ad67b243fd3'
    assert prior['status'] == 'completed' and prior['conclusion'] == 'failure'
    jobs = publisher.api('actions/runs/37204249219/jobs?per_page=100')['jobs']
    required = {'windows-x64 (customer)', 'windows-x64 (operator)', 'macos (customer, arm64)', 'macos (operator, arm64)', 'macos (operator, x86_64)'}
    by_name = {job['name']: job for job in jobs}
    assert required <= by_name.keys()
    assert all(by_name[name]['conclusion'] == 'success' for name in required)
    failed = [job for job in jobs if job['conclusion'] == 'failure']
    assert len(failed) == 1 and failed[0]['name'] == 'macos (customer, x86_64)'
    assert [s['name'] for s in failed[0]['steps'] if s['conclusion'] == 'failure'] == ['Save native packages to private draft only']
    assert any(s['name'] == 'Verify normal GUI startup' and s['conclusion'] == 'success' for s in failed[0]['steps'])
    new = publisher.api(f'actions/runs/{RUN}')
    assert new['head_sha'] == HEAD and new['status'] == 'completed' and new['conclusion'] == 'success'
    recovered = publisher.api(f'actions/runs/{RUN}/jobs?per_page=100')['jobs']
    assert any(job['name'].startswith('macos (customer, x86_64,') and job['conclusion'] == 'success' for job in recovered)
    assert any(job['name'] == 'session-tests' and job['conclusion'] == 'success' for job in recovered)
    for path in ['scripts/session-fix-manifest.json', 'scripts/apply_session_fix.py']:
        original = publisher.api('contents/' + path + '?ref=cfea17d703e2915087e390ce5e846ad67b243fd3')
        recovery = publisher.api('contents/' + path + '?ref=' + HEAD)
        assert original['sha'] == recovery['sha'], 'Recovery must not change application sources'

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

