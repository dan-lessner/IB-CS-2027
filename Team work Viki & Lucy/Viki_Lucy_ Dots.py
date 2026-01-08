# loteryy
import tkinter as tk  # drawing of da balls
import random
import math

# nudaaaaaaaaaa
WIDTH = 700
HEIGHT = 450
BALL_RADIUS = 18
BALL_SPEED = 4
NUMBER_OF_BALLS = 10


# what a ball is - ddescription
class Ball:
    def __init__(self, canvas, number, color):  # _init_ fachá automaticky, když míček tohle 
        self.canvas = canvas
        self.number = number
        self.color = color

        # random start position
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        # x = left/right
        # y = up/down

        # random direction
        self.dx = random.choice([-BALL_SPEED, BALL_SPEED])
        self.dy = random.choice([-BALL_SPEED, BALL_SPEED])

        self.alive = True
        # if alive is false, then the ball will disappear and štop

        # draw ball
        self.circle = canvas.create_oval(
            self.x - BALL_RADIUS, self.y - BALL_RADIUS,
            self.x + BALL_RADIUS, self.y + BALL_RADIUS,
            fill=color
        )

        # number on ball
        self.text = canvas.create_text(
            self.x, self.y,
            text=str(number),
            fill="white",
            font=("Arial", 11, "bold")
        )

    def move(self):  # how ball mmoves
        if not self.alive:
            return

        # move ball
        self.x += self.dx
        self.y += self.dy    # position plus speed = moveee

        # bounce from walls
        if self.x <= BALL_RADIUS or self.x >= WIDTH - BALL_RADIUS:
            self.dx *= -1
        if self.y <= BALL_RADIUS or self.y >= HEIGHT - BALL_RADIUS:
            self.dy *= -1
            # what to do if the ball crashes into wall - change direction

        # update drawing, moves it to a dif. position
        self.canvas.coords(
            self.circle,
            self.x - BALL_RADIUS, self.y - BALL_RADIUS,
            self.x + BALL_RADIUS, self.y + BALL_RADIUS
        )
        self.canvas.coords(self.text, self.x, self.y)  # moves the drawing to the new placce

    def remove(self): # ball kapput
        self.alive = False
        self.canvas.delete(self.circle)
        self.canvas.delete(self.text)
       #  ball stos drawing, and then disappears

# game
def check_collisions(): # controll if two balls touched
    alive_balls = [b for b in balls if b.alive]  # ignore balls that are already puff

    for i in range(len(alive_balls)):  # this checks all the balls, to know which to boom
       # the i goes through indexes, i= 0
        for j in range(i + 1, len(alive_balls)):
             # it starts plus one, since we check every pair once/ no duplicates
            b1 = alive_balls[i]
            b2 = alive_balls[j]
            # double for loop, since we check doubles (one ball cannot collide with itself)
            # how far apart
            distance = math.hypot(b1.x - b2.x, b1.y - b2.y)
            
            if distance < BALL_RADIUS * 2:  # if the balls overlap then boom
                random.choice([b1, b2]).remove()
                return


def game_loop():  # never ending storyy
    alive_balls = [b for b in balls if b.alive]

    if len(alive_balls) == 1:  # if only one is left then game over
        winner = alive_balls[0]
        result = "Yipeee" if winner.number == guessed_number else "BOOOOO"
        # canva created something ehhh
        canvas.create_text(
            WIDTH // 2, HEIGHT // 2,
            text=f"Winner: Ball {winner.number}\n{result}",
            font=("Arial", 24, "bold"),
            fill="yellow"
        )
        return

    for ball in alive_balls:  # every ball moves every frame
        ball.move()

    check_collisions()
    root.after(16, game_loop)  # looop, 16 milisec, runs again


def start_game():  # start button, this starts when you press Start
    global guessed_number

    try:
        guessed_number = int(entry.get())  # the number what you typed
        if guessed_number < 1 or guessed_number > 10:
            raise ValueError
    except ValueError:
        status.config(text="Was ist deine numeroo 1–10", fg="red")
        return

    entry.config(state="disabled")
    start_button.config(state="disabled")
    status.config(text=f"You guessed ball {guessed_number}", fg="white")

    for i in range(NUMBER_OF_BALLS):
        color = random.choice(["red", "black"])
        balls.append(Ball(canvas, i + 1, color))  # creates 10 balls

    game_loop()


# window creation of life
root = tk.Tk() # creates the window
root.title("Balll gamble")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="pink")
canvas.pack()  # canvas

control = tk.Frame(root)
control.pack(pady=5)
# button und inputen
tk.Label(control, text="Winning ball (1–10):").pack(side="left")
entry = tk.Entry(control, width=5)
entry.pack(side="left")

start_button = tk.Button(control, text="Start", command=start_game)
start_button.pack(side="left", padx=5)

status = tk.Label(root, text="", fg="white")
status.pack()

balls = [ ]
guessed_number = None

root.mainloop()