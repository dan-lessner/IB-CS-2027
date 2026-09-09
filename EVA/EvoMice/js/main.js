// EvoMice — vstupní bod: propojení UI, stavu simulace a hlavní smyčky.
//
// Chování evolučních operátorů (fitness, selekce, křížení, mutace,
// elitismus, náhrada generace) se čte přímo z ovládacích prvků při každém
// kroku (viz readParamsFromUI) — žádný duplicitní stav, jeden zdroj pravdy.
// Strukturální věci (velikost mřížky, seed) vyžadují restart simulace,
// protože mění délku genomu / počáteční náhodnou řadu.

// lastStatusKey si pamatuje poslední zobrazený stavový klíč, aby ho šlo
// znovu přeložit při přepnutí jazyka (viz onLanguageChanged níže).
var lastStatusKey = 'status_loading';

function setStatus(key) {
  lastStatusKey = key;
  var el = document.getElementById('status-line');
  if (el !== null) {
    el.textContent = t(key);
  }
}

var canvas = document.getElementById('sim-canvas');
var ctx = canvas.getContext('2d');

var fitnessChartCanvas = document.getElementById('fitness-chart-canvas');
var fitnessChartCtx = fitnessChartCanvas.getContext('2d');

// --- Stav simulace (mění se resetem, krokem generace, ručním kreslením) ---

var gridConfig;
var population;
var foodList;
var rng;
var generationCount = 0;
var isRunning = false;
var runIntervalId = null;
// Výchozí stav přepínače v UI je "ruční kreslení" (spec 13.1) — HTML má
// odpovídající radio button rovnou 'checked', tahle proměnná to jen zrcadlí.
var foodMode = 'manual'; // 'random' | 'manual'

// --- Vykreslení a stavový řádek --------------------------------------------

// Aktuální kapacita krmení (spec 10.3) — čte se přímo ze slideru, ať platí
// stejně pro vykreslení, náhodné rozhození i ruční přikreslení jedné buňky.
function currentFoodCapacity() {
  return Number(document.getElementById('food-capacity-slider').value);
}

function redraw() {
  drawScene(ctx, canvas, gridConfig, population, foodList, currentFoodCapacity());
  updateStatsLine();
  updateCursorPositionLine(); // myši/krmení pod kurzorem se mění i beze pohybu kurzoru (další generace)
  drawFitnessChart(fitnessChartCtx, fitnessChartCanvas);
}

// Přepočítá fitness aktuální populace a přidá záznam do grafu (viz
// js/fitness-chart.js). Volá computeFitness() z ga.js přímo — nezávisle na
// tom, jestli zrovna proběhl krok evoluce — ať je graf vždy konzistentní s
// právě zobrazenou populací a aktuálním krmením.
function recordCurrentFitnessStats() {
  var fitnessType = document.getElementById('fitness-type-select').value;
  computeFitness(population, foodList, gridConfig, fitnessType);
  recordFitnessSnapshot(generationCount, population);
}

function updateStatsLine() {
  var statsEl = document.getElementById('stats-line');
  if (statsEl === null) {
    return;
  }
  var fedCount = 0;
  var i = 0;
  while (i < population.length) {
    if (isMouseFed(population[i], foodList)) {
      fedCount = fedCount + 1;
    }
    i = i + 1;
  }
  statsEl.textContent = t('stats_line', { gen: generationCount, fed: fedCount, total: population.length });
}

// --- Souřadnice kurzoru pod plochou -----------------------------------
//
// Nezávislé na režimu krmení (funguje i mimo ruční kreslení) — jen ukazuje,
// nad kterou buňkou mřížky je právě kurzor. Využívá canvasPositionToCell()
// z input.js, ať se přepočet klientských souřadnic na buňku nepíše dvakrát.

var lastCursorCell = null; // null = kurzor není nad plochou

