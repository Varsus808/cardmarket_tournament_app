# cardmarket_tournament_app



Im folgendem findet sich ein Python-Script, welches die automatisierte Berechnung des billgsten Preises jeder MagicTheGathering Karte in deiner Deckliste erlaubt.

"Billigste" bedeutet in diesem Kontext: billigster Anbieter, 
- Standort: Deutschland
- Sprache: Deutsch, Englisch
- Nicht "Goldbordered".

## Installation
```sh
git clone https://github.com/Varsus808/cardmarket_tournament_app.git
cd cardmarket_tournament_app/
pip install -r requirements.txt
```


## Vor dem ersten gebrauch

Exportiere deine Deckliste von der Website deiner Wahl (Moxfield, Archidekt, etc.)
als "MTGO"-Format. Und ersetzt die test.txt durch eure Deckliste.
Man kann auch mehrere Decklisten in das "in" directory legen und das skript arbeitet die sachen automatisch ab.
Viel Erfolg und Spaß!

## Warnungen

Das skript braucht pro EDH Deck etwa 30 Minuten, ist nicht optimal gehandhabt.
Man braucht ununterbrochenen internet Zugang.

## To-Do's

- Filter optionen einstellbar machen
- Playsets nicht als Playset, sondern als 1/4 playset berechnen
- Bugs fixen (bitte reportet bugs)
- GUI hinzufügen 
