import tkinter as tk
import random

WIDTH, HEIGHT = 600, 400
FISH_SPEED = 3

root = tk.Tk()
root.title("My Aquarium")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="light blue")
canvas.pack()

# sand at the bottom
SAND_HEIGHT = 30
canvas.create_rectangle(
    0, HEIGHT - SAND_HEIGHT,
    WIDTH, HEIGHT,
    fill="#f2d7a1",
    outline=""
)

colors = [
    "orange", "yellow", "pink", "green", "violet",
    "navy", "lime", "red", "dark red", "dark red",
    "dark red", "dark red"
]

fish_list = []
bubble_list = []


# ---------- TŘÍDY ----------

class Fish:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.choice([-FISH_SPEED, FISH_SPEED])
        self.vy = random.choice([-FISH_SPEED, FISH_SPEED])
        self.parts = self.create_fish(color)

    def create_fish(self, color):
        body = canvas.create_oval(
            self.x - 25, self.y - 12,
            self.x + 25, self.y + 12,
            fill=color, outline=""
        )

        tail = canvas.create_polygon(
            self.x + 25, self.y,
            self.x + 40, self.y - 12,
            self.x + 40, self.y + 12,
            fill=color, outline=""
        )

        eye_white = canvas.create_oval(
            self.x - 15, self.y - 6,
            self.x - 7, self.y + 2,
            fill="white", outline=""
        )

        eye_black = canvas.create_oval(
            self.x - 12, self.y - 3,
            self.x - 9, self.y,
            fill="black", outline=""
        )

        return [body, tail, eye_white, eye_black]

    def move(self):
        self.x += self.vx
        self.y += self.vy

        # odraz od zdí
        if self.x <= 25 or self.x >= WIDTH - 25:
            self.vx *= -1

        if self.y <= 12 or self.y >= HEIGHT - 12:
            self.vy *= -1

        for part in self.parts:
            canvas.move(part, self.vx, self.vy)


class Bubble:
    def __init__(self):
        x = random.randint(20, WIDTH - 20)
        y = random.randint(HEIGHT - 40, HEIGHT)

        self.id = canvas.create_oval(
            x - 4, y - 4,
            x + 4, y + 4,
            fill="white",
            outline=""
        )

        self.speed = random.uniform(0.5, 1.5)

    def move(self):
        canvas.move(self.id, 0, -self.speed)

        x1, y1, x2, y2 = canvas.coords(self.id)
        if y2 < 0:
            new_x = random.randint(20, WIDTH - 20)
            new_y = HEIGHT
            canvas.coords(
                self.id,
                new_x - 4, new_y - 4,
                new_x + 4, new_y + 4
            )


# ---------- VYTVOŘENÍ OBJEKTŮ ----------

for color in colors:
    x = random.randint(50, WIDTH - 100)
    y = random.randint(50, HEIGHT - 50)
    fish_list.append(Fish(x, y, color))


# kytičky
def create_plant(x):
    stem_count = random.randint(3, 6)

    for i in range(stem_count):
        height = random.randint(50, 90)
        offset = random.randint(-10, 10)

        canvas.create_line(
            x + offset,
            HEIGHT,
            x + offset - random.randint(-15, 15),
            HEIGHT - height,
            smooth=True,
            width=3,
            fill="dark green"
        )

for x in range(30, WIDTH, 60):
    create_plant(x)


# bubliny
for i in range(20):
    bubble_list.append(Bubble())


# ---------- ANIMACE ----------

def animate():
    for fish in fish_list:
        fish.move()

    for bubble in bubble_list:
        bubble.move()

    root.after(30, animate)


animate()
root.mainloop()