// Kromě souřadnic doplní (spec 10.4) počet myší a množství krmení na dané
// buňce — ale jen když tam něco je, ať řádek nepůsobí zbytečně "upovídaně"
// u prázdných buněk.
function updateCursorPositionLine() {
  var el = document.getElementById('cursor-position-line');
  if (el === null) {
    return;
  }
  if (lastCursorCell === null) {
    el.textContent = t('cursor_position_none');
    return;
  }

  var x = lastCursorCell.x;
  var y = lastCursorCell.y;
  var text = t('cursor_position_label', { x: x, y: y });

  var miceCount = countMiceOnCell(x, y, population);
  if (miceCount > 0) {
    text = text + t('cursor_mice_segment', { count: miceCount });
  }

  var foodAmount = foodAmountOnCell(x, y, foodList);
  if (foodAmount > 0) {
    text = text + t('cursor_food_segment', { amount: foodAmount, capacity: currentFoodCapacity() });
  }

  el.textContent = text;
}

canvas.addEventListener('mousemove', function (event) {
  lastCursorCell = canvasPositionToCell(canvas, gridConfig, event.clientX, event.clientY);
  updateCursorPositionLine();
});

canvas.addEventListener('mouseleave', function () {
  lastCursorCell = null;
  updateCursorPositionLine();
});

// --- Čtení evolučních parametrů z UI ---------------------------------------

function readParamsFromUI() {
  var params = createDefaultGaParams();

  params.fitnessType = document.getElementById('fitness-type-select').value;

  params.selectionMethod = document.getElementById('selection-method-select').value;
  params.tournamentSize = Number(document.getElementById('tournament-size-slider').value);

  params.crossoverRate = Number(document.getElementById('crossover-rate-slider').value);
  params.crossoverType = document.getElementById('crossover-type-select').value;
  params.crossoverPoints = Number(document.getElementById('crossover-points-slider').value);

  params.mutationType = document.getElementById('mutation-type-select').value;
  params.mutationRate = Number(document.getElementById('mutation-rate-slider').value);
  params.mutationJumpRadius = Number(document.getElementById('mutation-jump-radius-slider').value);

  params.eliteCount = Number(document.getElementById('elite-count-slider').value);

  params.replacementMode = document.getElementById('replacement-mode-select').value;
  params.replacementPercent = Number(document.getElementById('replacement-percent-slider').value);

  params.foodDepletes = document.getElementById('food-depletes-checkbox').checked;
  params.foodReplenishes = document.getElementById('food-replenishes-checkbox').checked;
  params.foodMode = foodMode;
  params.foodCapacity = currentFoodCapacity();

  return params;
}

// --- Velikost canvasu: responzivní vůči dostupnému místu (spec 10.6, 12.1) -
//
// CELL_PIXEL_SIZE (js/render.js) není pevná konstanta — dopočítá se z
// aktuální šířky I výšky #canvas-area, ať plocha nikdy nepřeteče (spec
// 12.1) a mřížka zabírá dostupné místo rozumně bez ohledu na velikost okna
// nebo počet buněk. Volá se při resetu (mění se gridConfig) i při resize
// okna/přepnutí fullscreenu (mění se dostupné místo, gridConfig zůstává).
//
// Dostupná výška pro samotný canvas = výška #canvas-area mínus vše, co nad
// canvasem/pod ním v #zoom-wrapper reálně zabírá místo (souřadnice kurzoru,
// graf fitness) a toolbar nad tím — jinak by se cell size počítal, jako
// kdyby canvas mohl zabrat celou výšku #canvas-area, a zbytek by se stejně
// jako dřív jen uřízl/scrolloval.
var CANVAS_AREA_HORIZONTAL_RESERVE = 8; // malá rezerva na okraj #canvas-container
var CANVAS_AREA_VERTICAL_RESERVE = 8; // malá rezerva na okraje/mezery navíc

// Ve fullscreenu na šířku (landscape) sedí #info-panel vedle plochy místo
// pod ní (spec 12.2, viz media query ve style.css) — v tom případě ubírá
// místo ze šířky, ne z výšky. Mimo fullscreen (a na výšku i ve fullscreenu)
// zůstává info panel pod plochou jako dřív.
function isInfoPanelBesideCanvas() {
  return document.fullscreenElement !== null && window.matchMedia('(orientation: landscape)').matches;
}

