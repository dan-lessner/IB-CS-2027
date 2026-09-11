// CurveFitEA — evoluční jádro (selekce, křížení, mutace, náhrada generace).
//
// Stejné rozdělení vrstev jako EvoMice (spec 6a, viz i tamní js/ga.js):
//   1. ORCHESTRACE — stepGeneration() čte jako sled kroků: spočítej chybu,
//      seřaď, nech přežít elitu, zbytek doplň přes select()/crossover()/mutate().
//   2. IMPLEMENTACE — teprve uvnitř select()/crossover()/mutate() se řeší
//      konkrétní manipulace s "DNA": buď bity zakódovaného genomu (bitová
//      varianta), nebo přímo reálné koeficienty (doménová varianta).
// Kdo chce vědět "co se děje", čte stepGeneration(). Kdo chce vědět "jak
// přesně", zanoří se do konkrétní implementační funkce níže.

// --- Výchozí parametry evoluce ------------------------------------------

function createDefaultGaParams() {
  return {
    degree: 1,                     // stupeň polynomu (spec 1: 1 = přímka, výchozí)
    fitnessType: 'sse',            // 'sse' (výchozí) | 'mae' | 'max-error' | 'hit-count'
    fitnessTolerance: 1,           // použito jen pro 'hit-count' (spec 7)

    selectionMethod: 'roulette',   // 'roulette' (fitness-proporcionální) | 'tournament'
    tournamentSize: 3,

    crossoverRate: 0.8,            // pravděpodobnost, že potomek vznikne křížením (jinak jen mutovaná kopie 1 rodiče)
    crossoverType: 'one-point',    // 'one-point' | 'multi-point' | 'uniform' (bitové) | 'param-alternate' | 'line-point' (doménové)
    crossoverPoints: 3,            // počet bodů řezu, použito jen pro 'multi-point'

    mutationType: 'bit-flip',      // 'bit-flip' (bitové) | 'gaussian-jump' (doménové)
    mutationRate: 0.02,            // pravděpodobnost převrácení jednoho bitu (bit-flip)
    mutationSigma: 0.3,            // směrodatná odchylka náhodného posunu koeficientu (gaussian-jump)

    eliteCount: 0,                 // kolik nejlepších jedinců přežije beze změny do další generace

    replacementMode: 'full',       // 'full' (celá generace najednou) | 'partial' (jen nejhorší X %)
    replacementPercent: 50         // použito jen pro 'partial'
  };
}

// --- Hlavní evoluční krok (orchestrace) ---------------------------------

// Provede jednu generaci: ohodnotí populaci podle chyby vůči bodům, nechá
// přežít elitu (a případně další nejlepší přeživší), zbylá místa doplní
// novými potomky. Vrací novou populaci (stejné velikosti jako vstupní).
function stepGeneration(population, points, params, rng) {
  // 1) Ohodnoť aktuální populaci — nižší chyba (SSE/MAE) = vyšší fitness.
  var coeffRange = computeCoeffRange(points);
  computeFitness(population, points, params.fitnessType, params.fitnessTolerance);

  // 2) Seřaď od nejlepší po nejhorší — elitismus i "náhrada nejhorších X %"
  //    z tohohle pořadí přímo vychází.
  var sorted = sortPopulationByFitnessDescending(population);

  var eliteCount = Math.min(params.eliteCount, sorted.length);
  var replaceCount = determineReplaceCount(sorted.length, eliteCount, params);
  var survivorsCount = sorted.length - eliteCount - replaceCount;

  var nextGeneration = [];

  // 3) Elita přežívá beze změny.
  var i = 0;
  while (i < eliteCount) {
    nextGeneration.push(sorted[i]);
    i = i + 1;
  }

  // 4) Další nejlepší přeživší — relevantní hlavně pro replacementMode='partial'.
  var j = eliteCount;
  while (j < eliteCount + survivorsCount) {
    nextGeneration.push(sorted[j]);
    j = j + 1;
  }

  // 5) Zbylá místa doplní nová generace potomků: selekce rodičů -> křížení
  //    (nebo jen kopie jednoho rodiče) -> mutace.
  var k = 0;
  while (k < replaceCount) {
    var childCoeffs;

    if (randomChance(rng, params.crossoverRate)) {
      var parentA = select(sorted, params, rng);
      var parentB = select(sorted, params, rng);
      childCoeffs = crossover(parentA, parentB, params, coeffRange, rng);
    } else {
      var parent = select(sorted, params, rng);
      childCoeffs = parent.coeffs.slice();
    }

    childCoeffs = mutate(childCoeffs, params, coeffRange, rng);
    nextGeneration.push(createIndividual(childCoeffs));

    k = k + 1;
  }

  return nextGeneration;
}

