from tkinter import *

root = Tk()
root.title("Moving with arrows")
root.geometry("800x600")

# Set canvas size
w = 600
h = 400
x = w // 2
y = h // 2

my_canvas = Canvas(root, width=w, height=h, bg="white")
my_canvas.pack(pady=20)

# Create a circle
my_circle = my_canvas.create_oval(x, y, x + 10, y + 10)

# Define movement functions
def left(event):
    x = -10
    y = 0
    my_canvas.move(my_circle, x, y)

def right(event):
    x = 10
    y = 0
    my_canvas.move(my_circle, x, y)

def up(event):
    x = 0
    y = -10
    my_canvas.move(my_circle, x, y)

def down(event):
    x = 0
    y = 10
    my_canvas.move(my_circle, x, y)

# General key press function
def pressing(event):
    x =0
    y =0
    if event.char == "a": x = -10
    if event.char == "d": x = 10
    if event.char == "w": y = -10
    if event.char == "s": y = 10
    my_canvas.move(my_circle, x, y)

root.bind("<Key>", pressing)

# Bind arrow keys
root.bind("<Left>", left)
root.bind("<Right>", right)
root.bind("<Up>", up)
root.bind("<Down>", down)

root.mainloop()