function updateCanvasSize() {
  var canvasArea = document.getElementById('canvas-area');
  var toolbar = document.getElementById('canvas-toolbar');
  var statsLine = document.getElementById('stats-line');
  var cursorLine = document.getElementById('cursor-position-line');
  var fitnessChartArea = document.getElementById('fitness-chart-area');
  var infoPanel = document.getElementById('info-panel');

  var availableWidth = canvasArea.clientWidth - CANVAS_AREA_HORIZONTAL_RESERVE;
  var reservedHeight = toolbar.offsetHeight + CANVAS_AREA_VERTICAL_RESERVE;

  if (isInfoPanelBesideCanvas()) {
    availableWidth = availableWidth - infoPanel.offsetWidth;
  } else {
    reservedHeight = reservedHeight + statsLine.offsetHeight +
      cursorLine.offsetHeight + fitnessChartArea.offsetHeight;
  }

  var availableHeight = canvasArea.clientHeight - reservedHeight;

  updateCellPixelSize(availableWidth, availableHeight, gridConfig);
  resizeCanvasToGrid(canvas, gridConfig);
}

window.addEventListener('resize', function () {
  updateCanvasSize();
  redraw();
});

// --- Reset / inicializace simulace ------------------------------------

// `forceRandomFoodSeed` (nepovinné): i v ručním režimu vytvoří počáteční
// krmení náhodným rozhozením, místo aby začínalo na prázdno — použito jen
// při úplně první inicializaci stránky (spec 13.1: výchozí stav přepínače v
// UI je "ruční kreslení", ale počáteční krmení na ploše je pořád z náhodného
// rozhození "jako dřív"). Běžný reset/reseed tenhle argument nepředává,
// takže se tam ruční režim chová jako obvykle (prázdná plocha k nakreslení).
function resetSimulation(forceRandomFoodSeed) {
  var seedValue = Number(document.getElementById('seed-input').value);
  rng = createRng(seedValue);

  var gridSize = Number(document.getElementById('grid-size-slider').value);
  gridConfig = createGridConfig(gridSize, gridSize);
  updateCanvasSize();

  var populationSize = Number(document.getElementById('population-size-slider').value);
  population = createRandomPopulation(populationSize, gridConfig, rng);

  if (isManualFoodModeActive() && !forceRandomFoodSeed) {
    foodList = []; // ruční režim začíná na prázdno, uživatel si krmení nakreslí sám
  } else {
    var foodCount = Number(document.getElementById('food-count-slider').value);
    foodList = createRandomFood(foodCount, gridConfig, rng, currentFoodCapacity());
  }

  generationCount = 0;
  resetFitnessHistory();
  recordCurrentFitnessStats();
  redraw();
}

// --- Krmení: náhodné rozhození vs. ruční kreslení ------------------------

function isManualFoodModeActive() {
  return foodMode === 'manual';
}

function regenerateRandomFood() {
  var foodCount = Number(document.getElementById('food-count-slider').value);
  foodList = createRandomFood(foodCount, gridConfig, rng, currentFoodCapacity());
  redraw();
}

// Přidá krmení na danou buňku, pokud tam ještě není (ruční kreslení).
function addFoodCellIfMissing(x, y) {
  var alreadyThere = false;
  var i = 0;
  while (i < foodList.length) {
    if (foodList[i].x === x && foodList[i].y === y) {
      alreadyThere = true;
    }
    i = i + 1;
  }
  if (!alreadyThere) {
    foodList.push(createFood(x, y, currentFoodCapacity()));
  }
}

function handlePaintedCell(x, y) {
  addFoodCellIfMissing(x, y);
  redraw();
}

attachManualFoodPainting(
  canvas,
  function () { return gridConfig; }, // živý getter, ať funguje i po resetu s jinou velikostí mřížky
  isManualFoodModeActive,
  handlePaintedCell
);

var foodModeRandomRadio = document.getElementById('food-mode-random');
var foodModeManualRadio = document.getElementById('food-mode-manual');
foodModeRandomRadio.addEventListener('change', function () {
  if (foodModeRandomRadio.checked) {
    foodMode = 'random';
  }
});
foodModeManualRadio.addEventListener('change', function () {
  if (foodModeManualRadio.checked) {
    foodMode = 'manual';
  }
});

