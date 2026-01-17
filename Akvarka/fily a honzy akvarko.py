import tkinter as tk
import random
import math

WIDTH, HEIGHT = 2560, 1664
DT = 1

class Fish:
    def __init__(self, x, y, angle, speed, Fishy_images ):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.vx = 0
        self.vy = 0
        self.image = random.choice(Fishy_images)

    def move(self):
        self.x += self.vx * DT
        self.y += self.vy * DT

        # Wall collisions (Mantinels) using the actual window size
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

        self.vx *= FRICTION
        self.vy *= FRICTION

        if abs(self.vx) < 0.05: self.vx = 0
        if abs(self.vy) < 0.05: self.vy = 0

        self.canvas.coords(self.id, self.x-R, self.y-R, self.x+R, self.y+R)

root = tk.Tk()
root.title("Akvarka Fily a Honzy")
canvas = tk.Canvas(root, bg="white", highlightthickness=0)
canvas.pack(fill="both", expand=True)

canvas.create_rectangle(400, 400, 1200, 900 , fill="lightblue", outline="black")


def tick():
    for b in Fishes[:]:
        b.move()

    for i in range(len(Fishes)):
        for j in range(i+1, len(Fishes)):
            Fishes[i].collide_with(Fishes[j])


    root.after(16, tick)

Fishy_images = []

Fishes = []

tick()
root.mainloop()