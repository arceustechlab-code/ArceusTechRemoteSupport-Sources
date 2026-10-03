# ArceusTech Remote Support — sorgenti e licenze

Sorgenti pubblici di ArceusTech Remote Support, basato su RustDesk e RustDesk Server OSS. Le licenze originali, incluse AGPL-3.0 e quelle delle dipendenze, sono conservate negli archivi.

## Sorgenti aggiornati

[Snapshot verificato 494d39c](https://github.com/arceustechlab-code/ArceusTechRemoteSupport-Sources/releases/tag/source-snapshot-494d39c): codice del progetto, logo aggiornato, configurazione pubblica del server, cataloghi degli avvisi originali e termini delle licenze dichiarate. La dipendenza default_net priva di licenza è stata rimossa. I 16 controlli locali sono riusciti. Manifest e SHA256 sono allegati; tutti i 1.121 file sono stati verificati contro il commit di sviluppo.

Scaricare l'allegato **source-snapshot-494d39c.tar.gz**. I collegamenti automatici “Source code” di GitHub contengono il repository che ospita i download, non il codice dell'applicazione.

## Pacchetti cliente e operatore

Le nuove compilazioni Windows 64 bit, macOS Apple Silicon, macOS Intel e Windows 32 bit sono in corso per entrambi i profili. Gli installer aggiornati non sono ancora pubblicati. I pacchetti nativi vengono salvati in una bozza interna per la verifica, senza esporre quelli operatore.

I pacchetti cliente pubblicati avranno archivi dei sorgenti delle dipendenze risolte, inventari delle licenze e checksum corrispondenti a ciascuna piattaforma. I vecchi binari non sono sostituiti dalla sola pubblicazione dei nuovi avvisi.

Per Windows 32 bit resta da chiarire la compatibilità della licenza del motore proprietario Sciter con AGPL; il relativo pacchetto rimane interno. Il test TCP del 3 ottobre 2026 è riuscito sulle porte configurate del server ID e del relay. La prova di una sessione remota completa sui computer destinatari resta da eseguire.

## Ricostruzione e licenze

Seguire README_BUILD.md nell'archivio. Lo snapshot contiene gli input del progetto; gli archivi completi delle dipendenze risolte saranno allegati alle rispettive release native. Lo snapshot preparatorio precedente source-snapshot-2ba909e resta disponibile.

Il repository di sviluppo rimane privato. Gli archivi pubblici escludono credenziali, chiavi private e dati runtime del VPS. Il codice, il branding e gli input pubblici necessari alla ricostruzione sono inclusi negli archivi.

Marchi e asset di terzi conservano i rispettivi titolari; non si dichiara affiliazione con RustDesk. L'identità ArceusTech/Arceustech appartiene al titolare del progetto.
