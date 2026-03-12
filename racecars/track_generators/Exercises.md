**Shrnutí:** 3 úrovně obtížnosti (každá po 3 variantách) – od deterministických cyklů nad polem → práce s podmínkami a segmenty → pseudonáhodnost, stavové generování, „organický“ vzhled.

---

# ÚROVEŇ 1 – deterministické, čitelné cykly

## 1A – Plný obdélník

**Cíl:** pochopit 2D pole, dvojitý cyklus
**Princip generování:**

* vytvořit pole `width x height`
* všude nastavit `1` (trať)
* start = celý levý okraj
* cíl = celý pravý okraj

**Didaktický fokus:**

* inicializace 2D pole
* indexování `[y][x]`
* práce s rozměry světa

---

## 1B – Vnitřní obdélník s okrajem

**Cíl:** práce s podmínkou uvnitř cyklu
**Princip:**

* pole celé světa
* pokud `x == 0` nebo `x == width-1` nebo `y == 0` nebo `y == height-1` → 0
* jinak → 1

**Didaktický fokus:**

* podmínky v cyklu
* hranové případy

---

## 1C – Jednoduchý koridor (rovná trať)

**Cíl:** práce s intervalem
**Princip:**

* jen pás např. mezi `x = width/3` a `x = 2*width/3`
* zbytek 0
* start nahoře, cíl dole

**Didaktický fokus:**

* výpočet mezí
* práce s parametrem šířky trati

---

# ÚROVEŇ 2 – segmenty a zatáčky

## 2A – L-tvar

**Princip:**

* první segment: svislý pás
* druhý segment: vodorovný pás
* změna směru v bodě zlomu

**Didaktický fokus:**

* rozdělení generování do fází
* práce s mezními hodnotami

---

## 2B – U-tvar

**Princip:**

* dolů
* doprava
* nahoru
* vše pomocí tří segmentů

**Didaktický fokus:**

* stavová proměnná `fáze`
* sekvenční konstrukce trasy

---

## 2C – Schodovitá trať

**Princip:**

* střídání krátkého horizontálního a vertikálního úseku
* délky pevné nebo z parametru

**Didaktický fokus:**

* vnořené cykly
* řízení délky segmentu

---

# ÚROVEŇ 3 – bohatší a „organické“

## 3A – Náhodně lomená trať (random walk bez větvení)

**Princip:**

* začít ve startu
* aktuální směr (nahoru/dolů/vpravo)
* po N krocích změnit směr
* zapisovat pás o určité šířce

**Didaktický fokus:**

* náhodnost
* řízení hranic světa
* kontrola přetečení pole

---

## 3B – Generátor podle vlny (sinusový posun)

**Princip:**

* pro každé `y` spočítat `x_střed = A * sin(y/k) + offset`
* kolem středu vytvořit pás

**Didaktický fokus:**

* matematická funkce
* převod float → int
* spojitost tvaru

---

## 3C – Vyplňující labyrintový koridor

**Princip:**

* svět rozdělit na mřížku bloků
* projít bloky systematicky (např. cik-cak)
* spojovat sousední bloky
* vznikne dlouhá hadovitá trať

**Didaktický fokus:**

* práce s „buňkami vyšší úrovně“
* oddělení logické mřížky a skutečné mapy
* algoritmické myšlení (blízko DFS/BFS principům, bez nutnosti je pojmenovat)