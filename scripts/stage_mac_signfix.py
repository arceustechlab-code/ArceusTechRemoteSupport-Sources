"""Replace only private operator draft Mac packages with verified signing repairs."""
import time
import subprocess
import stage_operators as staging
deadline = time.monotonic() + 2700
while True:
    run = staging.api('actions/runs/37120988692')
    assert run['head_sha'] == '56b3dd93fa2f1d502bde5da1214eec853177de57'
    if run['status'] == 'completed':
        assert run['conclusion'] == 'success', 'Mac repair must pass before operator staging'
        break
    assert time.monotonic() < deadline
    print('Waiting for existing Mac signing repair', flush=True)
    time.sleep(30)
staging.ASSET_PLATFORM_ALIASES.update({'macos-arm64':'macos-arm64-signfix','macos-x86_64':'macos-x86_64-signfix'})
staging.main()
notes = staging.Path('operator-packages/OPERATOR-DOWNLOADS.md')
notes.write_text(notes.read_text() + '\nPacchetti Mac corretti per errore Flutter Team ID; avvio GUI di 15 secondi verificato su runner macOS Tahoe. Bozza privata; nessuna notarizzazione.\n')
subprocess.run(['gh','release','upload',staging.TAG,str(notes),'--repo',staging.REPO,'--clobber'],check=True)
release = next(r for r in staging.api('releases?per_page=100') if r['tag_name'] == staging.TAG)
assert release['draft']
subprocess.run(['gh','release','edit',staging.TAG,'--repo',staging.REPO,'--notes-file',str(notes)],check=True)
assert staging.api('releases/' + str(release['id']))['draft']
