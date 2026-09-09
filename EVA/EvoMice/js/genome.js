// EvoMice — datový model: mřížka, kódování genomu, myš a krmení.
//
// Genom myši je pole bitů (0/1), pevné délky, které kóduje souřadnici (x, y)
// na mřížce: prvních `bitsX` bitů je x, zbylých `bitsY` bitů je y.
// Tahle souřadnice je celý "život" myši — žádná jiná informace v genomu není.

// --- Konfigurace mřížky -----------------------------------------------

// Kolik bitů potřebujeme, abychom binárně pojmenovali `cellCount` různých
// buněk (hodnoty 0 .. cellCount-1)?
function bitsNeeded(cellCount) {
  var bits = 1;
  while (Math.pow(2, bits) < cellCount) {
    bits = bits + 1;
  }
  return bits;
}

// Vytvoří konfiguraci mřížky o daném počtu buněk na osu x a y.
// Odvodí z toho délku genomu (bitsX + bitsY).
function createGridConfig(cellsX, cellsY) {
  var config = {
    cellsX: cellsX,
    cellsY: cellsY,
    bitsX: bitsNeeded(cellsX),
    bitsY: bitsNeeded(cellsY)
  };
  return config;
}

// --- Kódování a dekódování souřadnice ----------------------------------

// Zakóduje nezáporné celé číslo `value` do pole bitů délky `bitCount`
// (bit s nejvyšší váhou první — "MSB first").
function encodeCoordinate(value, bitCount) {
  var bits = new Array(bitCount);
  var remaining = value;
  var i = bitCount - 1;
  while (i >= 0) {
    bits[i] = remaining % 2;
    remaining = Math.floor(remaining / 2);
    i = i - 1;
  }
  return bits;
}

// Dekóduje pole bitů zpět na celé číslo a zabalí ho do rozsahu mřížky
// (modulo `cellCount`) — díky tomu je dekódování validní i pro genomy
// vzniklé mutací/křížením, kde binární hodnota může přesáhnout velikost
// mřížky (bitCount pokrývá cellCount, ale ne nutně přesně).
function decodeCoordinate(bits, startIndex, bitCount, cellCount) {
  var value = 0;
  var i = 0;
  while (i < bitCount) {
    value = value * 2 + bits[startIndex + i];
    i = i + 1;
  }
  return value % cellCount;
}

// Zakóduje souřadnici (x, y) do jednoho genomu (pole bitů: x-část + y-část).
function encodeGenome(x, y, gridConfig) {
  var bitsX = encodeCoordinate(x, gridConfig.bitsX);
  var bitsY = encodeCoordinate(y, gridConfig.bitsY);
  var genome = bitsX.concat(bitsY);
  return genome;
}

// Dekóduje genom zpět na souřadnici {x, y}.
function decodeGenome(genome, gridConfig) {
  var x = decodeCoordinate(genome, 0, gridConfig.bitsX, gridConfig.cellsX);
  var y = decodeCoordinate(genome, gridConfig.bitsX, gridConfig.bitsY, gridConfig.cellsY);
  return { x: x, y: y };
}

// --- Myš (jedinec populace) --------------------------------------------

// Vytvoří myš na dané souřadnici. Genom se rovnou zakóduje ze souřadnice.
function createMouse(x, y, gridConfig) {
  var mouse = {
    genome: encodeGenome(x, y, gridConfig),
    x: x,
    y: y,
    fitness: 0
  };
  return mouse;
}

// Po změně genomu (mutace/křížení na úrovni bitů) je potřeba přepočítat
// dekódovanou souřadnici x/y, aby odpovídala aktuálnímu genomu.
function syncMousePositionFromGenome(mouse, gridConfig) {
  var decoded = decodeGenome(mouse.genome, gridConfig);
  mouse.x = decoded.x;
  mouse.y = decoded.y;
}

