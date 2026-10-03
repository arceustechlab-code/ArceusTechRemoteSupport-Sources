# ArceusTech Remote Support — download e primo collegamento

Build del progetto: `494d39c40759098e568658cf5d877c2ea3f788ad`. Le nuove build conservano il logo ArceusTech e la configurazione del server aziendale. Non occorre caricare gli installer sul VPS: sul VPS restano hbbs e hbbr.

## Download

La [beta cliente](https://github.com/arceustechlab-code/ArceusTechRemoteSupport-Sources/releases/tag/v2026.10.03-client-beta-494d39c) diventa disponibile quando il processo di distribuzione ha completato i controlli. Il processo pubblica solo Windows 64 bit, macOS Apple Silicon e macOS Intel, con i rispettivi sorgenti e checksum. Fino ad allora il collegamento può restituire 404.

Gli operatori usano la [bozza privata dedicata](https://github.com/arceustechlab-code/ArceusTechRemoteSupport-Sources/releases/tag/operator-2026.10.03-494d39c), accessibile al titolare con GitHub autenticato dopo la preparazione dei pacchetti. La bozza non va pubblicata. Per distribuire un operatore a un collega, il titolare scarica il pacchetto corretto e glielo consegna direttamente.

Windows 32 bit è compilato per entrambi i profili e rimane interno in attesa della verifica di compatibilità Sciter/AGPL. Gli avvisi originali sono conservati. Non viene dichiarato pronto alla distribuzione pubblica.

## Installazione

- Windows: scegliere l'installer EXE oppure estrarre tutto lo ZIP portable nella stessa cartella. Il solo EXE portable non contiene tutte le dipendenze.
- Mac con chip M1/M2/M3/M4 e successivi: scegliere ARM64 / Apple Silicon. Mac Intel: scegliere x86_64.
- Mac: aprire il DMG, trascinare l'app in Applicazioni e avviarla da lì; concedere i permessi al profilo cliente quando richiesti.
- Le nuove build sostituiscono quelle scaricate prima dell'aggiornamento. Chiudere prima le app precedenti.
- Windows non è firmato; macOS usa firma ad-hoc e non è notarizzato. Verificare origine e checksum. Se macOS blocca l'apertura, usare i normali controlli di Privacy e sicurezza; non disattivare Gatekeeper o SIP.

## Prima sessione

1. Sul computer da assistere aprire la versione **cliente**.
2. Su Mac cliente concedere **Registrazione schermo** e **Accessibilità**, quindi riaprire l'app quando richiesto.
3. Premere **Avvia assistenza** e attendere lo stato pronto con ID e password temporanea.
4. Sul computer del tecnico aprire la versione **operatore**, inserire l'ID del cliente e usare la password temporanea attraverso il canale concordato.
5. Il cliente riconosce il tecnico e accetta la richiesta.
6. Verificare video, mouse, tastiera, clipboard, chat e trasferimento di un file di prova.
7. Premere **Termina assistenza** dal cliente e verificare che controllo e video cessino. Provare una nuova sessione e il rifiuto della vecchia password.

Il profilo cliente chiude l'accesso all'avvio; occorre premere Avvia assistenza per aprire la sessione. Lo stato Offline prima di avviare l'assistenza non basta a diagnosticare un guasto. Se resta Offline dopo l'avvio e dopo avere concesso i permessi Mac, registrare messaggio e stato senza cambiare manualmente server o chiave.

## Verifiche svolte e limiti

I 16 controlli locali del progetto passano. Il VPS ha risposto al protocollo TestNat su TCP 21115 e 21116; UDP 21116 ha risposto a una richiesta rifiutata senza registrare un dispositivo; il relay TCP 21117 è raggiungibile. [Esito del controllo protocollo](https://github.com/arceustechlab-code/ArceusTechRemoteSupport-Sources/actions/runs/37113079717).

La verifica della distribuzione controlla checksum, architetture dei pacchetti, configurazione aziendale nei sorgenti, presenza degli avvisi OSS, rimozione della dipendenza default_net e corrispondenza di ogni file dell'archivio sorgente al suo manifest. Una sessione remota completa tra computer Windows/Mac reali resta **NON ESEGUITA**: il test del protocollo non dimostra acquisizione schermo, controllo input o autenticazione di una sessione desktop.
