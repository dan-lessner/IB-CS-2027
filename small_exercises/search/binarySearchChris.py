#skibidi pingus
import math

#nefunguje, asi budu potrebovat rewrite
#hardcoded for now cuz im too lazy to do it rn :3, also ik ze ten offset index vec se da udelat lepe ale nebudu to menit protoze bych to stealoval od ernesta

def listSplit(list, element):
    print("--------------------------------")
    print("element: " + str(element))
    print("maxIndex: " + str(len(list)-1))
    pivotIndex = math.floor((len(list)-1)/2)
    print("pivotIndex: " + str(pivotIndex))
    print("List!: " + str(list))
    
    if list == []:
        print("TS EMPTY!")
        return None
    if len(list) == 2:
        if element == list[0]:
            return 0
        elif element == list[1]:
            return 1
        else:
            return -1
    
    indx = 0
    
    if element > list[pivotIndex]:
        print("bigger: " + str(list[pivotIndex: ]))
        indx =listSplit(list[pivotIndex: ], element)
        if indx == -1:
            return -1
        indx += pivotIndex
        
    elif element < list[pivotIndex]:
        print("smaller: " + str(list[: pivotIndex ]))
        indx = listSplit(list[: pivotIndex ], element)
        if indx == -1:
            return -1
        
    elif element == list[pivotIndex]:
        print("Escape!: " + str(pivotIndex))
        indx = pivotIndex
    else:
        print("Can a loc come up in yo crib? Nah man, fuck you I see you at work!... aww fella dont hate me cuz im beautiful fella. Maybe if you got rid of that yee-yee ass haircut, you'd get some bitches on your dick. Better yet, maybe tanisha dog ass would stop fuckin' with that lawyer or surgeon she fuckin' wit' .... Fella!....... WHAT?")
    print("indx: " + str(indx))
    return indx 

list = [1,2,3,4,5,6,7,8,9,10,11]



print(listSplit(list, int(input(" on foenem grave what number you wanna check?: "))))
        