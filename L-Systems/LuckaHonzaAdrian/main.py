# Pracuje tady někdo?? halo tady sokoli orel, ano zacina se tu pracovat, opakuji prace zacina, zacina, prepinam
import turtle
import random


iterations = int(input("iterations: "))
angle = int(input("angle (degrees): "))
axiom = input("axiom: ")
rule_input = input("rule (e.g. F=F+F--F+F): ")


rule_key, rule_value = rule_input.split("=")

# generate the L-system string
current = axiom
for i in range(iterations):
    next_string = ""
    for char in current:
        if char == rule_key:
            next_string += rule_value
        else:
            next_string += char
    current = next_string

print("\nFinal L-system string after", iterations, "iterations:")
print(current)

# legend for commands
print("\nLegend:")
print(f"+ : turn right {angle} degrees")
print(f"- : turn left {angle} degrees")
print("F : move forward")
print("[ : push position")
print("] : pop position")

