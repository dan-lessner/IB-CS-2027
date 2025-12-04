import turtle as t

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

print(letters, rules)


def rewrite(string, arr, rules):
    global instr
    
    letters = [i for i in arr]
    instructions = []
    for a in string:
        if a in letters:
            instructions.append(rules[letters.index(a)])
        else:
            instructions.append(a)    
    instr = ("".join(map(str, instructions)))
    return
            
                
for i in range(iterations):
    rewrite(instr, letters, rules)

print(instr)

x = []
y = []
face = []

for c in instr:
    match c:
        case "F":
            t.forward(100)
        case "-":
            t.left(ang)
        case "+":
            t.right(ang)
        case "[":
            x.append(t.xcor)
            y.append(t.ycor)
            face.append(t.heading())
        case "]":
            t.setx(x.pop())
            t.sety(y.pop())
            t.setheading(face.pop())
