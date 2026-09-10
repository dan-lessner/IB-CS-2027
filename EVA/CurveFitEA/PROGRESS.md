# CurveFitEA — dokumentace a plán

Specifikace: `_Agentic/EvoMice/CurveFitEA - specifikace.md` (zdroj pravdy pro zadání) v Obsidianu,
odkazuje se navíc na sdílené konvence z `_Agentic/EvoMice/EvoMice - specifikace.md` (sekce 6a
didaktický kód, 8.2 i18n, 13.5 centralizace defaultů, 13.8 podmíněné parametry, 14.2 responzivní
layout). Tenhle soubor je živá dokumentace (ne log) — udržuj ho aktuální, historii dokončených
kroků hledej v git historii (`git log -- EVA/CurveFitEA`), ne tady.

## Koncept (stručně, viz spec pro detaily)

Didaktická demonstrace metody nejmenších čtverců: místo výpočtu uzavřeným vzorcem hledáme
koeficienty polynomu (daného stupně) evolučním algoritmem. Genom jedince = koeficienty
polynomu. Fitness = SSE (součet čtverců odchylek) křivky od bodů. Populace kandidátních křivek
se vykresluje současně, sytost barvy podle fitness. Body na ploše lze myší přidávat/mazat/tahat;
klik/hover na křivku zobrazí čtverce odchylek + jejich součet.

## Jak spustit

Statická stránka, žádný build krok. Otevřít `index.html` přímo v prohlížeči, nebo servírovat přes
`python3 -m http.server`.

## Architektonická rozhodnutí (nejednoznačná místa spec)

- **Normalizace x pro polynom:** koeficienty se evolučně hledají pro polynom vyhodnocený v
  normalizované souřadnici `u = (x - xMid) / xHalfSpan ∈ [-1, 1]`, ne přímo v souřadnici `x`
  domény. Díky tomu nedochází k "výbuchu" vysokých mocnin (x^5 apod.) a všechny koeficienty
  mohou sdílet stejný rozsah/přesnost kódování bez ohledu na stupeň polynomu — jinak by vyšší
  koeficienty potřebovaly řádově menší rozsah než ten první, což by komplikovalo bitové kódování
  i UI. Studentům je to vysvětleno v tooltipu sekce polynomu.
- **Rozsah koeficientů (`coeffRange`):** dopočítá se při každém resetu z rozpětí generovaných
  bodů (`max(10, 3 × maxAbsY)`), použije se jako mez pro bitové kódování i pro počáteční
  náhodnou populaci u obou variant (bitová/doménová). Není to samostatný UI ovládací prvek —
  přidávalo by to složitost bez jasného didaktického přínosu.
- **Body vs. doména:** doména (`x ∈ [DOMAIN_X_MIN, DOMAIN_X_MAX]`, `y` dopočtené z dat) je vždy
  přesně to, co odpovídá hranicím plochy — klik kamkoli na plochu tedy vždy padne do domény,
  není potřeba řešit "bod mimo rozsah".
  Referenční skrytý model (stupeň, koeficienty, šum) je nezávislý na uživatelem zvoleném stupni
  fitovaného polynomu — je to záměrné (umožňuje podfitování i přefitování jako pozorovatelný jev).
- **Tlačítko "Nová náhodná sada bodů (reset)"** (analogie EvoMice "Nová náhodná populace")
  regeneruje **obojí** — nové body ze skrytého modelu i novou náhodnou populaci — podle aktuálního
  seedu. Změna stupně polynomu restartuje jen populaci (nová náhodná populace daného stupně),
  body zůstávají — uživatelova ruční úprava bodů se změnou stupně neztrácí.
- **Metrika fitness:** SSE je výchozí a hlavní (dle spec), MAE nabídnuta jako alternativa
  (select, spec bod 5 "volitelně"). Fitness pro účely selekce/řazení je vždy `1 / (1 + chyba)`
  (vyšší = lepší), zobrazená/optimalizovaná "chyba" je přímo SSE nebo MAE dle volby.
- **Bez fitness grafu a bez save/load (cookie/URL):** CurveFitEA spec je na rozdíl od EvoMice
  nezmiňuje — vynecháno kvůli udržení rozsahu; centralizované defaulty + reset ano (spec 5,
  sdílená 13.5), ukládání/sdílení odkazem ne.
- **Mutace/křížení — sjednocený výběr bit/doménová varianta:** stejně jako EvoMice (jeden
  `mutation-type-select`/`crossover-type-select` nabízející obě rodiny vedle sebe, ne
  samostatný přepínač "reprezentace"), viz spec 4 a EvoMice 6a.

## Plán fází

1. [x] Kostra stránky (HTML/CSS/canvas) + i18n skeleton (cs/en)
2. [x] Vykreslení bodů + interakce myší (přidat/smazat/táhnout klikem a tažením)
3. [x] Model polynomu + fitness (SSE), zobrazení čtverců odchylek při hover/kliku na křivku + součet
4. [x] Evoluční jádro — bitová varianta (genom, mutace bit-flip, křížení 1/více-bodové/uniformní, selekce)
5. [x] Evoluční jádro — doménová/geometrická varianta (mutace = drobná změna, křížení = střídavé přebírání + bod mezi rodiči)
6. [x] UI nastavení (stupeň, populace, elitismus/náhrada, bit/doménová volby podmíněně, seed) + centralizované defaulty + reset
7. [x] Vizualizace kvality populace (sytost/průhlednost podle fitness)
8. [x] Responzivní layout (dle EvoMice 14.2) — Chromium screenshoty na víc velikostí okna
9. [x] README.md

Malé samostatně commitovatelné kroky, commit+push po každém dokončeném kroku.

## Vizuální ověřování

Na VM je nainstalované skutečné headless Chromium — použij ho na reálné screenshoty před
commitem cokoliv layoutového (viz EvoMice PROGRESS.md pro historii, proč tohle je nutné).

```
cd EVA/CurveFitEA && python3 -m http.server 8532 --bind 127.0.0.1 &
chromium --headless --disable-gpu --no-sandbox --window-size=<W>,<H> \
  --screenshot=/home/agent/curvefit_check_<popis>.png "http://127.0.0.1:8532/index.html"
```

Screenshot cesta MUSÍ být v `$HOME` (snap sandbox), smazat po prohlédnutí, necommitovat.

## Poznámky za běhu

(doplní se v průběhu implementace)