document.getElementById('regenerate-food-btn').addEventListener('click', function () {
  if (isManualFoodModeActive()) {
    // Tlačítko je určené pro náhodný režim, ať uživatel v ručním
    // omylem nesmaže vlastní kresbu.
    return;
  }
  regenerateRandomFood();
});

document.getElementById('clear-food-btn').addEventListener('click', function () {
  foodList = [];
  redraw();
});

document.getElementById('food-depletes-checkbox').addEventListener('change', redraw);

// --- Krok evoluce (jedna generace) -----------------------------------

function stepOnce() {
  var params = readParamsFromUI();
  var result = stepGeneration(population, foodList, gridConfig, params, rng);
  population = result.population;
  foodList = result.food;
  generationCount = generationCount + 1;
  recordCurrentFitnessStats();
  redraw();
}

// --- Běh (start/pauza/rychlost) ----------------------------------------

function scheduleNextTick() {
  if (runIntervalId !== null) {
    clearInterval(runIntervalId);
  }
  var speed = Number(document.getElementById('speed-slider').value); // generací za sekundu
  var intervalMs = Math.round(1000 / speed);
  runIntervalId = setInterval(stepOnce, intervalMs);
}

// Text tlačítka start/pauza závisí na stavu (isRunning), ne jen na jazyce —
// proto to není data-i18n atribut v HTML, ale funkce volaná z obou míst,
// která stav mění, a znovu i po přepnutí jazyka (viz onLanguageChanged).
function updateStartPauseButtonText() {
  var button = document.getElementById('start-pause-btn');
  if (isRunning) {
    button.textContent = t('pause_btn');
  } else {
    button.textContent = t('start_btn');
  }
}

function startRunning() {
  if (isRunning) {
    return;
  }

  var speed = Number(document.getElementById('speed-slider').value);
  if (speed === 0) {
    // Rychlost 0 nemá smysluplný interval — "Start" (i mezerník) udělá jen
    // jeden krok, stejně jako tlačítko "Krok po kroku" (spec 10.5).
    stepOnce();
    return;
  }

  isRunning = true;
  updateStartPauseButtonText();
  scheduleNextTick();
}

function stopRunning() {
  isRunning = false;
  updateStartPauseButtonText();
  if (runIntervalId !== null) {
    clearInterval(runIntervalId);
    runIntervalId = null;
  }
}

document.getElementById('start-pause-btn').addEventListener('click', function () {
  if (isRunning) {
    stopRunning();
  } else {
    startRunning();
  }
});

// Vrátí true, pokud fokus drží prvek, který mezerník normálně používá sám
// (tlačítko, posuvník/checkbox, výběrové pole, textové pole) — v tom případě
// mezerník necháváme na pokoji, ať nedojde k dvojímu efektu (spec 10.5).
function isInteractiveElementFocused() {
  var focused = document.activeElement;
  if (focused === null) {
    return false;
  }
  var tagName = focused.tagName;
  return tagName === 'BUTTON' || tagName === 'INPUT' || tagName === 'SELECT' || tagName === 'TEXTAREA';
}

document.addEventListener('keydown', function (event) {
  if (event.code !== 'Space') {
    return;
  }
  if (isInteractiveElementFocused()) {
    return;
  }
  event.preventDefault(); // mezerník by jinak stránku odscrolloval dolů
  if (isRunning) {
    stopRunning();
  } else {
    startRunning();
  }
});

document.getElementById('step-btn').addEventListener('click', function () {
  stopRunning(); // krok po kroku dává smysl hlavně v zastaveném stavu
  stepOnce();
});

document.getElementById('reset-btn').addEventListener('click', function () {
  stopRunning();
  resetSimulation();
});

document.getElementById('reseed-btn').addEventListener('click', function () {
  stopRunning();
  resetSimulation();
});

