import tkinter as tk
import random

WIDTH, HEIGHT = 600, 400
FISH_SPEED = 3

root = tk.Tk()
root.title("My Aquarium")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="light blue")
canvas.pack()

colors = ["orange", "yellow", "pink", "green", "violet"]

# místo slovníků: paralelní seznamy (index i = i-tá ryba)
fish_x = []
fish_y = []
fish_vx = []
fish_vy = []
fish_parts = []   # fish_parts[i] = [body_id, tail_id]

def create_fish(x, y, color):
    body = canvas.create_oval(
        x - 25, y - 12,
        x + 25, y + 12,
        fill=color, outline=""
    )

    tail = canvas.create_polygon(
        x + 25, y,
        x + 40, y - 12,
        x + 40, y + 12,
        fill=color, outline=""
    )

    return [body, tail]

# vytvoření rybiček
for color in colors:
    x = random.randint(50, WIDTH - 100)
    y = random.randint(50, HEIGHT - 50)

    fish_x.append(x)
    fish_y.append(y)
    fish_vx.append(random.choice([-FISH_SPEED, FISH_SPEED]))
    fish_vy.append(random.choice([-FISH_SPEED, FISH_SPEED]))
    fish_parts.append(create_fish(x, y, color))

def animate():
    for i in range(len(fish_x)):
        fish_x[i] += fish_vx[i]
        fish_y[i] += fish_vy[i]

        # odraz od levé a pravé zdi
        if fish_x[i] <= 25 or fish_x[i] >= WIDTH - 25:
            fish_vx[i] *= -1

        # odraz od horní a dolní zdi
        if fish_y[i] <= 12 or fish_y[i] >= HEIGHT - 12:
            fish_vy[i] *= -1

        # pohyb celé ryby
        for part in fish_parts[i]:
            canvas.move(part, fish_vx[i], fish_vy[i])

    root.after(30, animate)

animate()
root.mainloop()
