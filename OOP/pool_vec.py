import tkinter as tk
import random
import math
from turtle import position

WIDTH, HEIGHT = 600, 400
FRICTION = 0.995
DT = 1


class Vector:
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, k):
        return Vector(self.x * k, self.y * k)

    def __truediv__(self, k):
        return Vector(self.x / k, self.y / k)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def length(self):
        return math.hypot(self.x, self.y)

    def normalized(self):
        l = self.length()
        if l == 0:
            return Vector(0, 0)
        return Vector(self.x / l, self.y / l)

    def project_onto(self, other):
            length_squared = other.dot(other)
            if length_squared == 0:
                return Vector(0, 0)
            scale = self.dot(other) / length_squared
            return other * scale

class Ball:
    def __init__(self, canvas, pos, radius, color):
        self.canvas = canvas
        self.position = pos          # Vector
        self.velocity = Vector(0, 0)
        self.radius = radius
        self.id = canvas.create_oval(
            self.position.x-self.radius, self.position.y-self.radius,
            self.position.x+self.radius, self.position.y+self.radius,
            fill=color
        )
        canvas.tag_bind(self.id, "<Button-1>", self.hit)

    def hit(self, event):
        angle = random.random() * 2 * math.pi
        speed = random.uniform(6, 12)
        self.velocity = Vector(math.cos(angle), math.sin(angle)) * speed

    def move(self):
        self.position = self.position + self.velocity * DT

        # mantinely – závislé na poloměru
        if self.position.x - self.radius < 0 or self.position.x + self.radius > WIDTH:
            self.velocity.x = -self.velocity.x
            self.position.x = max(self.radius, min(WIDTH - self.radius, self.position.x))

        if self.position.y - self.radius < 0 or self.position.y + self.radius > HEIGHT:
            self.velocity.y = -self.velocity.y
            self.position.y = max(self.radius, min(HEIGHT - self.radius, self.position.y))

        self.velocity = self.velocity * FRICTION

        self.canvas.coords(
            self.id,
            self.position.x-self.radius, self.position.y-self.radius,
            self.position.x+self.radius, self.position.y+self.radius
        )

    def collide_with(self, other):
        displacement = other.position - self.position    # vektor mezi středy koulí
        distance = displacement.length()            # vzdálenost (středů) koulí
        min_distance = self.radius + other.radius
        if distance > min_distance:
            return

        # projekce rychlostí na vektor mezi středy
        self_velocity_along_displacement = self.velocity.project_onto(displacement)
        other_velocity_along_displacement = other.velocity.project_onto(displacement)

        # Předávám rychlost svojí (elastická srážka)
        self.velocity = self.velocity - self_velocity_along_displacement 
        other.velocity = other.velocity + self_velocity_along_displacement

        # Přijímám rychlost od druhé koule
        other.velocity = other.velocity - other_velocity_along_displacement
        self.velocity = self.velocity + other_velocity_along_displacement

        # oprava pozic, aby se koule nazobrazily překryté
        overlap = min_distance - distance
        correction_vector = (displacement / distance) * overlap
        self.position = self.position - correction_vector / 2
        other.position = other.position + correction_vector / 2

def tick():
    for b in balls:
        b.move()

    for i in range(len(balls)):
        for j in range(i+1, len(balls)):
            balls[i].collide_with(balls[j])

    root.after(16, tick)


root = tk.Tk()
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="darkgreen")
canvas.pack()

balls = [
    Ball(canvas, Vector(120, 200), 20, "white"),
    Ball(canvas, Vector(220, 200), 18, "red"),
    Ball(canvas, Vector(340, 200), 25, "yellow"),
    Ball(canvas, Vector(480, 200), 20, "blue"),
]

tick()
root.mainloop()
