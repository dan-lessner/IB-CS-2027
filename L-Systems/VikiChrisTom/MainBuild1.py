ruleDic = {"X":">[-FX]+FX"}
cmdDic = {"F":"turtle.fd(Distance/10)", "-":"turtle.left(Angle)","+":"turtle.right(Angle)","<":"Distance = Distance / distMult",">":"Distance = Distance * distMult","[":"storeState()", "]":"accessState()"}
Axiom = "FX"
current = Axiom
depth = 4
import turtle
Angle = 30
Distance = 1000  
distMult = 0.7
stateStack = []

width = 2000
height = 2000

turtle.tracer(1)
turtle.speed(1)
turtle.setup(width,height)
turtle.screensize(width*2,height*2)

class state:
    def __init__(self,heading,pos,length):
        self.heading = heading
        self.pos = pos
        self.length = length

def accessState():
    global Distance
    turtle.up()
    turtle.setheading(stateStack[-1].heading)
    turtle.setpos(stateStack[-1].pos)
    Distance = stateStack[-1].length
    stateStack.pop(-1)
    turtle.down()

def storeState():
    stateStack.append(state(turtle.heading(),turtle.pos(),Distance))

def processAxiom():
    global current 
    print(current)
    outputList = []
    for i in list(current):
        outputList.append(ruleDic.setdefault(i,i))
    current= ''.join(outputList)
    print(current)

for i in range(1,depth+1):
    processAxiom()
    print("This is depth " + str(i) + " ^^^" + "\n")

for i in current:
    exec(cmdDic.setdefault(i,''))

for i in range(1,len(stateStack)):
    print("heading " + str(i) + " " + str(stateStack[i].heading))
    print("pos " + str(i) + " " + str(stateStack[i].pos))
turtle.done()