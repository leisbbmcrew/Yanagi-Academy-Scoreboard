# Tabellone Judo

Tabellone segnapunti per il judo, pensato per essere usato da telefono o tablet in orizzontale e proiettato su una TV o un secondo schermo durante le gare.

Creato da **Yanagi Academy**.

🔗 **Sito pubblico:** https://leisbbmcrew.github.io/Janagi-Academy-Score/

## Funzionalità principali

- **Tempo**: regolamentare a countdown e golden score, personalizzabili o a tempo libero ("no limit").
- **Shido**: numero di penalità configurabile, con l'ultima penalità segnalata in rosso.
- **Punteggi**: Ippon, Waza-ari, Yuko e Koka, attivabili singolarmente; assegnazione automatica durante l'osaekomi in base ai secondi configurati.
- **Database atleti**: importazione da file (CSV/TXT), ricerca per nome, cognome o parte di essi, bandiera della nazione caricata in automatico.
- **Pannello per la TV**: vista separata, pensata per essere proiettata, che mostra solo i dati confermati.
- **Riepilogo match**: storico dei match disputati, esportabile in CSV.

## Come si usa

Tutte le istruzioni sono disponibili direttamente nell'app, nel menu **☰ → Info**.

## Installazione come app (PWA / APK)

Il sito include un file `manifest.json` e le icone necessarie per essere:
- installato come app direttamente dal browser (Chrome → "Aggiungi a schermata Home");
- impacchettato come APK Android tramite [PWABuilder](https://www.pwabuilder.com).

## Tecnologia

Pagina web singola in HTML, CSS e JavaScript, senza dipendenze esterne né server: tutti i dati (atleti, impostazioni, riepilogo match) restano salvati nel browser di chi lo usa.
