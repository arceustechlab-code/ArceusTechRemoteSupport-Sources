"""Stage verified session-stability operator builds in the existing private draft."""
import subprocess
import stage_operators as staging
import publish_session_clients as session

run = staging.api('actions/runs/' + str(session.RUN))
assert run['head_sha'] == session.HEAD and run['status'] == 'completed' and run['conclusion'] == 'success'
staging.ASSET_PLATFORM_ALIASES.update({p: p + '-credentials-ui-20261004' for p in ('windows-x64','macos-arm64','macos-x86_64')})
staging.validate_source = session.validate_session_source
staging.main()
notes = staging.Path('operator-packages/OPERATOR-DOWNLOADS.md')
notes.write_text("""Operatori ArceusTech Remote Support — aggiornamento 2026.10.04.

Bozza privata: Windows 64 bit e Mac Apple Silicon/Intel aggiornati con la richiesta di ID e password prima della connessione, barra leggibile con icone e nomi e firma Mac ad-hoc corretta. Il cliente conserva la password fino a Rigenera o chiusura dell’app, anche dopo un accesso o Stop/Start. Avvio GUI nativo verificato, sessione remota completa con i nuovi pacchetti ancora da collaudare. Windows nella sessione utente, senza passaggio automatico a SYSTEM. Nessuna firma Windows o notarizzazione macOS.

Windows 32 bit conserva la precedente build interna; non contiene questa correzione e la compatibilità della licenza Sciter resta irrisolta.

Per i clienti usare la release pubblica v2026.10.04-credentials-ui-beta. La bozza operatore resta privata. Installer, ZIP, sorgenti corrispondenti, avvisi OSS e checksum allegati.
""")
subprocess.run(['gh','release','upload',staging.TAG,str(notes),'--repo',staging.REPO,'--clobber'],check=True)
release = next(r for r in staging.api('releases?per_page=100') if r['tag_name'] == staging.TAG)
assert release['draft']
subprocess.run(['gh','release','edit',staging.TAG,'--repo',staging.REPO,'--notes-file',str(notes)],check=True)
assert staging.api('releases/' + str(release['id']))['draft']

