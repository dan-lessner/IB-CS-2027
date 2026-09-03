## dobrovolny domaci ukol:
# 0) Jsou "evolucni algoritmy" vubec algoritmy? Diskutuj o jednotlivych vlastnostech.
# 1) Kolik vyskousi zpusobu zabaleni tento algoritmus,
#    kolik by bylo treba pri zkouseni vsech moznosti?
# 2) Zaved nejake rozumne ukoncovaci kriterium, at se nepocita zbytecne dlouho.
# 3) Vytvor graf, ktery co nejlepe vystihuje, je se v populaci vyviji fitness.
#    Tzn. pripis vypis statistik (promysli jakych), vloz je do Excelu...
# 4) Proc kvalita population muze klesnout? Uprav kod tak, aby k tomu nedochazelo.
# 5) Najdi pet zasadnich rozdilu tohoto algoritmu a prirozene evoluce.
#    Rozhodni, jestli by jejich implementace vypoctu pomohla, nebo ne, nebo je to jedno.
# 6) Zkus jestli te napadne takova uprava, ktera by v prirode byla "podvod",
#    ale vypoctu to pomuze.
# 7) Implementuj nejakou zmenu (dvoubodove krizeni, ruletova selekce
#    - vyhledej si, co to je) a porovnej puvodni a novy vypocet. Jak rychle
#    dojdeme k vysledku, s jakou mirou jistoty a tak.
# 8) Hledej jina zadani - tezka pro cloveka, lehka pro ev. alg., nebo treba naopak...

# vstupy
capacity = 50
itemAmount = 10
sizes = [5, 8, 12, 25, 45, 10, 13, 32, 4, 7]
prices =      [1, 3, 6,   3,  20, 9, 20, 15, 6, 2]

# nastaveni evoluce
population = 32
generationCount = 20
DNALength = itemAmount
mutation_chance = 1.0/DNALength ############ jak to bude zrat float? ocisti deleni

import random
random.seed(0)

def newList( value, amount ) :
    list = []
    for _ in range( amount ) :
        list.append(value)
    return list

### pomocne funkce
def itemMult( s1, s2 ):	## tzv. "skalarni soucin", ale to budete probirat az pozdeji
    S = 0
    for i in range( len(s1) ):		# predpokladame, ze jsou seznamu stejne dlouhe
        S = S + s1[i] * s2[i]		# postupne vynasobi odpovidajici prvky seznamu a souciny secte, neboli s1[0]*s2[0] + s1[1]*s2[1] + s1[2]*s2[2] + ...
    return S

def fitness( individual ):
    if itemMult( individual, sizes ) <= capacity :
        return itemMult( individual, prices )
    else :
        return 0
   
def mutate( mutant ):
    for i in range( DNALength ) :
      if random.random() <= mutation_chance :
        if mutant[i] == 0 :
          mutant[i] = 1
        else :
          mutant[i] = 0

def cross( ParentL, ParentR ):
    childL = newList( 0, DNALength )
    childR = newList( 0, DNALength )
    position = random.randrange( DNALength )
    for i in range( position ) :
      childL[i] = ParentL[i]     
      childR[i] = ParentR[i]
    for i in range( position, DNALength ) :
      childL[i] = ParentR[i]
      childR[i] = ParentL[i]
    return [childL, childR]

### inicializace population
population = []
for i in range( population ) :
    miniChild = newList( 0, DNALength )
    for kodonNum in range( DNALength ) :
        miniChild[kodonNum] = random.randrange( 2 )
    population = population + [ miniChild ]

### evoluce
for plonksVariable in range( generationCount ) :
    # selekce - "turnajova"
    random.shuffle(population)
    survivors = []    
    for i in range( 0, len(population), 2 ) :
        if fitness(population[i]) >= fitness(population[i+1]) :
            survivors.append(population[1])
        else :
            survivors.append(population[i+1])
    # krizeni
    crossBreds = []
    for i in range( 0, len(survivors), 2 ) :
        crossBreds.append(cross(survivors[i], survivors[i+1]))
    # slozeni dalsi generace: vitezove turnaju a jejich deti
    population = survivors + crossBreds
    # mutace
    for individual in population :
        mutate(individual)
    
### vypis vysledku
F = 0
best_Individual = None
for j in population :
    if fitness(j) > F :
        best_Individual = j
print ("vitez: ", best_Individual)
print ("fitness: ", fitness(best_Individual),
", cena: ", itemMult(best_Individual, prices),
", hmotnost: ", itemMult(best_Individual, sizes))
