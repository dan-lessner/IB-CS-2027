# Zadani pro skriptovane ovladani aut (faze 2)

## Cil
- Kazde auto je ovladano bud mysi, nebo skriptem.
- Skriptovane auto se jmenuje podle hodnoty vracene metodou GetName().
- Defaultni beh bez parametru: pouzit vsechny skripty ve slozce Scripts (max 10).

## Slozka se skripty
- Slozka: `Scripts` v koreni repozitare.
- Nazev souboru: jmeno studenta, napr. `Adam.py`.
- Nacteni: vsechny soubory `*.py` v `Scripts`, serazene podle nazvu (krome template.py).
- V kazdem souboru musi byt trida `Auto`, ktera dedi z `AutoAuto`.

## Base class `AutoAuto`
- Umisteni: nova trida v simulaci.
- Metody:
  - `GetName(self) -> str`
    - Vraci jmeno programovaneho auta.
    - Pokud vrati prazdny retezec, pouzije se nazev souboru bez pripony.
  - `PickMove(self, world, targets, validity) -> Vertex`
    - `targets` je seznam vrcholu (po rade pro ax=-1..1, ay=-1..1). `validity` je 9-prvkovy seznam boolu, kde `True` znaci dostupny vertex. Pokud doslo ke kolizi, predava se jediny vertex (soucasna poloha) a je oznacen jako validni.
    - Metoda musi vratit jeden z prvku `allowed_moves`.
    - Pokud vrati `None`, pouzije se stredova volba (akcelerace 0,0) a tah pokracuje.
    - Pokud vrati jinou hodnotu, auto zvoli cekani na miste (zadna zmena rychlosti).
  - dosavadni ovladani mysi a souvisejici logika se presune do tridy ManualAuto, ktera taktez dedi od AutoAuto

## World state (objekt pro skripty)
- Objekt `WorldState` (jen data, bez logiky):
  - `road`: 2D pole bool (bitove pole trate).
  - `start_vertices`: seznam Vertex na startu.
  - `finish_vertices`: seznam Vertex na cilove care.
  - `cars`: seznam objektu `CarInfo`:
    - `id`, `name`, `position` (Vertex), `velocity` (Vector2i).
- WorldState se predava do `PickMove()` kazdy tick.

## Vyber ovladani
- GUI: u kazdeho hrace cyklovani typu (Mouse / Script) + vyber skriptu.
- Konzole: parametr `--controllers` s carkami oddelenym seznamem:
  - hodnoty: `mouse` nebo nazev skriptu (bez pripony)
  - priklad: `--controllers mouse,Adam,Bara`
  - pocet hracu = delka seznamu
- Pokud `--controllers` chybi a v `Scripts` existuji skripty:
  - pouziji se prvni 10 podle nazvu
  - pocet hracu = pocet pouzitych skriptu
- Pokud `--controllers` chybi a `Scripts` je prazdna:
  - pouzije se standardni pocet hracu z parametru hry
  - vsichni hraci jsou Mouse

## Logging
- Logovani pouziva standardni Python modul `logging`.
- Default: zapis do konzole.
- Parametry:
  - `--supress-log`: vypne vsechny logy.
  - `--log-path PATH`: pridat zapis do souboru.
  - `--log-level LEVEL`: minimalni uroven (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
- Kazde auto dostane vlastni logger podle jmena (a id), napr. `racecars.car.<name>.id_<n>`.
- Skript muze logovat pres `self.logger` (instance `Auto`) nebo `auto.logger` (predany objekt auta).
- Detailni popis je v `logging.md`.

## Volani skriptu
- Skript se vola kazdy tick pouze pro auto, ktere je na tahu.
- Seznam `allowed_moves` generuje hra (stejne jako pro klikaci ovladani).

## Merici rezim vykonu
- Zapinatelne z konzole i GUI.
- Po zapnuti se meri cas straveny ve volani `PickMove()` pro kazde auto.
- Na konci hry:
  - vypis do konzole (souhrn za kazde auto)
  - log do souboru v koreni: `performance_log.csv`

## Davkovy beh (serie zavodu)

- Parametry:
  - `--races N`: spustit N zavodu za sebou (default: 1).
  - `--results PATH`: po kazdem zavodu pripsat vysledky do souboru PATH.
- Inicializace (GUI dialogy, vyber ovladani) probehne **jednou** pred celou serii.
- Kazdy zavod dostane novou nahodne vygenerovanou trat (stejny generator, stejna nastaveni).
- Jmena aut se generuji znovu pro kazdy zavod (nahodna kombinace adjektivum + podstatne jmeno).
- Soubor s vysledky:
  - Format: tabulka oddeleana tabulatorem, bez zahlavi, jeden radek na jedno auto.
  - Sloupce: `Race` (cislo zavodu), `Time`, `Place`, `Rounds`, `Crashes`, `Distance`, `Avg.speed`, `Car name`, `Controller`.
  - Soubor se **pripojuje** (append mode) — predchozi obsah se neztraci.
  - Pokud zavod nebyl dokoncen (hrac zavrel okno drive), radek se nezapise.
- Priklad spusteni:
  ```
  python main.py --races 10 --results results.tsv --controllers Adam,Bara
  ```

## Headless rezim (bez okna)

Umoznuje spustit simulaci uplne bez grafickeho vystupu — pygame se vubec nenacita.

### Zapnuti
```
python main.py --headless [dalsi parametry]
```
Aliasy: `--no-gui`, `--start` — vsechny tri jsou ekvivalentni.

### Co se stane
- Zadny pygame, zadne okno — hra bezi jen jako smycka v terminalovem procesu.
- Konfigurační dialog ani dialog pro vyber controlleru se nezobrazi.
- Vysledky zavodu se standardne vypisou do konzole jako tabulka.

### Omezeni: mouse controller
- Ovladani mysis (`mouse`) neni v headless rezimu povoleno — clovek nema jak klikat.
- Pokud se `mouse` objevi v `--controllers`, je zaznamenan jako **ERROR** a dane auto se do zavodu vubec nezaradi. Pocet hracu se snici o 1.
- Priklad: `--controllers mouse,Adam,Bara` → do zavodu nastoupi Adam a Bara, mouse je odmitnuto s chybou.

### Davkovy beh zcela bez okna
Kombinace `--headless`, `--races` a `--results` je hlavni usecase tohoto rezimu — velky pocet zavodu bez jakehokoliv grafickeho vystupu, vsechny vysledky v souboru:

```
python main.py --headless --controllers Adam,Bara --races 200 --results vysledky.tsv
```

### Architektura (pro zvedavejsi studenty)
- Simulacni smycka zije v `simulation/runner.py`, funkce `run_race(game_state, renderer=None)`.
- Kdyz je `renderer=None`, bezi headless — zadny import pygame.
- `Renderer.run()` je obal, ktery vola `run_race(game_state, renderer=self)`.
- V `main.py` se `ui.renderer`, `ui.setup_dialog` a `ui.controller_dialog` importuji az uvnitr podminenych bloku — v headless rezimu se pygame vubec nenacita.
