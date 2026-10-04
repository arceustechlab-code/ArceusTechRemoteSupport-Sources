# ArceusTech Remote Support — download e primo collegamento

Aggiornamento del 4 ottobre: corretta la sincronizzazione dello stato dell'assistenza e della password cliente. Gli aggiornamenti con impostazioni vecchie non arrestano o riaprono la sessione e il controllo periodico non rigenera la password. Password stabile fino a Rigenera o chiusura dell’app, anche dopo un accesso, Stop/Start o perdita di rete. Consenso locale richiesto; operatore con ID e password prima della connessione e barra della sessione con icone e nomi leggibili. Test del controller e avvio GUI nei runner nativi superati; collaudo remoto completo dei nuovi pacchetti sui dispositivi reali ancora da eseguire. Windows non firmato e Mac con firma ad-hoc, senza notarizzazione.

## Download cliente

- [Windows 64 bit](https://github.com/arceustechlab-code/ArceusTechRemoteSupport-Sources/releases/tag/v2026.10.04-credentials-ui-beta): installer EXE e ZIP portable.
- [Mac Apple Silicon e Intel — pacchetti corretti](https://github.com/arceustechlab-code/ArceusTechRemoteSupport-Sources/releases/tag/v2026.10.04-credentials-ui-beta): DMG e app ZIP.

Logo aggiornato e server aziendale preconfigurato. Ogni release contiene sorgenti corrispondenti, avvisi OSS e checksum. I pacchetti operatore sono distribuiti separatamente dal titolare. Windows 32 bit è compilato, ma resta interno per la compatibilità Sciter/AGPL ancora da verificare.

## Installazione

- Windows: usare l'installer EXE oppure estrarre tutto lo ZIP portable nella stessa cartella.
- Mac con chip M1/M2/M3/M4 e successivi: scegliere ARM64 / Apple Silicon. Mac Intel: scegliere x86_64.
- Mac: chiudere l'app precedente, aprire il nuovo DMG e trascinare l'app in Applicazioni, confermando la sostituzione. Avviare dalla cartella Applicazioni.
- Windows non è firmato; Mac è firmato ad-hoc e non notarizzato. Verificare origine e checksum. Se Mac blocca l'apertura, usare Apri comunque in Impostazioni di Sistema → Privacy e sicurezza.
- Windows usa la normale sessione utente: alcune finestre UAC/amministratore e schermate protette possono restare fuori dal controllo remoto.

## Prima sessione

1. Sul computer da assistere aprire la versione cliente.
2. Su Mac concedere Registrazione schermo e Accessibilità, quindi riaprire l'app quando richiesto.
3. Premere Avvia assistenza e attendere lo stato pronto con ID e password temporanea.
4. Il tecnico apre la versione operatore, inserisce l'ID e usa la password temporanea attraverso il canale concordato.
5. Il cliente riconosce il tecnico e accetta la richiesta.
6. Verificare video, mouse, tastiera, clipboard, chat e trasferimento di un file di prova.
7. Premere Termina assistenza dal cliente e verificare che controllo e video cessino. Provare una nuova sessione e il rifiuto della vecchia password.

Il profilo cliente chiude l'accesso all'avvio: occorre premere Avvia assistenza. Prima dell'avvio appare Assistenza non avviata. Dopo Avvia attendere Pronto prima di copiare la password. Connessione al server prolungata indica un problema da verificare senza cambiare manualmente la configurazione aziendale. L’operatore inserisce ID e password prima di Connetti, poi il cliente accetta la richiesta sullo schermo. La password resta uguale fino a Rigenera o chiusura dell’app; Termina assistenza e Avvia non la cambiano. Rigenera chiude le connessioni esistenti.

## Verifiche e limiti

Checksum, architetture, configurazione preimpostata, avvisi OSS e ogni file degli archivi sorgenti sono verificati. La correzione della firma conserva le funzioni e i controlli di consenso del programma.

Avvio sul computer destinatario e sessione remota completa restano da confermare. Una prova di avvio automatica non certifica acquisizione schermo, controllo input o autenticazione di una sessione desktop. I pacchetti restano beta.
