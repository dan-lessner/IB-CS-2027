#skibidi pingus
import math

#hardcoded for now cuz im too lazy to do it rn :3 

def listSplit(list, element,offset : int):
    #print("--------------------------------")
    maxIndex = len(list) -1 
    #print("element: " + str(element))
    #print("maxIndex: " + str(maxIndex))
    pivotIndex = math.floor(maxIndex/2)
    #print("pivotIndex: " + str(pivotIndex))
    #print("List!: " + str(list))
    #print("offset!: " + str(offset))
    
    if maxIndex < 2:
        if element == list[maxIndex]:
            #print("maxEscape!: " + str(maxIndex + offset +1))
            return maxIndex + offset + 1
        else:
            #print("max2Escape!: " + str(offset + 1 ))
            return offset +1 
    
    if element > list[pivotIndex]:
        #print("bigger: " + str(list[pivotIndex + 1: ]))
        listSplit(list[pivotIndex + 1: ], element, offset + pivotIndex + 1)
    elif element < list[pivotIndex]:
        #print("smaller: " + str(list[: pivotIndex ]))
        listSplit(list[: pivotIndex ], element, offset)
    elif element == list[pivotIndex]:
        #print("elementEscape!: " + str(pivotIndex + offset + 1))
        return pivotIndex
    else:
        print("Can a loc come up in yo crib? Nah man, fuck you I see you at work!... aww fella dont hate me cuz im beautiful fella. Maybe if you got rid of that yee-yee ass haircut, you'd get some bitches on your dick. b=Better yet, maybe tanisha fine ass would stop fuckin' with that lawyer or surgeon she fuckin' with.... Fella!....... WHAT?")


list = [1,2,3,4,5,6,7]

listSplit(list, 2, -1)
        