import tkinter as tk
import random
import math

WIDTH, HEIGHT = 600, 400
R = 15
FRICTION = 0.995
DT = 1

class Ball:
    def __init__(self, canvas, x, y, color):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.id = canvas.create_oval(x-R, y-R, x+R, y+R, fill=color)
        canvas.tag_bind(self.id, "<Button-1>", self.hit)

    def hit(self, event):
        angle = random.random() * 2 * math.pi
        speed = random.uniform(6, 12)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

    def move(self):
        self.x += self.vx * DT
        self.y += self.vy * DT

        # odraz od mantinelů
        if self.x - R < 0:
            self.x = R
            self.vx = -self.vx
        elif self.x + R > WIDTH:
            self.x = WIDTH - R
            self.vx = -self.vx

        if self.y - R < 0:
            self.y = R
            self.vy = -self.vy
        elif self.y + R > HEIGHT:
            self.y = HEIGHT - R
            self.vy = -self.vy

        # tření
        self.vx *= FRICTION
        self.vy *= FRICTION

        # vykreslení
        self.canvas.coords(self.id, self.x-R, self.y-R, self.x+R, self.y+R)

    def collide_with(self, other):
        # vektor mezi středy
        dx = other.x - self.x
        dy = other.y - self.y
        dist = math.hypot(dx, dy)

        if dist == 0 or dist > 2*R:
            return

        # normalizace
        nx = dx / dist
        ny = dy / dist

        # projekce rychlosti do normály
        p1 = self.vx * nx + self.vy * ny
        p2 = other.vx * nx + other.vy * ny

        # výměna normálních složek (elastická srážka)
        self.vx += (p2 - p1) * nx
        self.vy += (p2 - p1) * ny
        other.vx += (p1 - p2) * nx
        other.vy += (p1 - p2) * ny

        # oddělení koulí, aby se neprolínaly
        overlap = 2*R - dist
        self.x -= nx * overlap/2
        self.y -= ny * overlap/2
        other.x += nx * overlap/2
        other.y += ny * overlap/2


def tick():
    # pohyb
    for b in balls:
        b.move()

    # kolize OOP style
    for i in range(len(balls)):
        for j in range(i+1, len(balls)):
            balls[i].collide_with(balls[j])

    root.after(16, tick)


root = tk.Tk()
c = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="darkgreen")
c.pack()

balls = [
    Ball(c, 150, 200, "white"),
    Ball(c, 250, 200, "red"),
    Ball(c, 350, 200, "yellow"),
    Ball(c, 450, 200, "blue"),
]

tick()
root.mainloop()