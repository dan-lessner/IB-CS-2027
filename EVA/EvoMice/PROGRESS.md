# EvoMice — dokumentace a plán

Specifikace: viz Obsidian `_Agentic/EvoMice/EvoMice - specifikace.md` (zdroj pravdy pro zadání,
v1-v13 historie zadání). Tenhle soubor je živá dokumentace (ne log) — udržuj ho aktuální,
historii dokončených kroků hledej v git historii (`git log -- EVA/EvoMice`), ne tady.

## Jak spustit

Statická stránka, žádný build krok. Otevřít `index.html` přímo v prohlížeči.

## Stav

- v1-v4 (viz `personal-playground/EvoMice` git historie, kód je stejný, jen bez dev-dokumentace
  přenesen sem 2026-09-09) — hotovo.
- **v5 (spec sekce 13) — v implementaci.**

## Vizuální ověřování (nové od v5)

Na VM je od 2026-09-09 nainstalované skutečné headless Chromium — **použij ho na reálné
screenshoty před commitem cokoliv layoutového**, ne jen Lightpanda JS-bez-pádu kontrolu (ta
neumí layout vůbec, viz starší poznámky v historii tohohle souboru v personal-playground repu).

```
cd EVA/EvoMice && python3 -m http.server 8531 --bind 127.0.0.1 &
chromium --headless --disable-gpu --no-sandbox --window-size=1600,1000 \
  --screenshot=/home/agent/evomice_check.png "http://127.0.0.1:8531/index.html"
```

Screenshot cesta MUSÍ být v `$HOME`, ne v repu ani ve scratchpadu (snap confinement) — smaž ho
po prohlédnutí, necommituj.

## Plán v5 (spec sekce 13)

- [x] 13.1 — výchozí režim krmení v UI = "ruční kreslení" (počáteční rozhození zůstává)
- [x] 13.2 — přesunout blok "Běh simulace" k ploše (k zoomu/fullscreen)
- [x] 13.3 — zrušit patičku
- [x] 13.4 — populace až 1, deaktivovat irelevantní prvky (křížení, turnaj)
- [x] 13.5 — centralizovat výchozí hodnoty (u save/load kódu) + tlačítko reset na výchozí
- [x] 13.6 — fullscreen: graf využije celou výšku, auto-hide ovládací panel při pohybu myší
      (ověřeno screenshotem, viz "Poznámky za běhu" — funguje potřetí napoprvé)
- [x] 13.7 — velikost plochy až 512
- [x] 13.8 — podmíněné zobrazení parametrů (velikost turnaje, počet bodů řezu, ...)
- [x] 13.9 — elitismus pod náhradu generace, default elitismus=0, náhrada=celá generace
- [x] 13.10 — seed nahoru k resetu, zrušit vlastní panel

Malé samostatně commitovatelné kroky, commit+push po každém. i18n (žádný natvrdo zadrátovaný
text) a didaktický kód platí pořád.

## Poznámky za běhu

**13.6 — jak se to ověřovalo bez skutečného Fullscreen API.** Headless
Chromium odmítá `requestFullscreen()` bez opravdového uživatelského gesta
(promise se zamítne, `:fullscreen` se nikdy neuplatní) — proto celá
fullscreen logika teď nezávisí na CSS pseudo-třídě `:fullscreen` přímo, ale
na JS-toggled třídě `.is-fullscreen` na `#canvas-area` (viz
`isFullscreenActive()` v `main.js`, nastavuje/ruší ji `fullscreenchange`
listener). Díky tomu šlo layout ověřit i bez reálného gesta — dočasně (jen
pro test, ne v commitnutém kódu) přidán `<script>` kontrolovaný přes
`?debugFullscreen=1`, který třídu nastaví ručně + navíc nasimuluje, že
`#canvas-area` skutečně vyplňuje celý viewport (`position:fixed;inset:0`),
což jinak zajišťuje prohlížeč sám při reálném fullscreenu. Ověřeno
screenshoty (1600×1000):
- Toolbar (běh simulace, zoom, fullscreen tlačítko) je plovoucí
  poloprůhledná lišta přes horní okraj, plocha simulace pod ní vyplňuje
  prakticky celou výšku okna.
- Graf fitness vpravo (landscape orientace → info panel vedle plochy)
  vyplňuje celou výšku sloupce, ne malý ~90px pruh jako dřív — `canvas`
  atributy `width`/`height` se teď dopočítávají z reálné CSS velikosti
  (`updateFitnessChartCanvasSize()` v `main.js`).
- Auto-hide: toolbar zmizel (opacity 0) po ~2.5 s nečinnosti
  (`--virtual-time-budget=4000`), a při simulovaném `mousemove` na
  `#canvas-area` se okamžitě vrátil zpět.
- Mimo fullscreen (běžný screenshot bez debug parametru) beze změny oproti
  minulému kroku — žádná regrese.

Skutečné volání Fullscreen API (klik na tlačítko myší v opravdovém
prohlížeči) nebylo touhle cestou ověřeno, jen simulovaný CSS/JS stav — na
reálném uživatelském kliknutí by se ale měla spustit úplně stejná větev
kódu (`fullscreenchange` nastaví stejnou třídu `.is-fullscreen`), takže by
se mělo chovat stejně.
