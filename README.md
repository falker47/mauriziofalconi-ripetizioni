# mauriziofalconi-ripetizioni

Repository del mio sito web dedicato alle ripetizioni scolastiche.

Il progetto è un sito statico, sviluppato con HTML, CSS e JavaScript. Il Quaderno presenta tre esempi di lezione sfogliabili, con un'interfaccia responsive e senza framework applicativi.

## Struttura del progetto

- `index.html` — pagina principale del sito.
- `quaderno.css` e `quaderno.js` — layout della home e controlli del carosello.
- `styles.css` — stili delle pagine di servizio e dei reindirizzamenti.
- `assets/` — immagini, font locali e licenza di Instrument Serif.
- `404.html` — pagina per gli indirizzi non trovati.
- `contattami.html`, `prenota-una-lezione.html`, `materiale-didattico.html` — reindirizzamenti dalle vecchie pagine.
- `scripts/check_site.py` — script per la verifica statica del sito.
- `.github/workflows/quality.yml` — workflow di controllo automatico.

## Tecnologie

- HTML5
- CSS3
- JavaScript
- Python 3 per le verifiche
- GitHub Actions per la CI
- GitHub Pages per l'hosting

Il sito non richiede un backend, un processo di compilazione o l'installazione di dipendenze applicative.

La home collega WhatsApp e il sito personale dell'autore. Non implementa script di analytics propri.

## Esecuzione locale

Clonare il repository e, dalla directory principale, avviare un server HTTP locale:

    python -m http.server 8000

Il sito sarà accessibile all'indirizzo:

http://localhost:8000/

## Verifiche

Per eseguire i controlli statici:

    python scripts/check_site.py

Lo script verifica la struttura delle pagine, i collegamenti interni, i reindirizzamenti e alcuni requisiti del layout.

Il workflow `site-quality` esegue automaticamente questi controlli tramite GitHub Actions. Le verifiche statiche non sostituiscono un collaudo visivo o funzionale nel browser.

## Deployment

Il sito è pubblicato tramite GitHub Pages dal branch `master`.

https://falker47.github.io/mauriziofalconi-ripetizioni/

## Licenza e cronologia

Il repository non contiene attualmente un file `LICENSE`.

La cronologia Git conserva anche versioni precedenti del progetto. Non è stata eseguita alcuna riscrittura della history; un'eventuale operazione di questo tipo richiede autorizzazione separata.
