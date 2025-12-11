import turtle
import random

# This dictionary tells how to replace the symbols
rules = {
    "F": "F+F-+-F+F"   # this will be then changed (testing mode)
}


# This dictionary tells  what each symbol does
actions = {
    "F": "draw_forward",   
    "+": "turn_right",     
    "-": "turn_left"       
}

##Here are strings alternated, the symbols are replaced by the rules above

def apply_rules(old_string):
    new_string = "" #start with empty string
    

    for character in old_string:  #one charater at itme
        if character in rules:    # if the leter/symbol has a rule then replace it with it
            new_string += rules[character]   # replace if it has a rule
        else:
            new_string += character          # keep the same if not
                                    
                                             # and then build a new string 
    return new_string



#repeat the rules (and since this is L-systems, the rules apply many times)

def create_lsystem(axiom, number_of_times):
    result = axiom

    for i in range(number_of_times):  #loop, rewritting the string by the amount set in num_of_times
        result = apply_rules(result)
#
    return result



# draw (the turtle follows the rules = yipeee)
def draw_with_turtle(instructions, step_size=10, angle=90):
    t = turtle.Turtle()
    t.speed(0)   
    t.color('green')
    t.shape("turtle")
    screen = turtle.Screen()
    turtle.TurtleScreen._RUNNING=True
    

    for char in instructions:
        # everything in the string instruction is looked at (one character at a time)
        action = actions.get(char, None)

        if action == "draw_forward":
            t.forward(step_size)
            r=random.random()
            g=random.random()
            b=random.random()
            t.color(r,g,b)
     
        elif action == "turn_right":
            t.right(angle)
        elif action == "turn_left":
            t.left(angle)
        # ignore symbols we don’t know

    screen.exitonclick()  #stays upon until its clicked


# TEST
axiom = "F--F--F"

#not stable 
iterations = int(input('Iterations #:'))


# final string
final_string = create_lsystem(axiom, iterations)
print("L-system output:")
print(final_string)

# drawing c
draw_with_turtle(final_string, step_size=10, angle=60)
