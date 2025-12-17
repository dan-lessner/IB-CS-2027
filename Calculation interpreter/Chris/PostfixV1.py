inputString = ["2","7","4","1","-","+","-","2","10","-","-","5","3","2","*","+","/"]
operationList = ["+","-","*","/"]
stack = []

for i in inputString:
    if i in operationList:
        temp1 = ''.join([stack[-2],i,stack[-1]])
        stack = stack[0:-2]
        print(eval(temp1))
        stack.append(str(eval(temp1)))
    else:
        stack.append(i)
print (stack)
    