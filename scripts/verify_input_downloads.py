"""Verify anonymous downloads, then update only public customer documentation."""
import base64
import json
import subprocess
import urllib.request
from publish_input_clients import TAG
from publish_clients import REPO, api

release = next(r for r in api('releases?per_page=100') if r['tag_name'] == TAG)
assert not release['draft'] and release['prerelease']
assets = {a['name']: a for a in release['assets']}
names = ['ArceusTechRemoteSupport-Setup.exe', 'ArceusTechRemoteSupport-macOS-arm64.dmg', 'ArceusTechRemoteSupport-macOS-x86_64.dmg']
for name in names:
    asset = assets[name]
    request = urllib.request.Request(asset['browser_download_url'], method='HEAD')
    with urllib.request.urlopen(request, timeout=60) as response:
        assert response.status == 200
        assert int(response.headers['Content-Length']) == asset['size']
    print('Anonymous download verified:', name)
for path in ['README.md','GETTING-STARTED.md']:
    data = api('contents/' + path)
    text = base64.b64decode(data['content']).decode()
    for old in ['v2026.10.03-windows-user-beta','v2026.10.03-mac-signfix-beta','v2026.10.04-session-beta','v2026.10.04-credentials-ui-beta']:
        text = text.replace(old, TAG)
    paragraphs = text.split('\n\n')
    assert paragraphs[0].startswith('# ArceusTech Remote Support')
    paragraphs[1] = ("Aggiornamento del 4 ottobre: pannello cliente spostabile dalla maniglia Trascina qui per spostare il pannello. Operatore Mac verso Windows: Command diventa Ctrl per selezione, copia/incolla e altri shortcut, anche sui clic modificati; Ctrl reale, Option/Alt e Shift invariati. Password stabile fino a Rigenera o chiusura dell’app; ID e password obbligatori prima della connessione; consenso locale mantenuto. Test di regressione e avvio GUI nativo superati; collaudo remoto completo dei nuovi pacchetti sui dispositivi reali ancora da eseguire. Windows non firmato e Mac con firma ad-hoc, senza notarizzazione.")
    text = '\n\n'.join(paragraphs)
    if path == 'GETTING-STARTED.md':
        text = text.replace("Offline prima dell'avvio non basta a diagnosticare un guasto. Se resta Offline dopo l'avvio e i permessi Mac, registrare il messaggio senza cambiare manualmente la configurazione aziendale.", "Prima dell'avvio appare Assistenza non avviata. Dopo Avvia attendere Pronto prima di copiare la password. Connessione al server prolungata indica un problema da verificare senza cambiare manualmente la configurazione aziendale. L’operatore inserisce ID e password prima di Connetti, poi il cliente accetta la richiesta sullo schermo. La password resta uguale fino a Rigenera o chiusura dell’app; Termina assistenza e Avvia non la cambiano. Rigenera chiude le connessioni esistenti.")
    text = text.replace("La richiesta della password segue il contatto iniziale con l'ID: l'accesso al desktop richiede autenticazione e consenso. La password monouso cambia dopo un accesso autorizzato.", 'L’operatore inserisce ID e password prima di Connetti, poi il cliente accetta la richiesta sullo schermo. La password resta uguale fino a Rigenera o chiusura dell’app; Termina assistenza e Avvia non la cambiano. Rigenera chiude le connessioni esistenti.')
    payload = json.dumps({'message':'Point public customer downloads to verified session-stability beta','sha':data['sha'],'content':base64.b64encode(text.encode()).decode()}).encode()
    subprocess.run(['gh','api','--method','PUT','/repos/' + REPO + '/contents/' + path,'--input','-','--jq','.commit.sha'],input=payload,check=True)