// Kolik jedinců (mimo elitu) se má tuhle generaci nahradit novými potomky?
// (spec, sdílená konvence EvoMice 13.9: náhrada generace nad elitismem, jsou
// to dvě nezávislé osy — viz PROGRESS.md/i18n tooltip pro vysvětlení rozdílu.)
function determineReplaceCount(totalCount, eliteCount, params) {
  var nonEliteCount = totalCount - eliteCount;

  if (params.replacementMode === 'partial') {
    var fraction = params.replacementPercent / 100;
    var count = Math.round(nonEliteCount * fraction);
    if (count < 0) {
      count = 0;
    }
    if (count > nonEliteCount) {
      count = nonEliteCount;
    }
    return count;
  }

  // 'full' (výchozí): nahradíme úplně všechny ne-elitní jedince najednou.
  return nonEliteCount;
}

// Vrátí kopii populace seřazenou od nejvyšší fitness po nejnižší (selection
// sort — pro velikosti populace v týhle simulaci dost rychlé a hlavně
// snadno čitelné, žádné komparátory, stejně jako EvoMice).
function sortPopulationByFitnessDescending(population) {
  var sorted = [];
  var i = 0;
  while (i < population.length) {
    sorted.push(population[i]);
    i = i + 1;
  }

  var n = sorted.length;
  var a = 0;
  while (a < n - 1) {
    var bestIndex = a;
    var b = a + 1;
    while (b < n) {
      if (sorted[b].fitness > sorted[bestIndex].fitness) {
        bestIndex = b;
      }
      b = b + 1;
    }
    if (bestIndex !== a) {
      var temp = sorted[a];
      sorted[a] = sorted[bestIndex];
      sorted[bestIndex] = temp;
    }
    a = a + 1;
  }

  return sorted;
}

// --- Fitness ----------------------------------------------------------------
//
// Chyba (SSE/MAE, viz model.js computeError) je "čím míň, tím líp" — pro
// selekci/řazení potřebujeme opak ("čím víc, tím líp"), proto fitness =
// 1 / (1 + chyba). Nikdy nedělí nulou (chyba >= 0), 0 chyby -> fitness 1.
function computeFitness(population, points, fitnessType, fitnessTolerance) {
  var i = 0;
  while (i < population.length) {
    var individual = population[i];
    individual.error = computeError(individual.coeffs, points, fitnessType, fitnessTolerance);
    individual.fitness = 1 / (1 + individual.error);
    i = i + 1;
  }
}

// --- Selekce rodiče ------------------------------------------------------
//
// Pravděpodobnost stát se rodičem roste s fitness (tj. klesá s chybou).

function select(population, params, rng) {
  if (params.selectionMethod === 'tournament') {
    return selectByTournament(population, params.tournamentSize, rng);
  }
  // výchozí varianta ('roulette'): fitness-proporcionální výběr
  return selectByRoulette(population, rng);
}

// Turnajová selekce: vyber `tournamentSize` náhodných jedinců a nech
// vyhrát toho s nejvyšší fitness. Vyšší tournamentSize = vyšší tlak
// selekce (rychlejší konvergence, ale menší diverzita).
function selectByTournament(population, tournamentSize, rng) {
  var bestSoFar = population[randomInt(rng, population.length)];
  var i = 1;
  while (i < tournamentSize) {
    var challenger = population[randomInt(rng, population.length)];
    if (challenger.fitness > bestSoFar.fitness) {
      bestSoFar = challenger;
    }
    i = i + 1;
  }
  return bestSoFar;
}

