import turtle as t

print("Add new shape? Y/N:", end=" ") #prozatím zbytečná otázka - pamět zatím není zprovozněna
ans = input()
if ans == "Y":
    print("Name of the shape:", end=" ") #input všech prvků potřebných od uživatele
    name = input()
    print("# of iterations:", end=" ")
    iterations = int(input())
    print("angle:", end=" ")
    ang = int(input())
    print("Axiom:", end=" ")
    instr = str(input())
    print("Letters used:", end=" ")
    letters = input().split()

    rules = []

    for i in range(len(letters)):
        print("Rule: ", letters[i], "=", end=" ")
        rules.append(input())


    def rewrite(string, arr, rules):    #funkce, která přepisuje axiom
        global instr       #globální proměnná púoužívaná napříč celým kódem, ne pouze v této funkci
        
        letters = [i for i in arr]      #list písmen
        instructions = []
        for a in string:     #loop který postupně prochází všechny symboly v momentální verzi axiomu, a všechny písmena přepisuje příslušnými pravidly
            if a in letters:      
                instructions.append(rules[letters.index(a)])
            else:
                instructions.append(a)    
        instr = ("".join(map(str, instructions)))
        return
    

    # zapisování do paměti: prozatím nezprovozněno
    # Franta = [name, iterations, ang, instr, letters, rules]

    # with open("mem.txt", "a") as w: 
    #     w.write(name)
    #     w.write(str(iterations))
    #     w.write(str(ang))
    #     for a in instr:
    #         w.write(a, end=", ")
    #     w.write("")
    #     for a in letters:
    #         w.write(a, end=", ")
    #     w.write("")
    #     for a in rules:
    #         w.write(a, end=", ")
    #     w.write("")

if ans == "N":
    # shapes = []
    # with open("mem.txt", "r") as f:
    #     lines = f.readlines()
    
    
    # print("Name of the shape?", end=" ")
    # name = input()
    print("Feature coming soon")



for i in range(iterations):   #aplikování funkce rewrite na axiom (počet iterací)-krát
        rewrite(instr, letters, rules)



x = []
y = []
face = []
t.speed(0)
t.hideturtle()

for c in instr:  #kreslení podle instrukcí (finální forma axiomu) za pomocí želvy :3
    match c:
        case "F":
            t.forward(5)
        case "-":
            t.left(ang)
        case "+":
            t.right(ang)
        case "[":
            x.append(t.xcor())
            y.append(t.ycor())
            face.append(t.heading())
        case "]":
            t.setx(x.pop())
            t.sety(y.pop())
            t.setheading(face.pop())

t.mainloop()