// Opačný směr: po geometrické operaci (myš dostala novou souřadnici přímo,
// ne přes bity) je potřeba znovu zakódovat genom, aby zůstal zdrojem pravdy.
function syncMouseGenomeFromPosition(mouse, gridConfig) {
  mouse.genome = encodeGenome(mouse.x, mouse.y, gridConfig);
}

// --- Krmení --------------------------------------------------------------

// Krmení nemá genom, jen souřadnici a množství (spec 10.3) — kolik "porcí"
// ještě zbývá. Nové krmení vždy vzniká plné, na úrovni aktuální kapacity.
function createFood(x, y, capacity) {
  var food = { x: x, y: y, amount: capacity };
  return food;
}

// --- Self-testy ------------------------------------------------------
//
// Jednoduché ověření round-tripu encode -> decode v konzoli prohlížeče
// (i při spuštění přes `node js/genome.js`). Chyba se ohlásí přes
// console.assert (vypíše se jen když test neprojde).

function runGenomeSelfTests() {
  var testsRun = 0;

  // Test 1: bitsNeeded pro typické velikosti mřížky.
  console.assert(bitsNeeded(1) === 1, 'bitsNeeded(1) má být 1');
  console.assert(bitsNeeded(2) === 1, 'bitsNeeded(2) má být 1');
  console.assert(bitsNeeded(3) === 2, 'bitsNeeded(3) má být 2');
  console.assert(bitsNeeded(256) === 8, 'bitsNeeded(256) má být 8');
  console.assert(bitsNeeded(257) === 9, 'bitsNeeded(257) má být 9');
  testsRun = testsRun + 5;

  // Test 2: round-trip encode/decode přes několik velikostí mřížky a souřadnic.
  var gridSizesToTest = [2, 5, 16, 64, 256];
  var gridIndex = 0;
  while (gridIndex < gridSizesToTest.length) {
    var size = gridSizesToTest[gridIndex];
    var gridConfig = createGridConfig(size, size);

    var x = 0;
    while (x < size) {
      var y = 0;
      while (y < size) {
        var genome = encodeGenome(x, y, gridConfig);
        var decoded = decodeGenome(genome, gridConfig);
        console.assert(
          decoded.x === x && decoded.y === y,
          'round-trip selhal pro mřížku ' + size + 'x' + size + ', x=' + x + ', y=' + y
        );
        testsRun = testsRun + 1;
        // Pro velké mřížky netestujeme úplně všechny buňky (bylo by jich moc),
        // jen náhodný vzorek posunem o víc než 1.
        y = y + (size > 16 ? 7 : 1);
      }
      x = x + (size > 16 ? 5 : 1);
    }
    gridIndex = gridIndex + 1;
  }

  // Test 3: createMouse uloží genom odpovídající zadané souřadnici.
  var gridConfig64 = createGridConfig(64, 64);
  var mouse = createMouse(10, 20, gridConfig64);
  var decodedMouse = decodeGenome(mouse.genome, gridConfig64);
  console.assert(
    decodedMouse.x === 10 && decodedMouse.y === 20,
    'createMouse: genom neodpovídá zadané souřadnici'
  );
  testsRun = testsRun + 1;

  // Test 4: syncMousePositionFromGenome a syncMouseGenomeFromPosition jsou navzájem konzistentní.
  mouse.genome[0] = mouse.genome[0] === 0 ? 1 : 0; // ručně "zmutujeme" první bit
  syncMousePositionFromGenome(mouse, gridConfig64);
  syncMouseGenomeFromPosition(mouse, gridConfig64);
  var recheck = decodeGenome(mouse.genome, gridConfig64);
  console.assert(
    recheck.x === mouse.x && recheck.y === mouse.y,
    'sync funkce nejsou navzájem konzistentní'
  );
  testsRun = testsRun + 1;

  console.log('EvoMice: genom self-test hotov (' + testsRun + ' dílčích ověření). ' +
    'Pokud výše nejsou žádné "Assertion failed" zprávy, vše je v pořádku.');
}

runGenomeSelfTests();