// Ruletová (fitness-proporcionální) selekce: šance na výběr je úměrná
// podílu fitness jedince na celkové fitness populace.
function selectByRoulette(population, rng) {
  var totalFitness = 0;
  var i = 0;
  while (i < population.length) {
    totalFitness = totalFitness + population[i].fitness;
    i = i + 1;
  }

  if (totalFitness <= 0) {
    // Fitness je vždy > 0 (viz computeFitness), ale kdyby přece jen celková
    // suma vyšla 0/záporně (obranná pojistka), vybereme rovnoměrně náhodně.
    return population[randomInt(rng, population.length)];
  }

  var threshold = rng() * totalFitness;
  var cumulative = 0;
  var j = 0;
  while (j < population.length) {
    cumulative = cumulative + population[j].fitness;
    if (cumulative >= threshold) {
      return population[j];
    }
    j = j + 1;
  }

  // Sem se dostaneme jen kvůli zaokrouhlovacím chybám na floatech.
  return population[population.length - 1];
}

// --- Křížení ---------------------------------------------------------------
//
// Bitové varianty (spec 4.1, jednobodové/vícebodové/uniformní — stejný kód
// jako EvoMice, jen genom místo x/y souřadnic) + doménové varianty (spec
// 4.2 — střídavé přebírání celých koeficientů, bod mezi rodiči).

function crossover(parentA, parentB, params, coeffRange, rng) {
  if (params.crossoverType === 'multi-point') {
    var genomeA1 = encodeGenome(parentA.coeffs, coeffRange);
    var genomeB1 = encodeGenome(parentB.coeffs, coeffRange);
    var childBits1 = crossoverMultiPointBits(genomeA1, genomeB1, params.crossoverPoints, rng);
    return decodeGenome(childBits1, params.degree, coeffRange);
  }
  if (params.crossoverType === 'uniform') {
    var genomeA2 = encodeGenome(parentA.coeffs, coeffRange);
    var genomeB2 = encodeGenome(parentB.coeffs, coeffRange);
    var childBits2 = crossoverUniformBits(genomeA2, genomeB2, rng);
    return decodeGenome(childBits2, params.degree, coeffRange);
  }
  if (params.crossoverType === 'param-alternate') {
    return crossoverParamAlternate(parentA, parentB, rng);
  }
  if (params.crossoverType === 'line-point') {
    return crossoverLinePoint(parentA, parentB, rng);
  }
  // výchozí varianta ('one-point'): klasický jednobodový crossover přes bity genomu
  var genomeA0 = encodeGenome(parentA.coeffs, coeffRange);
  var genomeB0 = encodeGenome(parentB.coeffs, coeffRange);
  var childBits0 = crossoverOnePointBits(genomeA0, genomeB0, rng);
  return decodeGenome(childBits0, params.degree, coeffRange);
}

// Klasický jednobodový crossover přes celý binární řetězec (bity všech
// koeficientů dohromady, řez může padnout kamkoliv).
function crossoverOnePointBits(genomeA, genomeB, rng) {
  var length = genomeA.length;
  var cutPoint = 1 + randomInt(rng, length - 1); // aspoň 1 bit od každého rodiče
  var childBits = new Array(length);
  var i = 0;
  while (i < length) {
    if (i < cutPoint) {
      childBits[i] = genomeA[i];
    } else {
      childBits[i] = genomeB[i];
    }
    i = i + 1;
  }
  return childBits;
}

// Vícebodový crossover: víc bodů řezu, rodiče se u každého bodu střídají.
function crossoverMultiPointBits(genomeA, genomeB, numberOfPoints, rng) {
  var length = genomeA.length;
  var cutPoints = chooseDistinctCutPoints(numberOfPoints, length, rng);

  var childBits = new Array(length);
  var currentParentIsA = true;
  var nextCutIndex = 0;
  var i = 0;
  while (i < length) {
    while (nextCutIndex < cutPoints.length && i === cutPoints[nextCutIndex]) {
      currentParentIsA = !currentParentIsA;
      nextCutIndex = nextCutIndex + 1;
    }
    if (currentParentIsA) {
      childBits[i] = genomeA[i];
    } else {
      childBits[i] = genomeB[i];
    }
    i = i + 1;
  }
  return childBits;
}

