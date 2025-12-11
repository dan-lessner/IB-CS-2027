import turtle
axiom = "F"
rules = {"F": "F+F-F-F+F"}

interations = 4

def apply_rules (axiom, rules, iterations):
    current_string = axiom
    for _ in range(iterations):
        next_string = ""
        for char in current_string:
            next_string += rules.get(char, char)
        current_string = next_string
    return current_string
iterations = 4
result = apply_rules(axiom, rules, iterations)
print (result)


import turtle
def draw_l_systems (instructions, angle = 90, distance = 5):
    for command in instructions:
        if command == "F":
            turtle.forward (distance)
        elif command == "+":
            turtle.right (angle)
        elif command == "-":
            turtle.left (angle)

turtle.speed (0)
draw_l_systems (result)
turtle.done () 
screen = turtle.Screen ()

turtle.Turtle.Screen._RUNNING = True 