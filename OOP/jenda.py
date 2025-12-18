import tkinter as tk
import random
import math

WIDTH, HEIGHT = 600, 400
R = 15
FRICTION = 0.02
DT = 1
K_COULOMB = 500.0
RESTITUTION = 0.85
TANGENTIAL_DAMP = 0.02
CLICK_STRENGTH = 200.0
CLICK_MAX = 100.0

class Ball:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.charge = random.choice([-1, 1])
        self.id = canvas.create_oval(x-R, y-R, x+R, y+R, fill="red" if self.charge > 0 else "blue", outline="black")
        self.text_id = canvas.create_text(x, y, text=("+" if self.charge > 0 else "-"), fill="white")
        canvas.tag_bind(self.id, "<Button-3>", self.toggle_charge)
        canvas.tag_bind(self.text_id, "<Button-3>", self.toggle_charge)

    def toggle_charge(self, _):
        self.charge *= -1
        self.canvas.itemconfig(self.id, fill="red" if self.charge > 0 else "blue")
        self.canvas.itemconfig(self.text_id, text=("+" if self.charge > 0 else "-"))

    def apply_click_impulse(self, cx, cy):
        dx = self.x - cx
        dy = self.y - cy
        dist = math.hypot(dx, dy)
        if dist == 0:
            angle = random.random() * 2 * math.pi
            nx = math.cos(angle)
            ny = math.sin(angle)
            mag = CLICK_MAX
        else:
            nx = dx / dist
            ny = dy / dist
            mag = CLICK_STRENGTH / (dist)
            if mag > CLICK_MAX:
                mag = CLICK_MAX

        self.vx += nx * mag
        self.vy += ny * mag

    def move(self):
        self.x += self.vx * DT
        self.y += self.vy * DT

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

        try:
            f = friction_var.get()
        except Exception:
            f = FRICTION
        self.vx *= (1-f)
        self.vy *= (1-f)

        self.canvas.coords(self.id, self.x-R, self.y-R, self.x+R, self.y+R)
        self.canvas.coords(self.text_id, self.x, self.y)

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

        try:
            rest = restitution_var.get()
        except Exception:
            rest = RESTITUTION
        rel = p1 - p2
        if rel > 0:
            j = -(1.0 + rest) * rel / 2.0
            self.vx += j * nx
            self.vy += j * ny
            other.vx -= j * nx
            other.vy -= j * ny

        tx = -ny
        ty = nx
        t1 = self.vx * tx + self.vy * ty
        t2 = other.vx * tx + other.vy * ty
        try:
            td = tangential_var.get()
        except Exception:
            td = TANGENTIAL_DAMP
        t1_new = t1 * (1.0 - td)
        t2_new = t2 * (1.0 - td)
        self.vx += (t1_new - t1) * tx
        self.vy += (t1_new - t1) * ty
        other.vx += (t2_new - t2) * tx
        other.vy += (t2_new - t2) * ty

        overlap = 2*R - dist
        self.x -= nx * overlap/2
        self.y -= ny * overlap/2
        other.x += nx * overlap/2
        other.y += ny * overlap/2

    def apply_force_from(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)

        if dist == 0:
            return

        nx = dx / dist
        ny = dy / dist

        try:
            k = k_var.get()
        except Exception:
            k = K_COULOMB

        force = -k * (self.charge * other.charge) / pow(dist, 2)

        ax = force * nx
        ay = force * ny

        self.vx += ax * DT
        self.vy += ay * DT
        other.vx -= ax * DT
        other.vy -= ay * DT


def tick():
    for i in range(len(balls)):
        for j in range(i+1, len(balls)):
            balls[i].apply_force_from(balls[j])

    for b in balls:
        b.move()

    for i in range(len(balls)):
        for j in range(i+1, len(balls)):
            balls[i].collide_with(balls[j])

    root.after(16, tick)


root = tk.Tk()
c = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="darkgreen")
c.pack()


def on_canvas_click(event):
    for b in balls:
        b.apply_click_impulse(event.x, event.y)

c.bind("<Button-1>", on_canvas_click)


def spawn_ball():
    balls.append(Ball(c, WIDTH//2, HEIGHT//2))

def delete_ball():
    if not balls:
        return
    b = balls.pop()
    try:
        c.delete(b.id)
        c.delete(b.text_id)
    except Exception:
        pass

btn_frame = tk.Frame(root)
btn_frame.pack(fill="x")
spawn_btn = tk.Button(btn_frame, text="Spawn", command=spawn_ball)
spawn_btn.pack(side="left", padx=6, pady=6)
del_btn = tk.Button(btn_frame, text="Delete", command=delete_ball)
del_btn.pack(side="left", padx=6, pady=6)

controls_frame = tk.Frame(root)
controls_frame.pack(fill="x", pady=4)

k_var = tk.DoubleVar(value=K_COULOMB)
restitution_var = tk.DoubleVar(value=RESTITUTION)
friction_var = tk.DoubleVar(value=FRICTION)
tangential_var = tk.DoubleVar(value=TANGENTIAL_DAMP)

tk.Scale(controls_frame, label="Coulomb K", variable=k_var, from_=0, to=1000, resolution=10, orient="horizontal", length=240).pack(side="left", padx=6)
tk.Scale(controls_frame, label="Restitution", variable=restitution_var, from_=0.0, to=1.0, resolution=0.01, orient="horizontal", length=160).pack(side="left", padx=6)
tk.Scale(controls_frame, label="Tangential damp", variable=tangential_var, from_=0.0, to=0.05, resolution=0.001, orient="horizontal", length=160).pack(side="left", padx=6)
tk.Scale(controls_frame, label="Friction (drag)", variable=friction_var, from_=0.0, to=0.05, resolution=0.001, orient="horizontal", length=180).pack(side="left", padx=6)

balls = []
for _ in range(10):
    balls.append(Ball(c, random.randint(R, WIDTH-R), random.randint(R, HEIGHT-R)))

tick()
root.mainloop()