// Vybere `count` různých bodů řezu z rozsahu [1, length-1], vzestupně seřazené.
function chooseDistinctCutPoints(count, length, rng) {
  var maxPossible = length - 1;
  if (count > maxPossible) {
    count = maxPossible;
  }

  var points = [];
  while (points.length < count) {
    var candidate = 1 + randomInt(rng, maxPossible);
    if (!arrayContainsValue(points, candidate)) {
      points.push(candidate);
    }
  }

  // Vzestupné seřazení výběrem — pole je malé (řádově jednotky bodů).
  var n = points.length;
  var a = 0;
  while (a < n - 1) {
    var minIndex = a;
    var b = a + 1;
    while (b < n) {
      if (points[b] < points[minIndex]) {
        minIndex = b;
      }
      b = b + 1;
    }
    if (minIndex !== a) {
      var temp = points[a];
      points[a] = points[minIndex];
      points[minIndex] = temp;
    }
    a = a + 1;
  }

  return points;
}

function arrayContainsValue(array, value) {
  var i = 0;
  while (i < array.length) {
    if (array[i] === value) {
      return true;
    }
    i = i + 1;
  }
  return false;
}

// Uniformní (per-bit) crossover: každý bit nezávisle padne na 50:50
// od jednoho nebo druhého rodiče.
function crossoverUniformBits(genomeA, genomeB, rng) {
  var length = genomeA.length;
  var childBits = new Array(length);
  var i = 0;
  while (i < length) {
    if (randomChance(rng, 0.5)) {
      childBits[i] = genomeA[i];
    } else {
      childBits[i] = genomeB[i];
    }
    i = i + 1;
  }
  return childBits;
}

// Doménová varianta (spec 4.2): každý koeficient nezávisle padne na 50:50
// celý (ne po bitech) od jednoho nebo druhého rodiče — "uniformní křížení
// po celých parametrech".
function crossoverParamAlternate(parentA, parentB, rng) {
  var childCoeffs = [];
  var i = 0;
  while (i < parentA.coeffs.length) {
    if (randomChance(rng, 0.5)) {
      childCoeffs.push(parentA.coeffs[i]);
    } else {
      childCoeffs.push(parentB.coeffs[i]);
    }
    i = i + 1;
  }
  return childCoeffs;
}

// Doménová varianta (spec 4.2): potomek je náhodný bod na úsečce mezi
// vektory koeficientů obou rodičů, s náhodným t ∈ [0, 1] (lineární
// interpolace — analogie geometrického křížení z EvoMice spec 6a).
function crossoverLinePoint(parentA, parentB, rng) {
  var t = rng();
  var childCoeffs = [];
  var i = 0;
  while (i < parentA.coeffs.length) {
    var value = parentA.coeffs[i] + t * (parentB.coeffs[i] - parentA.coeffs[i]);
    childCoeffs.push(value);
    i = i + 1;
  }
  return childCoeffs;
}

// --- Mutace ----------------------------------------------------------------
//
// Bitová varianta (spec 4.1: bit-flip s pravděpodobností p_mutace) +
// doménová varianta (spec 4.2: "drobná změna" — malý gaussovský posun).

function mutate(coeffs, params, coeffRange, rng) {
  if (params.mutationType === 'gaussian-jump') {
    return mutateGaussianJump(coeffs, coeffRange, params.mutationSigma, rng);
  }
  // výchozí varianta ('bit-flip'): každý bit genomu se s pravděpodobností p převrátí
  return mutateBitFlip(coeffs, params, coeffRange, rng);
}

function mutateBitFlip(coeffs, params, coeffRange, rng) {
  var genome = encodeGenome(coeffs, coeffRange);
  var i = 0;
  while (i < genome.length) {
    if (randomChance(rng, params.mutationRate)) {
      if (genome[i] === 0) {
        genome[i] = 1;
      } else {
        genome[i] = 0;
      }
    }
    i = i + 1;
  }
  return decodeGenome(genome, params.degree, coeffRange);
}

// Každý koeficient se posune o malý náhodný vektor (gaussovské rozdělení,
// směrodatná odchylka mutationSigma) místo náhodného převrácení bitů genomu.
function mutateGaussianJump(coeffs, coeffRange, mutationSigma, rng) {
  var mutated = [];
  var i = 0;
  while (i < coeffs.length) {
    var jumped = coeffs[i] + randomGaussian(rng) * mutationSigma;
    mutated.push(clampNumber(jumped, -coeffRange, coeffRange));
    i = i + 1;
  }
  return mutated;
}

