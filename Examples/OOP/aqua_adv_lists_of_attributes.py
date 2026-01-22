import tkinter as tk
import random
import math

WIDTH, HEIGHT = 600, 400
FISH_SPEED = 3
FOOD_SPEED = 2

MIN_FISH_DISTANCE = 50
REPULSION_STRENGTH = 0.5
FOOD_ATTRACTION = 0.3

root = tk.Tk()
root.title("My Aquarium")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="light blue")
canvas.pack()

# písek dole
SAND_HEIGHT = 30
canvas.create_rectangle(
    0, HEIGHT - SAND_HEIGHT,
    WIDTH, HEIGHT,
    fill="#f2d7a1",
    outline=""
)

colors = ["orange", "yellow", "pink", "green", "violet", "navy", "lime", "red", "dark red"]

# místo slovníků: paralelní seznamy (index i = i-tá ryba)
fish_x = []
fish_y = []
fish_vx = []
fish_vy = []
fish_parts = []   # fish_parts[i] = [body, tail, eye_white, eye_black]

# bubliny: paralelní seznamy
bubble_id = []
bubble_speed = []

# jídlo: paralelní seznamy
food_id = []
food_x = []
food_y = []

def create_fish(x, y, color):
    body = canvas.create_oval(x - 25, y - 12, x + 25, y + 12, fill=color, outline="")
    tail = canvas.create_polygon(x + 25, y, x + 40, y - 12, x + 40, y + 12, fill=color, outline="")
    eye_white = canvas.create_oval(x - 15, y - 6, x - 7, y + 2, fill="white", outline="")
    eye_black = canvas.create_oval(x - 12, y - 3, x - 9, y, fill="black", outline="")
    return [body, tail, eye_white, eye_black]

# vytvoření rybiček
for color in colors:
    x = random.randint(50, WIDTH - 100)
    y = random.randint(50, HEIGHT - 50)

    fish_x.append(x)
    fish_y.append(y)
    fish_vx.append(random.uniform(-1, 1))
    fish_vy.append(random.uniform(-1, 1))
    fish_parts.append(create_fish(x, y, color))

# kytičky
def create_plant(x):
    for _ in range(random.randint(3, 6)):
        height = random.randint(50, 90)
        offset = random.randint(-10, 10)
        canvas.create_line(
            x + offset, HEIGHT,
            x + offset - random.randint(-15, 15), HEIGHT - height,
            smooth=True, width=3, fill="dark green"
        )

for x in range(30, WIDTH, 60):
    create_plant(x)

# bublinky
for _ in range(20):
    x = random.randint(20, WIDTH - 20)
    y = random.randint(HEIGHT - 40, HEIGHT)
    bid = canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="white", outline="")
    bubble_id.append(bid)
    bubble_speed.append(random.uniform(0.5, 1.5))

# jídlo
def drop_food(event):
    x = random.randint(20, WIDTH - 20)
    y = 0
    fid = canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="brown", outline="")

    food_id.append(fid)
    food_x.append(x)
    food_y.append(y)

root.bind("<space>", drop_food)

def animate():
    # ryby
    for i in range(len(fish_x)):

        # separace ryb (vektorově)
        for j in range(len(fish_x)):
            if j == i:
                continue

            dx = fish_x[i] - fish_x[j]
            dy = fish_y[i] - fish_y[j]
            dist = math.hypot(dx, dy)

            if 0 < dist < MIN_FISH_DISTANCE:
                fish_vx[i] += (dx / dist) * REPULSION_STRENGTH
                fish_vy[i] += (dy / dist) * REPULSION_STRENGTH

        # přitahování k jídlu (jen k prvnímu kousku)
        if food_id:
            dx = food_x[0] - fish_x[i]
            dy = food_y[0] - fish_y[i]
            dist = math.hypot(dx, dy)

            if dist != 0:
                fish_vx[i] += (dx / dist) * FOOD_ATTRACTION
                fish_vy[i] += (dy / dist) * FOOD_ATTRACTION

        # omezení rychlosti
        speed = math.hypot(fish_vx[i], fish_vy[i])
        if speed > FISH_SPEED:
            fish_vx[i] = (fish_vx[i] / speed) * FISH_SPEED
            fish_vy[i] = (fish_vy[i] / speed) * FISH_SPEED

        fish_x[i] += fish_vx[i]
        fish_y[i] += fish_vy[i]

        if fish_x[i] <= 25 or fish_x[i] >= WIDTH - 25:
            fish_vx[i] *= -1
        if fish_y[i] <= 12 or fish_y[i] >= HEIGHT - 12:
            fish_vy[i] *= -1

        for part in fish_parts[i]:
            canvas.move(part, fish_vx[i], fish_vy[i])

    # bublinky
    for i in range(len(bubble_id)):
        canvas.move(bubble_id[i], 0, -bubble_speed[i])
        if canvas.coords(bubble_id[i])[3] < 0:
            x = random.randint(20, WIDTH - 20)
            canvas.coords(bubble_id[i], x - 4, HEIGHT - 4, x + 4, HEIGHT + 4)

    # jídlo
    k = 0
    while k < len(food_id):
        food_y[k] += FOOD_SPEED
        canvas.move(food_id[k], 0, FOOD_SPEED)

        eaten = False
        for i in range(len(fish_x)):
            if math.hypot(food_x[k] - fish_x[i], food_y[k] - fish_y[i]) < 20:
                canvas.delete(food_id[k])

                food_id.pop(k)
                food_x.pop(k)
                food_y.pop(k)

                eaten = True
                break

        if eaten:
            continue

        if food_y[k] > HEIGHT - SAND_HEIGHT:
            canvas.delete(food_id[k])

            food_id.pop(k)
            food_x.pop(k)
            food_y.pop(k)
            continue

        k += 1

    root.after(30, animate)

animate()
root.mainloop()
