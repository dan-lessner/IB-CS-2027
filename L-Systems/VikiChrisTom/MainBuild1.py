import turtle
cmdDic = {"F":"turtle.fd(Distance/10)", "-":"turtle.left(Angle)","+":"turtle.right(Angle)","<":"Distance = Distance / distMult",">":"Distance = Distance * distMult","[":"storeState()", "]":"accessState()"}

storeInput = input('Want to change save? Y/N ')
while True:
    if  storeInput== 'Y':
        file = open("/Users/evastumpfova/Documents/GitHub/IB-CS-2027/L-Systems/VikiChrisTom/DataDump.txt","w")
        file.write(input("Depth: ") + "\n ")
        file.write(input("Angle: ") + "\n ")
        file.write(input("Distance: ") + "\n ")
        file.write(input("DistMult: ") + "\n ")
        file.write(input("Axiom: ") + "\n ")
        while True:
            if input("New Rule? Y/N: ") == "Y":
                file.write(input("Name: ") + "\n ")
                file.write(input("Rule: ") + "\n ")
            else:
                break
        print("finished!!!!")
        file.close()
    elif storeInput == 'N':
        print("continuing")
    else:
        print("wrong input, but fuck it we ball! :)")
    file = open("/Users/evastumpfova/Documents/GitHub/IB-CS-2027/L-Systems/VikiChrisTom/DataDump.txt","r")
    content = file.read()
    print(content)
    file.seek(0)
    print(file.readlines())
    file.close()

    with open("L-Systems/VikiChrisTom/DataDump.txt","r") as file:
        lines = file.readlines()
        
    for i in range(len(lines)):
        lines[i] = lines[i].strip()
            
    lines.pop(-1)

    print(lines)

    ruleDic = {}

    try:
        depth = int(lines[0])
        Angle = int(lines[1])
        Distance = int(lines[2]) 
        distMult = float(lines[3])  
        Axiom = lines[4]
        for i in range(0,int((len(lines)-5)/2),2):
            
            ruleDic.update({lines[i-2]:lines[i-1]})
        break
    except TypeError:
        print("Wrong save, wtf are you doing? \n please try again lmaoooo!")
        
current = Axiom

print(ruleDic)


stateStack = []

width = 5000
height = 5000
turtle.tracer(1)
turtle.speed(100)
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