import tkinter as tk
import random
import math
from turtle import position

WIDTH, HEIGHT = 1200, 600
FRICTION = 0.97 
DT = 1
speed = 10
maxAccel = 1.5
history = []
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
    
    def angle(self):
        self.normalized(self)

    def project_onto(self, other):
            length_squared = other.dot(other)
            if length_squared == 0:
                return Vector(0, 0)
            scale = self.dot(other) / length_squared
            return other * scale
Accel = Vector(0,0)
class Player:
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
        root.bind('<KeyPress>', self.keyDown)
        root.bind('<KeyRelease>', self.keyUp)
    
    def keyDown(self, event):
        if not event.keysym in history:
            history.append(event.keysym)
    
    def keyUp(self, event):
        if event.keysym in history:
            history.pop(history.index(event.keysym))
    
    def inputHandler(self,input):
        global Accel
        
        normalizedVelocity = self.velocity.normalized()
        
        if input == "w":
           wInput = 1
        else:
            wInput = 0 
        if input == "s":
           sInput = 1
        else:
            sInput = 0 
            
        if input == "a":
           aInput = 1
        else:
            aInput = 0 
        if input == "d":
           dInput = 1
        else:
            dInput = 0 

        if dInput != 0 or aInput !=0:
            if (dInput-aInput) == -1 * normalizedVelocity.x:
                maxAccel = 3
            else:
                maxAccel = 1
        if sInput != 0 or wInput !=0:
            if (sInput-wInput) == -1 * normalizedVelocity.y:
                maxAccel = 3
            else:
                maxAccel = 1

        Accel.x = (dInput-aInput) * maxAccel
        Accel.y = (sInput-wInput) * maxAccel
        print(f"xAccel: {Accel.x} yAceel: {Accel.y}")
        self.velocity = self.velocity + Accel * DT

            
    def move(self):
        if self.velocity.length() > speed:
            self.velocity = self.velocity.normalized() * speed
        self.position = self.position + self.velocity * DT
        #print(f"xSpeed: {self.velocity.x} ySpeed: {self.velocity.y}")
        # mantinely – závislé na poloměru
        if self.position.x - self.radius < 0 or self.position.x + self.radius > WIDTH:
            self.velocity.x = -(self.velocity.x/abs(self.velocity.x))
            self.position.x = max(self.radius, min(WIDTH - self.radius, self.position.x))

        if self.position.y - self.radius < 0 or self.position.y + self.radius > HEIGHT:
            self.velocity.y = -(self.velocity.y/abs(self.velocity.y))
            self.position.y = max(self.radius, min(HEIGHT - self.radius, self.position.y))

        
        self.velocity = self.velocity * FRICTION * DT
        self.canvas.coords(
            self.id,
            self.position.x-self.radius, self.position.y-self.radius,
            self.position.x+self.radius, self.position.y+self.radius
        )
        
        
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
    
    for b in objects:
        b.move()
    
    for p in players:
        p.move()
        for i in history: #temp Fix. Pls remake to not be retard
            p.inputHandler(i)

      
    for i in range(1, len(objects)):
        objects[0].collide_with(objects[i])

    root.after(16, tick)


root = tk.Tk()
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="darkgreen")
canvas.pack()

objects = [
    Ball(canvas, Vector(WIDTH/2, HEIGHT/2), 10, "white"),
]

players = [
    Player(canvas, Vector(200, 400), 20, "green")
]

tick()
root.mainloop()
