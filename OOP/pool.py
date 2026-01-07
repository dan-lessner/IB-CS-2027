import tkinter as tk
import random
import math

WIDTH, HEIGHT = 600, 400
R = 5
FRICTION = 0.9
DT = 1

class Snake:
    def __init__(self, canvas):
        self.canvas = canvas
        self.direction = "Right"
        self.body = [(10, 10), (9, 10), (8, 10)]  # grid positions
        self.squares = []

    def hit(self, event):
        angle = random.random() * 2 * math.pi
        speed = random.uniform(6, 12)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

    def move(self):
        self.x += self.vx * DT
        self.y += self.vy * DT

    
    def collide_with(self, other):
    

    # kolize OOP style
        for i in range(len(snakes)):
            for j in range(i+1, len(snakes)):
                snakes[i].collide_with(snakes[j])

    root.after(16, tick)


root = tk.Tk()
c = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="darkgreen")
c.pack()

snakes = [
    Snake(c),
    Snake(c),
    Snake(c),
    Snake(c),
]

tick()
root.mainloop()
