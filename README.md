# mauriziofalconi-ripetizioni

Rebuild statico del sito pubblico per l'attività di ripetizioni di Maurizio Falconi.

## Offerta pubblica corrente

- **Materie:** matematica e fisica
- **Livelli:** scuole medie e superiori
- **Online:** 20 €/h
- **In presenza:** 25 €/h
- **Zona per le lezioni in presenza:** Comune di Parma
- **Contatto pubblico:** 377 098 2047, telefono e WhatsApp

## Architettura

- HTML/CSS statico, senza framework, dipendenze runtime o telemetria.
- Mobile-first e compatibile con GitHub Pages.
- index.html contiene l'intero sito.
- Le vecchie URL contattami.html, prenota-una-lezione.html e materiale-didattico.html restano come redirect leggeri verso le sezioni equivalenti.
- Gli asset locali già presenti in assets/ vengono mantenuti; il nuovo sito usa soltanto mf-circle-logo.png.
- Nessun calendario, form o servizio di prenotazione esterno viene incorporato.

## Contenuto preservato dal sito precedente

Sono stati mantenuti soltanto gli elementi ancora utili e coerenti con il contesto corrente:

- impostazione delle lezioni basata sul ragionamento, non sulla memorizzazione meccanica;
- sequenza teoria essenziale -> esercizi;
- supporto per recupero delle lacune e preparazione a verifiche;
- struttura della sezione materiali;
- i vecchi URL principali, preservati come redirect leggeri.

Sono stati rimossi dal nuovo codice:

- dipendenze, fogli di stile, script, branding e telemetria del vecchio site builder;
- email personale legacy;
- il vecchio numero di telefono non più approvato;
- vecchi orari;
- vecchia tariffa online da 15 €/h;
- vecchie aree di servizio fuori dal Comune di Parma;
- link Calendly legacy;
- link all'intero Drive didattico, perché include materiale degli studenti e documenti di provenienza eterogenea.

## Stato privacy

Il nuovo sito espone un solo recapito approvato: **377 098 2047**, usato per telefono e WhatsApp.

Non viene pubblicata alcuna email. Il quality gate controlla l'assenza del vecchio numero e dei recapiti non approvati.

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
- assenza dell'email legacy e del vecchio numero;
- presenza esatta dei link telefono/WhatsApp approvati;
- presenza di regole responsive nel CSS;
- presenza dei redirect per le vecchie URL.

## Deployment

Il progetto resta compatibile con GitHub Pages da branch. Il rebuild non cambia il modello di hosting e non introduce costi.

## History reset — NON ESEGUITO

La history precedente contiene copie del vecchio export, della telemetria già rimossa dal branch corrente e dei recapiti legacy. Nessun rewrite è stato eseguito.

Per eliminare quei dati dalla history pubblica, dopo approvazione esplicita è consigliato un history reset del repository:

1. conservare, se desiderato, un archivio locale o privato della vecchia history;
2. creare un nuovo root commit contenente soltanto il tree pulito approvato;
3. aggiornare forzatamente il branch pubblico a quel root commit;
4. eliminare eventuali branch o tag pubblici che mantengano raggiungibili i vecchi commit;
5. verificare nuovamente la superficie pubblica e attendere la normale garbage collection e scadenza delle cache di GitHub.

Un tag pubblico di backup non va creato se l'obiettivo è rimuovere i dati legacy dalla superficie pubblica, perché manterrebbe la vecchia history raggiungibile.

Questa operazione è distruttiva rispetto alla history Git e richiede approvazione esplicita prima dell'esecuzione.
