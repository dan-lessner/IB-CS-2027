# EvoMice

Evoluční simulace myší hledajících krmení — klasický generační genetický algoritmus vizualizovaný
na canvasu. Genom myši je její souřadnice (x, y) na mřížce, binárně zakódovaná; myši se
nepohybují krok za krokem, každá generace je nová náhodně/křížením/mutací vzniklá populace.

## Jak stránku spustit

Je to čistě statická stránka (HTML + JS, žádný build krok, žádné závislosti). Stačí otevřít
`index.html` přímo v prohlížeči:

```
xdg-open index.html
```

nebo dvojklikem v souborovém manažeru, nebo přetažením souboru do okna prohlížeče.

**GitHub Pages nejde zapnout** — `personal-playground` je private repozitář a GitHub Pages na
privátním repu vyžaduje placený plán (ověřeno 2026-09-04). Pokud by šlo zapnout někdy v budoucnu
(zveřejnění repa / upgrade plánu), stačí v nastavení repozitáře zapnout Pages ze složky `EvoMice/`
— žádná úprava kódu není potřeba, stránka je samostatná.

Otevřením `index.html` se v konzoli prohlížeče (F12) navíc spustí dva sady vestavěných
self-testů (`genome.js` — kódování/dekódování genomu, `ga.js` — evoluční operátory). Pokud se v
konzoli neobjeví žádné "Assertion failed", vše je v pořádku.

## Ovládání

Každý ovládací prvek a nadpis sekce má vedle sebe ikonku "?" — najetím myší (nebo focusem přes
klávesnici) se zobrazí technické vysvětlení, jak daná volba mechanicky funguje.

| Sekce | Co dělá |
|---|---|
| Běh simulace | Start/pauza, krok po kroku, reset (nová náhodná populace), rychlost (generací/s) |
| Populace a plocha | velikost populace (živě), velikost mřížky (vyžaduje reset — mění délku genomu) |
| Krmení | množství, náhodné rozhození vs. ruční kreslení myší (klik/tažení po ploše), mizení po "snězení" |
| Fitness | binární (je/není na krmení) vs. spojitá (klesá se vzdáleností) |
| Selekce rodičů | ruletová (fitness-proporcionální) vs. turnajová |
| Křížení | míra křížení + 6 variant (4 bitové, 2 geometrické — bod na spojnici rodičů / bod v obdélníku rodičů) |
| Mutace | bitová (převrácení bitu) vs. geometrická (skok do okolí) |
| Elitismus a náhrada generace | kolik jedinců přežije beze změny, celá generace najednou vs. postupná náhrada nejhorších X % |
| Random seed | pro zopakovatelný běh |
| Zoom | čistě vizuální přiblížení celého panelu simulace (canvas + stats + graf) |

Pod plochou se navíc zobrazují souřadnice buňky pod kurzorem a běžící graf min/průměr/max
fitness populace od posledního restartu. Jazyk rozhraní (čeština/angličtina) se přepíná
tlačítky vpravo nahoře, volba se pamatuje mezi návštěvami.

## Uložení a načtení nastavení

Sekce "Uložení a načtení" v panelu nastavení nabízí dvě nezávislé cesty, jak si uložit
aktuální nastavení simulace (a volitelně i to, kde přesně stojí myši a krmení) a později
se k němu vrátit:

| Tlačítko | Co dělá |
|---|---|
| **Uložit do cookie** | Uloží aktuální nastavení do cookie tohoto prohlížeče (platnost 1 rok). Před úplně prvním uložením se zobrazí potvrzovací dialog s vysvětlením, že jde o cookie — bez odsouhlasení se neuloží nic. Souhlas se pak pamatuje (v `localStorage`, ne v další cookie), takže se dialog příště neptá znovu. |
| **Načíst z cookie** | Vrátí ovládací prvky a stav simulace na to, co bylo naposledy uloženo do cookie. Načítání z cookie je vždy ruční akce (tlačítko) — stránka sama od sebe cookie při otevření nečte, aby se nastavení neměnilo "potichu" bez viditelné akce. |
| **Smazat cookie** | Smaže uloženou cookie z tohoto prohlížeče. |
| **Uložit do odkazu** | Vygeneruje URL adresu s aktuálním nastavením zakódovaným v parametru `evomice` a rovnou ji označí v textovém poli pod tlačítkem — stačí zkopírovat (Ctrl+C) a poslat/uložit/otevřít později. Otevření takového odkazu **nahradí výchozí hodnoty nastavení** těmi uloženými v adrese — to se děje automaticky, bez dalšího kroku, protože otevření konkrétního odkazu už samo je explicitní akce. |

Zaškrtávátko **"Uložit i stav plochy (myši, krmení)"** nad tlačítky platí pro obě cesty (cookie
i odkaz) — když je zapnuté, uloží/obnoví se i přesné pozice všech myší a zbývající množství
krmení na každé buňce, ne jen hodnoty ovládacích prvků. Vypnuté (výchozí) uloží jen nastavení —
po načtení pak vznikne nová náhodná populace/krmení podle uloženého seedu, stejně jako po
kliknutí na "Nastavit seed a resetovat".

Technicky jde v obou případech o stejná data (JSON) — jen jinak zabalená: v cookie jako
hodnota `document.cookie`, v odkazu jako URL-encodovaný parametr `evomice`. Kód pro sestavení a
aplikaci dat je sdílený, viz `js/save-load.js`.

## Struktura kódu

Bez build kroku — soubory se načítají jako obyčejné `<script>` tagy v pevném pořadí a sdílejí
globální scope (žádné moduly/bundler):

- `js/i18n/cs.js`, `js/i18n/en.js` — slovníky textů rozhraní (klíč → text), včetně tooltipů;
  přidání dalšího jazyka znamená jen přidat další takový soubor
- `js/i18n.js` — `t(key, params)` pro JS-generované texty, `applyTranslations()` napojuje
  slovník na DOM prvky s atributem `data-i18n` (text) a `data-i18n-tooltip` (obsah tooltipu),
  přepínač jazyka
- `js/rng.js` — seedovatelný generátor náhodných čísel (`mulberry32`)
- `js/genome.js` — mřížka, kódování/dekódování genomu, `Mouse`/`Food`, self-test
- `js/ga.js` — evoluční jádro: `stepGeneration()` jako čitelná orchestrace (fitness → selekce →
  křížení → mutace → náhrada generace → krmení), implementační detaily (bitová/geometrická
  manipulace) schované uvnitř `select()`/`crossover()`/`mutate()`, self-test
- `js/render.js` — vykreslení na canvas + zoom celého panelu simulace
- `js/fitness-chart.js` — historie a graf min/průměr/max fitness populace v čase
- `js/input.js` — ruční kreslení krmení myší, přepočet souřadnic kurzoru na buňku mřížky
- `js/main.js` — propojení UI se stavem simulace, hlavní smyčka
- `js/save-load.js` — uložení/načtení nastavení (a volitelně stavu plochy) do cookie nebo do
  URL (viz "Uložení a načtení nastavení" výše); načítá se jako poslední `<script>`, po `main.js`

Kód je psaný jako didaktická ukázka pro studenty: explicitní `while` smyčky místo
comprehensions/array-metod řetězených dohromady, pojmenované pomocné funkce, komentáře u
netriviálních kroků. Žádný text v rozhraní není zadrátovaný natvrdo — všechno jde přes
`js/i18n/*.js`.
