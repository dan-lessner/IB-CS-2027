import tkinter as tk
import random as rand

canv_width = 1000
canv_height = 600
dt = 0.1
friction = 0.04

class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

class Ball:
    def __init__(self, vec_pos, rad, canv, color):
        self.pos = vec_pos
        self.canvas = canv
        self.radius = rad
        self.velocity = Vector(rand.uniform(0, 20), rand.uniform(0, 20))
        self.id = canv.create_oval(self.pos.x-rad, self.pos.y-rad, self.pos.x+rad, self.pos.y+rad, fill=color)
        canv.tag_bind(self.id, "<Button-1>", self.pum)

    def pum(self):
        self.velocity = Vector(rand.uniform(20, 100), rand.uniform(20, 100))

    def move(self):
        self.pos += self.velocity*dt

        if (self.pos.x - self.radius < 0) or (self.pos.x + self.radius > canv_width):
            self.velocity.x = -self.velocity.x
            self.pos.x = 1 #???


root = tk.Tk()
canvas = tk.Canvas(root, width=canv_width, height=canv_height, bg="darkgreen")
canvas.pack()

root.mainloop()