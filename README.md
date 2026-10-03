# ArceusTech Remote Support — sorgenti e licenze

Sorgenti pubblici di ArceusTech Remote Support, basato su RustDesk e RustDesk Server OSS. Le licenze originali, incluse AGPL-3.0 e quelle delle dipendenze, sono conservate negli archivi.

## Sorgenti aggiornati

[Snapshot verificato 494d39c](https://github.com/arceustechlab-code/ArceusTechRemoteSupport-Sources/releases/tag/source-snapshot-494d39c): codice del progetto, logo aggiornato, configurazione pubblica del server, cataloghi degli avvisi originali e termini delle licenze dichiarate. La dipendenza default_net priva di licenza è stata rimossa. I 16 controlli locali sono riusciti. Manifest e SHA256 sono allegati; tutti i 1.121 file sono stati verificati contro il commit di sviluppo.

Scaricare l'allegato **source-snapshot-494d39c.tar.gz**. I collegamenti automatici “Source code” di GitHub contengono il repository che ospita i download, non il codice dell'applicazione.

## Pacchetti cliente e operatore

Sono pubblicate le beta cliente con nuovo logo e server aziendale preconfigurato:

- [Windows 64 bit — installer](https://github.com/arceustechlab-code/ArceusTechRemoteSupport-Sources/releases/download/v2026.10.03-windows-user-beta/ArceusTechRemoteSupport-Setup.exe)
- [macOS Apple Silicon — DMG](https://github.com/arceustechlab-code/ArceusTechRemoteSupport-Sources/releases/download/v2026.10.03-client-beta-494d39c/ArceusTechRemoteSupport-macOS-arm64.dmg)
- [macOS Intel — DMG](https://github.com/arceustechlab-code/ArceusTechRemoteSupport-Sources/releases/download/v2026.10.03-client-beta-494d39c/ArceusTechRemoteSupport-macOS-x86_64.dmg)

Le release [Windows](https://github.com/arceustechlab-code/ArceusTechRemoteSupport-Sources/releases/tag/v2026.10.03-windows-user-beta) e [Mac](https://github.com/arceustechlab-code/ArceusTechRemoteSupport-Sources/releases/tag/v2026.10.03-client-beta-494d39c) contengono ZIP, archivi completi dei sorgenti delle dipendenze risolte, inventari delle licenze e checksum verificati. Windows usa la normale sessione utente, senza passaggio automatico a SYSTEM: alcune finestre UAC e schermate protette non sono controllabili remotamente. I pacchetti operatore restano privati.

Tutte e quattro le build Windows cliente/operatore 64/32 bit aggiornate sono riuscite. Nessuna firma Windows o notarizzazione Mac. Le beta richiedono ancora il collaudo di una sessione reale su due computer; seguire [download e primo collegamento](GETTING-STARTED.md).

Per Windows 32 bit resta da chiarire la compatibilità della licenza del motore proprietario Sciter con AGPL; il relativo pacchetto rimane interno. Il test TCP del 3 ottobre 2026 è riuscito sulle porte configurate del server ID e del relay. La prova di una sessione remota completa sui computer destinatari resta da eseguire.

## Ricostruzione e licenze

Seguire README_BUILD.md nell'archivio. Lo snapshot contiene gli input del progetto; gli archivi completi delle dipendenze risolte saranno allegati alle rispettive release native. Lo snapshot preparatorio precedente source-snapshot-2ba909e resta disponibile.

Il repository di sviluppo rimane privato. Gli archivi pubblici escludono credenziali, chiavi private e dati runtime del VPS. Il codice, il branding e gli input pubblici necessari alla ricostruzione sono inclusi negli archivi.

Marchi e asset di terzi conservano i rispettivi titolari; non si dichiara affiliazione con RustDesk. L'identità ArceusTech/Arceustech appartiene al titolare del progetto.