// --- Pomocná funkce: napojí slider na textový "displej" jeho hodnoty ----
//
// SLIDER_DISPLAY_PAIRS je i seznam, který znovu použije save-load.js
// (spec 12.5, refreshSliderDisplays()) — poté, co načtená data nastaví
// hodnoty sliderů rovnou přes .value (bez uživatelského 'input' eventu),
// je potřeba tenhle displej ručně dorovnat stejnou logikou, ne ji psát
// podruhé na jiném místě.
var SLIDER_DISPLAY_PAIRS = [
  ['speed-slider', 'speed-value'],
  ['population-size-slider', 'population-size-value'],
  ['grid-size-slider', 'grid-size-value'],
  ['food-count-slider', 'food-count-value'],
  ['food-capacity-slider', 'food-capacity-value'],
  ['tournament-size-slider', 'tournament-size-value'],
  ['crossover-rate-slider', 'crossover-rate-value'],
  ['crossover-points-slider', 'crossover-points-value'],
  ['mutation-rate-slider', 'mutation-rate-value'],
  ['mutation-jump-radius-slider', 'mutation-jump-radius-value'],
  ['elite-count-slider', 'elite-count-value'],
  ['replacement-percent-slider', 'replacement-percent-value']
];

function wireSliderDisplay(sliderId, displayId) {
  var slider = document.getElementById(sliderId);
  var display = document.getElementById(displayId);
  display.textContent = slider.value;
  slider.addEventListener('input', function () {
    display.textContent = slider.value;
  });
}

function refreshSliderDisplays() {
  var i = 0;
  while (i < SLIDER_DISPLAY_PAIRS.length) {
    var sliderId = SLIDER_DISPLAY_PAIRS[i][0];
    var displayId = SLIDER_DISPLAY_PAIRS[i][1];
    document.getElementById(displayId).textContent = document.getElementById(sliderId).value;
    i = i + 1;
  }
}

var sliderDisplayIndex = 0;
while (sliderDisplayIndex < SLIDER_DISPLAY_PAIRS.length) {
  wireSliderDisplay(SLIDER_DISPLAY_PAIRS[sliderDisplayIndex][0], SLIDER_DISPLAY_PAIRS[sliderDisplayIndex][1]);
  sliderDisplayIndex = sliderDisplayIndex + 1;
}

// --- Strukturální ovládací prvky: rychlost (za běhu), velikost plochy, ---
// velikost populace, množství krmení ----------------------------------

document.getElementById('speed-slider').addEventListener('input', function () {
  if (!isRunning) {
    return;
  }
  var speed = Number(document.getElementById('speed-slider').value);
  if (speed === 0) {
    // Přetažení na 0 za běhu nemá smysluplný interval — zastavíme (spec 10.5).
    stopRunning();
  } else {
    scheduleNextTick(); // za běhu se rychlost projeví hned, ne až dalším startem
  }
});

document.getElementById('grid-size-slider').addEventListener('change', function () {
  // Velikost plochy mění i délku genomu (počet bitů na osu) — vyžaduje
  // kompletní restart simulace, nejde jen "dopočítat".
  stopRunning();
  resetSimulation();
});

function adjustPopulationSize() {
  var targetSize = Number(document.getElementById('population-size-slider').value);

  if (targetSize > population.length) {
    var toAdd = targetSize - population.length;
    var added = createRandomPopulation(toAdd, gridConfig, rng);
    var i = 0;
    while (i < added.length) {
      population.push(added[i]);
      i = i + 1;
    }
  } else {
    while (population.length > targetSize) {
      population.pop();
    }
  }

  redraw();
}

document.getElementById('population-size-slider').addEventListener('change', adjustPopulationSize);

document.getElementById('food-count-slider').addEventListener('change', function () {
  if (!isManualFoodModeActive()) {
    regenerateRandomFood();
  }
});

document.getElementById('food-capacity-slider').addEventListener('change', function () {
  // Nová kapacita se projeví na nově vzniklém krmení — v náhodném režimu je
  // to nejjednodušší rozhodit ho znovu, ať se to hned promítne i vizuálně;
  // v ručním režimu zůstává už nakreslené krmení s původní kapacitou (stejné
  // chování jako food-count-slider výše).
  if (!isManualFoodModeActive()) {
    regenerateRandomFood();
  } else {
    redraw(); // aspoň se přepočítá barevná škála podle nové kapacity
  }
});

