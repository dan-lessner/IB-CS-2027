# Zadani pro skriptovane generovani trati (faze 3)

Chceme moci generovat tratě uživatelskými skripty, analogicky k řízení aut.

---

## 1) Umístění a načítání skriptů

* složka: `track_generators/` (vedle `Scripts/` analogicky)
* načíst všechny `*.py` v té složce
* každý skript musí exportovat:

  * `META` (dict) – metadata pro UI
  * funkci `generate_track(params)` – vlastní generátor

---

## 2) Volba generátoru při startu

* zdroje volby:

  * pevná defaultní volba (jeden z ukázkových skriptů)
  * volba daná v racecars.config
  * CLI parametr (přednost) např. `--track <id>`
  * nebo úvodní dialog: select box naplněný z načtených generátorů
* `id` generátoru:

  * `META["id"]` (unikátní string)
* zobrazený název:

  * `META["name"]`

---

## 3) Kontrakt rozhraní (co student implementuje)

### 3.1 Funkce

`generate_track(params) -> (grid, start_nodes, finish_nodes)`

### 3.2 Vstup `params` (read-only dict)

Povinné klíče:

* `width` (int) – šířka světa v uzlech (krajní uzly ale nikdy nejsou trať)
* `height` (int) – výška světa v uzlech (krajní uzly ale nikdy nejsou trať)
* `player_count` (int) – počet aut/hráčů
* `track_width` (int) – doporučená šířka tratě (>=1)

  * smysl: aby generátor mohl udělat start/cíl široký aspoň na auta
* `seed` (int | None) – volitelný seed pro náhodnost (pokud chcete reprodukovatelnost)
* `extra` (dict) – volitelné další parametry (UI/CLI může doplnit později)

### 3.3 Výstupy

**A) `track`**

* typ: 2D boolean pole `height x width`
* hodnoty - viz předchozí specifikaci
* vnější perimetr - netraťové uzly, tzn. auta nemusí kontrolovat podmínku, jestli nevyjíždí mimo mapu. Žádný traťový uzel není na okraji.

**B) `start_nodes`**

* seznam uzlů (souřadnice)
* formát uzlu: dvojice `(x, y)` (int, int)
* musí být na trati (`grid[y][x] == True`)
* počet start uzlů mírně větší než `player_count`, např. o 3

**C) `finish_nodes`**

* seznam uzlů (souřadnice)
* formát uzlu: `(x, y)`
* musí být na trati
* musí tvořit sousedící uzly (svisle, vodorovně nebo šikmo)
* doporučení: počet cílů v rozmezí 3 a `player_count`


Vedle toho se loguje level INFO: který algoritmus generoval, jaké byly vstupní parametry (vč. seed, abychom mohli lépe replikovat a ladit)

---

## 4) Post-processing v simulátoru (co doplní engine, ne student)

### 4.1 „Bezpečnostní rám“ světa

* po návratu `grid` engine vynutí okraj světa jako **mimo trať**:
  * pro všechny `x`: `grid[0][x]=0`, `grid[height-1][x]=0`
  * pro všechny `y`: `grid[y][0]=0`, `grid[y][width-1]=0`
* pokud není splněno, okraj se doplní (zneprůjezdnění trati se zkontroluje později)

### 4.2 Ošetření start/finish

* kontrola splnění podmínek pro start a finish uzly

### 4.3 Ošetření průjezdnosti

* lze se dostat z každého startovního pole do nějakého cílového? (prohledávání do šířky)

* pokud je podmínka 4.2 nebo 4.3 porušena, loguje se chyba generování a generuje se znovu (může dojít k zacyklení, což dovolíme, studenti si případně opraví sami)

---

## 6) Metadata `META` (pro UI/CLI)

Povinné:
* `id`: string, unikátní (např. `"rectangle"`, `"l_turn"`)
* `name`: string (lidský, pro select)

---

## 7) Defaultní ukázkové generátory

### 7.1 `rectangle.py`

* `grid`: všude True, jen okraj False, prostě obdélníková plocha
* `start_nodes`: na levém okraji rámu (`x=1`), uprostřed, počet odpovídá `player_count`
* `finish_nodes`: protilehlá strana (např. `x=width-2`)

### 7.2 `L_turn.py`

* `grid`: pás „L“:

  * svislý segment u levé strany uvnitř rámu (např. `x=1..1+track_width-1`)
  * vodorovný segment u spodní strany uvnitř rámu (např. `y=height-2-track_width+1 .. height-2`)
  * šířka pásu odpovídá počtu hráčů
* start: vodorovně, nahoře vlevo „u počátku“ (ale uvnitř rámu)
* cíl: dole vpravo (uvnitř rámu)
* ostrý ohyb 90° (zřetelná zatáčka)

### 7.3 `ractangular_zigzag.py`

Refactor současného generátoru:
* start na levém okraji, počet odpovídá počtu hráčů
* cíl na pravém okraji
* trať projede téměř rovnými segmenty několikrát mezi horním a dolním okrajem, kde jsou prudké zatáčky 
* nikdy není potřeba se vracet zpět podél osy x (když bude auto zkoušet jet co nejvíc doprava a při nárazu do zdi hledat volnou cestu jedním a pak druhým směrem, co cíle dojede)