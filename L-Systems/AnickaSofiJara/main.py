import turtle

iterations = int(input("Number of iterations: ")) #users input
angle = int(input("Angle: "))
axiom = input("Axiom: ")
print("Letters used (e.g. F X): ", end="")
letters = input().split()

rules = {}
for L in letters:
    rules[L] = input(f"Rule for {L}: ")


def rewrite(string, rules): #L-system rewrite
    new = []
    for char in string:
        if char in rules:
            new.append(rules[char])
        else:
            new.append(char)
    return "".join(new)

current = axiom
for _ in range(iterations):
    current = rewrite(current, rules)

print("\nFinal string:")
print(current)
print()


turtle.speed(1)  # drawing speed (1-10, 0 = fastest but no animation)
turtle.showturtle()  # make turtle visible
turtle.tracer(1)  # update screen after each drawing action
turtle.pensize(3)  # make lines thicker
stack = []

distance = 40  # movement distance (increased for larger drawing)

def store_state():
    stack.append((turtle.position(), turtle.heading()))

def restore_state():
    pos, head = stack.pop()
    turtle.penup()
    turtle.setposition(pos)
    turtle.setheading(head)
    turtle.pendown()


for c in current: #interpretation
    if c == "F":
        turtle.forward(distance)
    elif c == "+":
        turtle.right(angle)
    elif c == "-":
        turtle.left(angle)
    elif c == "[":
        store_state()
    elif c == "]":
        restore_state()

turtle.done()