// --- Inicializace populace ---------------------------------------------

function createRandomIndividual(degree, coeffRange, rng) {
  var coeffs = [];
  var i = 0;
  while (i <= degree) {
    coeffs.push(randomRange(rng, -coeffRange, coeffRange));
    i = i + 1;
  }
  return createIndividual(coeffs);
}

function createRandomPopulation(size, degree, coeffRange, rng) {
  var population = [];
  var i = 0;
  while (i < size) {
    population.push(createRandomIndividual(degree, coeffRange, rng));
    i = i + 1;
  }
  return population;
}

// --- Self-testy --------------------------------------------------------
//
// Stejný styl jako EvoMice: ověřujeme evoluční jádro přes konzoli, na
// natvrdo nastavených hodnotách (žádné UI zatím, to přijde ve fázi 6).

function runGaSelfTests() {
  var testsRun = 0;
  var rng = createRng(1234);
  var testCoeffRange = 20; // libovolná kladná hodnota, testy rozsah samy neřeší

  // --- Fitness -------------------------------------------------------
  var perfectPoints = [{ x: 0, y: 5 }, { x: 10, y: 5 }];
  var perfectIndividual = createIndividual([5]);
  var badIndividual = createIndividual([-5]);
  computeFitness([perfectIndividual, badIndividual], perfectPoints, 'sse');
  console.assert(perfectIndividual.fitness === 1, 'computeFitness: přesná shoda (chyba 0) má dát fitness 1');
  console.assert(badIndividual.fitness < perfectIndividual.fitness, 'computeFitness: horší shoda má mít nižší fitness');
  testsRun = testsRun + 2;

  // --- Křížení: všech 5 variant musí vrátit vektor koeficientů správné délky ---
  var parentA = createIndividual([2, -3, 1]);
  var parentB = createIndividual([-4, 7, -2]);
  var degreeForParents = parentA.coeffs.length - 1;
  var crossoverTypes = ['one-point', 'multi-point', 'uniform', 'param-alternate', 'line-point'];
  var typeIndex = 0;
  while (typeIndex < crossoverTypes.length) {
    var crossParams = createDefaultGaParams();
    crossParams.crossoverType = crossoverTypes[typeIndex];
    crossParams.degree = degreeForParents;
    var trial = 0;
    while (trial < 20) {
      var child = crossover(parentA, parentB, crossParams, testCoeffRange, rng);
      console.assert(
        child.length === parentA.coeffs.length,
        'crossover (' + crossParams.crossoverType + '): špatná délka vektoru koeficientů'
      );
      testsRun = testsRun + 1;
      trial = trial + 1;
    }
    typeIndex = typeIndex + 1;
  }

  // --- Mutace: obě varianty musí vrátit vektor koeficientů uvnitř rozsahu ---
  var mutationTypes = ['bit-flip', 'gaussian-jump'];
  var mutIndex = 0;
  while (mutIndex < mutationTypes.length) {
    var mutParams = createDefaultGaParams();
    mutParams.mutationType = mutationTypes[mutIndex];
    mutParams.mutationRate = 0.5; // vyšší šance na projevení mutace v testu
    mutParams.mutationSigma = 3;
    mutParams.degree = 2;
    var mtrial = 0;
    while (mtrial < 20) {
      var mutated = mutate([1, -1, 0.5], mutParams, testCoeffRange, rng);
      console.assert(mutated.length === 3, 'mutate (' + mutParams.mutationType + '): špatná délka vektoru koeficientů');
      var withinRange = true;
      var mi = 0;
      while (mi < mutated.length) {
        if (mutated[mi] < -testCoeffRange - 1e-9 || mutated[mi] > testCoeffRange + 1e-9) {
          withinRange = false;
        }
        mi = mi + 1;
      }
      console.assert(withinRange, 'mutate (' + mutParams.mutationType + '): koeficient mimo povolený rozsah');
      testsRun = testsRun + 2;
      mtrial = mtrial + 1;
    }
    mutIndex = mutIndex + 1;
  }

  // --- Selekce: obě metody vrací jedince z populace ----------------------
  var population = createRandomPopulation(30, 2, testCoeffRange, rng);
  computeFitness(population, perfectPoints, 'sse');

  var selParams1 = createDefaultGaParams();
  selParams1.selectionMethod = 'roulette';
  var picked1 = select(population, selParams1, rng);
  console.assert(population.indexOf(picked1) !== -1, 'select (roulette): vybraný jedinec musí být z populace');
  testsRun = testsRun + 1;

  var selParams2 = createDefaultGaParams();
  selParams2.selectionMethod = 'tournament';
  selParams2.tournamentSize = 4;
  var picked2 = select(population, selParams2, rng);
  console.assert(population.indexOf(picked2) !== -1, 'select (tournament): vybraný jedinec musí být z populace');
  testsRun = testsRun + 1;

  // --- stepGeneration: velikost populace se nesmí měnit napříč libovolnou --
  // kombinací náhrady generace / typu křížení / typu mutace ----------------
  var replacementModes = ['full', 'partial'];
  var crossoverKinds = ['one-point', 'line-point'];
  var mutationKinds = ['bit-flip', 'gaussian-jump'];
  var rmIndex = 0;
  while (rmIndex < replacementModes.length) {
    var ckIndex = 0;
    while (ckIndex < crossoverKinds.length) {
      var mkIndex = 0;
      while (mkIndex < mutationKinds.length) {
        var stepParams = createDefaultGaParams();
        stepParams.degree = 2;
        stepParams.replacementMode = replacementModes[rmIndex];
        stepParams.replacementPercent = 30;
        stepParams.crossoverType = crossoverKinds[ckIndex];
        stepParams.mutationType = mutationKinds[mkIndex];
        stepParams.eliteCount = 2;

        var testPopulation = createRandomPopulation(25, 2, testCoeffRange, rng);
        var testPoints = [{ x: 1, y: 2 }, { x: 5, y: -3 }, { x: 9, y: 4 }];

        var gen = 0;
        while (gen < 5) {
          testPopulation = stepGeneration(testPopulation, testPoints, stepParams, rng);
          console.assert(
            testPopulation.length === 25,
            'stepGeneration: velikost populace se nesmí měnit (' + stepParams.replacementMode + '/' +
              stepParams.crossoverType + '/' + stepParams.mutationType + ')'
          );
          gen = gen + 1;
        }
        testsRun = testsRun + 5;

        mkIndex = mkIndex + 1;
      }
      ckIndex = ckIndex + 1;
    }
    rmIndex = rmIndex + 1;
  }

  // --- Elitismus: elitní jedinec (nejlepší fitness) musí přežít beze změny -
  var eliteParams = createDefaultGaParams();
  eliteParams.degree = 0;
  eliteParams.eliteCount = 1;
  eliteParams.replacementMode = 'full';
  var eliteBest = createIndividual([5]); // přesně sedí na bodech níže
  var eliteRest = createRandomPopulation(9, 0, testCoeffRange, rng);
  var elitePopulation = [eliteBest].concat(eliteRest);
  var elitePoints = [{ x: 0, y: 5 }, { x: 10, y: 5 }];
  var eliteResult = stepGeneration(elitePopulation, elitePoints, eliteParams, rng);
  console.assert(
    eliteResult.indexOf(eliteBest) !== -1,
    'stepGeneration: elitní (nejlepší) jedinec musí přežít beze změny do další generace'
  );
  testsRun = testsRun + 1;

  // --- Random seed: stejný seed musí dát stejnou počáteční populaci -------
  var seedA = createRng(777);
  var seedB = createRng(777);
  var popA = createRandomPopulation(10, 3, testCoeffRange, seedA);
  var popB = createRandomPopulation(10, 3, testCoeffRange, seedB);
  var same = true;
  var si = 0;
  while (si < popA.length) {
    var ci = 0;
    while (ci < popA[si].coeffs.length) {
      if (popA[si].coeffs[ci] !== popB[si].coeffs[ci]) {
        same = false;
      }
      ci = ci + 1;
    }
    si = si + 1;
  }
  console.assert(same, 'random seed: stejný seed musí dát stejnou náhodnou populaci');
  testsRun = testsRun + 1;

  console.log('CurveFitEA: GA self-test hotov (' + testsRun + ' dílčích ověření). ' +
    'Pokud výše nejsou žádné "Assertion failed" zprávy, vše je v pořádku.');
}

runGaSelfTests();
