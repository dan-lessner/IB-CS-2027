import tkinter as tk
import random
import math

WIDTH, HEIGHT = 2560, 1664
R = 20
FRICTION = 0.985
DT = 1

<<<<<<< HEAD
POCKET_R = 65
POCKETS = [
    (0, 0),
    (WIDTH, 0),
    (0, HEIGHT),
    (WIDTH, HEIGHT),
    (1470, 0),
    (WIDTH, 0),
    (0, HEIGHT),
    (WIDTH, HEIGHT),
    (0, 830),
    (WIDTH, 0),
    (0, HEIGHT),
    (WIDTH, HEIGHT),
    (1470, 830),
    (WIDTH, 0),
    (0, HEIGHT),
    (WIDTH, HEIGHT)
]

class Ball:
    def __init__(self, canvas, x, y, color):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
=======
class Snake:
    def __init__(self, canvas):
        self.canvas = canvas
        self.direction = "Right"
        self.body = [(10, 10), (9, 10), (8, 10)]  # grid positions
        self.squares = []
>>>>>>> 3641ebd4c50856f16b9c25c28514b823762e347f

        self.is_aiming = False
        self.aim_line = None

        self.id = canvas.create_oval(
            x-R, y-R, x+R, y+R, fill=color, outline="black"
        )

        canvas.tag_bind(self.id, "<Button-1>", self.start_aim)
        canvas.tag_bind(self.id, "<B1-Motion>", self.update_aim)
        canvas.tag_bind(self.id, "<ButtonRelease-1>", self.shoot)

    
    def start_aim(self, event):
        self.is_aiming = True
        if self.aim_line:
            self.canvas.delete(self.aim_line)
            self.aim_line = None

    def update_aim(self, event):
        if not self.is_aiming:
            return

        if self.aim_line:
            self.canvas.delete(self.aim_line)

        self.aim_line = self.canvas.create_line(
            self.x, self.y, event.x, event.y,
            fill="white", width=2
        )

    def shoot(self, event):
        if not self.is_aiming:
            return

        dx = self.x - event.x
        dy = self.y - event.y

        distance = math.hypot(dx, dy)
        max_power = 20
        power = min(distance / 10, max_power)

        angle = math.atan2(dy, dx)

        self.vx = math.cos(angle) * power
        self.vy = math.sin(angle) * power

        self.is_aiming = False

        if self.aim_line:
            self.canvas.delete(self.aim_line)
            self.aim_line = None

   
    def move(self):
        self.x += self.vx * DT
        self.y += self.vy * DT

<<<<<<< HEAD
        # Wall collisions
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

        # Friction
        self.vx *= FRICTION
        self.vy *= FRICTION

        # Stop tiny motion
        if abs(self.vx) < 0.05:
            self.vx = 0
        if abs(self.vy) < 0.05:
            self.vy = 0

        self.canvas.coords(
            self.id,
            self.x-R, self.y-R,
            self.x+R, self.y+R
        )

        self.check_pocket()

 
    def check_pocket(self):
        for px, py in POCKETS:
            if math.hypot(self.x - px, self.y - py) < POCKET_R - R/2:
                self.canvas.delete(self.id)
                if self in balls:
                    balls.remove(self)
                return


    def collide_with(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        dist = math.hypot(dx, dy)

        if dist == 0 or dist > 2*R:
            return

        nx = dx / dist
        ny = dy / dist

        p1 = self.vx * nx + self.vy * ny
        p2 = other.vx * nx + other.vy * ny

        self.vx += (p2 - p1) * nx
        self.vy += (p2 - p1) * ny
        other.vx += (p1 - p2) * nx
        other.vy += (p1 - p2) * ny

        overlap = 2*R - dist
        self.x -= nx * overlap / 2
        self.y -= ny * overlap / 2
        other.x += nx * overlap / 2
        other.y += ny * overlap / 2



def tick():
    for b in balls[:]:
        b.move()

    for i in range(len(balls)):
        for j in range(i+1, len(balls)):
            balls[i].collide_with(balls[j])
=======
    
    def collide_with(self, other):
    

    # kolize OOP style
        for i in range(len(snakes)):
            for j in range(i+1, len(snakes)):
                snakes[i].collide_with(snakes[j])
>>>>>>> 3641ebd4c50856f16b9c25c28514b823762e347f

    root.after(16, tick)



<<<<<<< HEAD
root = tk.Tk()
root.title("Pool Game")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="darkgreen")
canvas.pack()

# Draw pockets
for px, py in POCKETS:
    canvas.create_oval(
        px-POCKET_R, py-POCKET_R,
        px+POCKET_R, py+POCKET_R,
        fill="black"
    )

# Balls
balls = [
    Ball(canvas, 280, 328, "white"),
    Ball(canvas, 920, 320, "black"),
    Ball(canvas, 960, 330, "purple"),
    Ball(canvas, 960, 320, "darkred"),
    Ball(canvas, 960, 310, "lightblue"),
    Ball(canvas, 1000, 296, "green"),
    Ball(canvas, 1000, 346, "red"),
    Ball(canvas, 1000, 336, "yellow"),
    Ball(canvas, 1000, 316, "blue"),
=======
snakes = [
    Snake(c),
    Snake(c),
    Snake(c),
    Snake(c),
>>>>>>> 3641ebd4c50856f16b9c25c28514b823762e347f
]

tick()
root.mainloop()
