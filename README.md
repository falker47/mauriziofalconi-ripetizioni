# mauriziofalconi-ripetizioni

Rebuild statico del sito pubblico per l'attività di ripetizioni di Maurizio Falconi.

## Architettura

- HTML/CSS statico, senza framework, dipendenze runtime o telemetria.
- Mobile-first e compatibile con GitHub Pages.
- index.html contiene l'intero sito.
- Le vecchie URL contattami.html, prenota-una-lezione.html e materiale-didattico.html restano come redirect leggeri verso le sezioni equivalenti.
- Gli asset locali già presenti in assets/ vengono mantenuti; il nuovo sito usa soltanto mf-circle-logo.png.
- Nessun calendario, form o servizio esterno viene incorporato finché non è confermato come canale corrente.

## Contenuto preservato dal sito precedente

Sono stati mantenuti soltanto gli elementi ancora utili e coerenti con il contesto corrente:

- impostazione delle lezioni basata sul ragionamento, non sulla memorizzazione meccanica;
- sequenza teoria essenziale -> esercizi;
- supporto per recupero delle lacune e preparazione a verifiche;
- pubblico scolastico di medie e superiori, da riconfermare prima della pubblicazione;
- sezione materiali, ora ridotta a risorse pubbliche selezionate e senza esporre cartelle studenti.

Sono stati rimossi dal nuovo codice:

- dipendenze, fogli di stile, script, branding e telemetria del vecchio site builder;
- recapiti personali legacy;
- orari e tariffe non più verificati come offerta generale;
- vecchie aree di servizio fuori Parma;
- link di prenotazione non riconfermati;
- link all'intero Drive didattico, perché include materiale degli studenti e documenti di provenienza eterogenea.

## Stato privacy

Il branch di rebuild non contiene recapiti personali. La sezione contatti è volutamente incompleta finché non viene scelto il canale pubblico definitivo.

## Verifica locale

Eseguire:

    python scripts/check_site.py
    python -m http.server 8000

Poi aprire http://localhost:8000/ e verificare almeno una viewport mobile e una desktop.

## Quality gate

La GitHub Action site-quality esegue controlli zero-dipendenze su:

- struttura HTML di base e viewport;
- link interni e anchor;
- assenza di riferimenti legacy al vecchio builder/CDN;
- assenza di email e link telefonici nel draft privacy-safe;
- presenza di regole responsive nel CSS;
- presenza dei redirect per le vecchie URL.

## Deployment

Il progetto resta compatibile con GitHub Pages da branch. Il rebuild non modifica qui le impostazioni Pages del repository. La pubblicazione va verificata dopo il merge sul branch servito da Pages.

## History reset — NON ESEGUITO

La history precedente contiene copie del vecchio export e dei recapiti legacy. Nessun rewrite è stato eseguito.

Per eliminare quei dati dalla history pubblica, dopo approvazione esplicita è consigliato un history reset del repository:

1. conservare, se desiderato, un archivio locale o privato della vecchia history;
2. creare un nuovo root commit contenente soltanto il tree pulito approvato;
3. aggiornare forzatamente il branch pubblico a quel root commit;
4. eliminare eventuali branch o tag pubblici che mantengano raggiungibili i vecchi commit;
5. verificare nuovamente la superficie pubblica e attendere la normale garbage collection e scadenza delle cache di GitHub.

Un tag pubblico di backup non va creato se l'obiettivo è rimuovere i dati legacy dalla superficie pubblica, perché manterrebbe la vecchia history raggiungibile.

Questa operazione è distruttiva rispetto alla history Git e richiede approvazione esplicita prima dell'esecuzione.
