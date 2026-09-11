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

**Stav k 2026-09-11 (ověřeno inspekcí souborů, ne jen textem téhle tabulky):** JS moduly
(`js/*.js`, ~2300 řádků) existují a vypadají obsahově hotové, ALE `index.html`, `style.css`,
`js/i18n/` (slovníky) **neexistují vůbec** — stránka se tedy nedá otevřít ani spustit, natož
vizuálně ověřit. Nikdy neproběhl žádný Chromium screenshot. Jediný commit je plán (PROGRESS.md).
Checkboxy níže přeznačeny na realitu — **předchozí běh si fáze 1-9 označil jako hotové, aniž by
HTML/CSS/i18n vůbec existovaly — nedělej to samé, "hotovo" znamená prokazatelně funkční a
vizuálně ověřenou stránku, ne že JS soubor existuje.**

1. [ ] Kostra stránky (HTML/CSS/canvas) + i18n skeleton (cs/en) — **chybí úplně, udělej první**
2. [~] Vykreslení bodů + interakce myší — logika v `input.js`/`render.js` možná existuje, ověř a doprop propoj s HTML
3. [~] Model polynomu + fitness (SSE) — `model.js` existuje, ověř funkčnost po zprovoznění stránky
4. [~] Evoluční jádro — bitová varianta — `ga.js` existuje, ověř
5. [~] Evoluční jádro — doménová/geometrická varianta — `ga.js` existuje, ověř
6. [~] UI nastavení + centralizované defaulty (`defaults.js`) — propoj s HTML, chybí i18n slovníky
7. [ ] Vizualizace kvality populace (sytost/průhlednost podle fitness)
8. [ ] Responzivní layout (dle EvoMice 14.2) — Chromium screenshoty na víc velikostí okna — POVINNÉ, nikdy neproběhlo
9. [ ] README.md
10. [ ] Reprezentace genomu (spec 5) — transformace přímá/normalizovaná × celá/pevná/float
11. [ ] Stupeň polynomu jako součást genomu (spec 6)
12. [ ] Další fitness metriky + vysvětlení v UI (spec 7)
13. [ ] Historie nejlepších jedinců, blednoucí stopa (spec 3)
14. [ ] Přirozená čísla pro souřadnice bodů (spec 2)

`[~]` = kód možná existuje, ale NEOVĚŘENO během stránky v prohlížeči — nepovažuj za hotové, dokud
to nevidíš fungovat na screenshotu.

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
