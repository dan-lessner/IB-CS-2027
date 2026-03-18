**Shrnutí (1–2 řádky):** A* nad stavovým prostorem **(x, y, vx, vy)**, přechod = „zrychlení“ **ax, ay ∈ {-1,0,1}**, nová poloha = poloha + nová rychlost; heuristika odhaduje délku cesty vzdušnou čarou, ale počítá s aktuální rychlostí v daném stavu a se zrychlováním až do cíle; jde  přepínat i pro „styl jízdy“ (rychlost/úhel) jako sekundární preference výběru stavu k prozkoumání

---

## 1) Kontext a cíle algoritmu

1. **Úloha**

   * najít sekvenci tahů (zrychlení) pro autíčko v mřížce s překážkami
   * respektovat fyziku: rychlost je 2D vektor, mění se omezeným zrychlením, poloha se posouvá rychlostí

2. **Optimalita**

   * primární optimalizační kritérium: **minimální počet kroků (tahů / ticků simulace)** do cíle
   * sekundárně (jen volitelně): „styl jízdy“ (preferovat/odmítat vysokou rychlost, ostré zatáčky, cik-cak), ale **nesmí to zhoršit minimální počet kroků**, pokud je požadována striktní optimalita

---

## 2) Vstupy / výstupy

1. **Vstupy**
Viz script_api.py
   * `track[y][x] -> bool` (2D maska trati)
   * `start_pos = (x0,y0)`
   * `start_vel = (vx0,vy0)` (typicky (0,0))
   * `finish_cells = množina buněk cílové rovinky` (může být více buněk)
   * targets, valid targets

2. **Výstupy**

   * plán jako seznam akcí `[(ax1,ay1), (ax2,ay2), ...]`, kde `axi,ayi ∈ {-1,0,1}`

---

## 3) Stavový prostor a přechody

1. **Stav (uzel v A*)**

   * `S = (x, y, vx, vy)`
   * interpretace: auto je v buňce `(x,y)` a má aktuální rychlost `(vx,vy)`

2. **Akce**

   * `A = (ax, ay)` kde `ax, ay ∈ {-1, 0, 1}` (9 možností, leda některé prchází zdí nebo v ní končí - potřebné informace jsou k dispozici na vstupu, nebo je lze importovat z modelu fyziky, nebo implementovat i tady zvlášť)

3. **Přechodová funkce**

   * `vx2 = vx + ax`
   * `vy2 = vy + ay`
   * `x2 = x + vx2`
   * `y2 = y + vy2`

4. **Validace přechodu (nutno přesně navázat na API světa)**

   * minimální varianta: cílová buňka musí být na trati: `track[y2][x2] == True`
   * samotná cesta:
     * zkontrolovat všechny buňky/segmenty na úsečce `(x,y)->(x2,y2)` (line rasterization / Bresenham) nebo raději volání enginu `is_segment_clear`
   * případné „out of bounds“ = neplatný přechod

5. **Cena hrany**

   * `cost(S->S2) = 1` (jeden tick)
   * tím pádem A* hledá minimum počtu kroků

---

## 4) Cíl a ukončení

1. **Cílový test**

   * `is_goal(S): (x,y) ∈ finish_cells`
   * čím vyšší rychlost projetí cílem, tím lépe

2. **Rekonstrukce cesty**

   * klasicky přes `came_from[state] = (prev_state, action_used)`
   * po nalezení cíle vrátit akce v obráceném pořadí

---

## 6) A* – datové struktury a pořadí rozvoje

1. **Open set (prioritní fronta)**

   * klíč `f = g + h`
   * `g[state] = počet kroků od startu`

2. **Closed set / best g**

   * ukládej nejlepší známé `g` pro stav; když přijde horší, zahodit

3. **Generování sousedů**

   * pro každé `(ax,ay)` spočti `S2`
   * pokud neplatné, pokračuj
   * `tentative_g = g[S] + 1`
   * pokud `tentative_g < g_best[S2]`, aktualizuj

4. **Stop podmínka**

   * jakmile vytáhneš z priority queue stav, který splňuje `is_goal`, budeš končit.
   * je potřeba ještě douzavřít ostatní stavy, které by mohly ukončit ve stejném kole, protože engine upřednostní interpolovaný brzký průjezd cílem => podívej se do implementace určení vítěze (v controller.py) - toto namodeluj a z těch cest, které končí v daném tahu, vyber tu vítěznou
   
---

## 7) Heuristika A*: přípustnost vs. monotónnost (konzistence)

1. **Přípustnost (admissible)**

   * `h(n) ≤ skutečná nejmenší cena z n do cíle`
   * důsledek: A* najde optimální řešení (min. kroků), typicky při „tree search“ i „graph search“, ale s různými detaily

Počítá se zvlášť přes x a přes y, popis je jen pro x:
1) Spočítat rozdíl polohy auta a polohy (nejbližšího) cílového uzlu. 
2) Upravit znaménko tak, aby odpovídalo rychlosti v dané souřadnici: pokud se auto pohybuje směrem k cíli, tak má rozdíl zneménko stejné, pokud ne, znaménku musíme obrátit
3) Dosadit do vzorce: `-v+(sqrt((2v-1)**2+8*d))/2`, kde v je rychlost a d je rozdíl polohy (se správným znaménkem)
4) výsledná heuristika je ta větší z obou výsledků (za x a y)
---

## 8) Parametrická heuristika / preference stylu jízdy (bez rozbití optimality)

Chceš přepínat:

* jen `max`/grid odhad,
* zahrnout velikost rychlosti (Eukleidovsky),
* zahrnout úhel změny rychlosti (min/max).

Použije se při tie-break, nezasahuje do heuristiky. Připrav potřebné funkce, podle potřeby je budu v kódu přepínat ručně.
Tzn. najdi jednotnou signaturu a univerzální placeholder název (move_style_score), to se bude volat při samotném výběru tahu, a na začátku kódu ručně přiřadím např. move_score_style = _score_style_max_speed

### Definice volitelných style metrik

1. **Velikost rychlosti**

   * `speed = sqrt(vx*vx + vy*vy)` (Eukleidovsky)
   * varianty:

     * preferovat vyšší rychlost: `-speed`
     * preferovat nižší rychlost: `speed`

2. **Úhel změny rychlosti**

   * máš `v_prev = (vx,vy)` a `v_next = (vx2,vy2)`
   * cos úhlu:
     `cosθ = dot(v_prev, v_next) / (|v_prev|*|v_next|)` (ošetři nulu)
   * varianty:

     * minimalizovat úhel (plynulost): maximalizovat `cosθ` ⇒ `style = -cosθ`
     * maximalizovat úhel („kličkování“): minimalizovat `cosθ` ⇒ `style = +cosθ`

---

## 9) Implementační detaily, které musí být explicitní (aby to šlo rovnou nakódovat)

1. **Rozsahy rychlostí**

   * rychlost nemůže být vikdy větší, než velikost (sqrt(1+8*max(width,height)))/2 podle rozměrů mapy (světa)
   
3. **Paměť a výkon**
   * před zahájením implementace zanalyzuj a odpověz na otázku: je lepší prioritní frontu držet jako heap, abychom rychle dostali minimum (s nutností dohledávat při každém updatu, nebo prostě přidávat, ale při popu testovat, jestli nejde o už zpracovaný a uzavřený stav), nebo jako dictionary, abychom mohli rychle updatovat, ale pop minima je dražší?
4. **Nedosažitelnost**

   * pokud open set dojde, vrať „nenalezeno“