// --- Zoom ovládání --------------------------------------------------------
//
// Zoom škáluje celý panel simulace (#zoom-wrapper: canvas + stats +
// souřadnice kurzoru + graf fitness), ne jen samotný canvas — viz applyZoom
// v render.js a spec 8.1.

var zoomWrapper = document.getElementById('zoom-wrapper');
var zoomSlider = document.getElementById('zoom-slider');
zoomSlider.addEventListener('input', function () {
  var zoomFactor = Number(zoomSlider.value);
  applyZoom(zoomWrapper, zoomFactor);
});

// --- Fullscreen (spec 10.6) -----------------------------------------------
//
// Fullscreen API je požádané přímo na #canvas-area — prohlížeč pak sám
// zobrazí přes celou obrazovku jen tenhle prvek (a jeho potomky: canvas,
// stats, kurzor, graf fitness), #controls jako sourozenec zůstane mimo,
// není potřeba ho schovávat ručně.

var fullscreenBtn = document.getElementById('fullscreen-btn');

function updateFullscreenButtonText() {
  if (document.fullscreenElement) {
    fullscreenBtn.textContent = t('fullscreen_exit_btn');
  } else {
    fullscreenBtn.textContent = t('fullscreen_enter_btn');
  }
}

fullscreenBtn.addEventListener('click', function () {
  if (document.fullscreenElement) {
    document.exitFullscreen();
  } else {
    document.getElementById('canvas-area').requestFullscreen();
  }
});

// fullscreenchange se spustí při vstupu i výstupu (i po stisku Esc, kdy
// exitFullscreen() nevoláme sami) — jediné spolehlivé místo pro obojí.
document.addEventListener('fullscreenchange', function () {
  updateFullscreenButtonText();
  updateCanvasSize(); // dostupné místo se vstupem/výstupem z fullscreenu skokově změní
  redraw();
});

// --- Sbalitelné sekce nastavení (accordion, spec 10.7) ---------------------
//
// Klik na nadpis (legend) sbalí/rozbalí zbytek fieldsetu (viz .collapsed v
// style.css). Tooltip ikonka je součástí legendy, ale klik na ni sbalení
// spustit nesmí, ať jde na ni nezávisle najet myší/kliknout — proto se
// kliky z .help-icon rovnou přeskočí.
var controlLegends = document.querySelectorAll('#controls legend');
var legendIndex = 0;
while (legendIndex < controlLegends.length) {
  controlLegends[legendIndex].addEventListener('click', function (event) {
    if (event.target.classList.contains('help-icon')) {
      return;
    }
    event.currentTarget.parentElement.classList.toggle('collapsed');
  });
  legendIndex = legendIndex + 1;
}

// --- i18n: obnovení textů generovaných za běhu (mimo data-i18n) ------------
//
// Statické popisky (legendy, labely, texty voleb) mají atribut data-i18n a
// přeloží se samy uvnitř applyTranslations() (viz js/i18n.js). Tahle funkce
// dorovná zbytek — texty, které main.js sám skládá za běhu podle stavu
// simulace, ne jen podle jazyka. Volá ji setLanguage() po každém přepnutí.
function onLanguageChanged() {
  updateStatsLine();
  updateCursorPositionLine();
  updateStartPauseButtonText();
  updateFullscreenButtonText();
  setStatus(lastStatusKey);
  // save-load.js se načítá až po tomhle souboru a má vlastní obdobný
  // stavový řádek (#saveload-status-line) — stejný "volitelný hook" vzor
  // jako setLanguage() používá pro tuhle funkci samotnou (viz i18n.js).
  if (typeof onSaveLoadLanguageChanged === 'function') {
    onSaveLoadLanguageChanged();
  }
}

// --- Úvodní inicializace ------------------------------------------------

updateStartPauseButtonText();
updateFullscreenButtonText();
resetSimulation(true); // spec 13.1: první krmení je vždy náhodně rozhozené, i když UI ukazuje "ruční"
setStatus('status_running');
