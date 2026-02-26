#sets with lists
# big picture, number list manager, it converts list to a set and then it compares the lenght to find duplicates

# function to check duplicates
def has_duplicates(lst):  #list is a parameter
    if len(lst) != len(set(lst)):  #lenght of(our list) =  coverst list to sets , ! not equal
        return True
    return False
#basicly if the lenght is not equal  - oh no duplicates

# function to remove duplicates
def remove_duplicates(lst):
    return list(set(lst))  # remove duplicate - convert back to list


# function to add 
def add_number(lst, number):
    if number not in lst: #check
        lst.append(number) # add to the end of the list
    else:  # if false 
        print("here")


# function to delete 
def delete_number(lst, number):
    if number in lst: #check
        lst.remove(number)
    else:
        print("Number not here anymore")


# the input part

numbers = [] #creation of empty list

# Enter #
user_input = input("Whole # : ")

# ehmm a bit confusing
numbers = map(int, user_input.split())
#user_input.split() - this will break the text into pieces, so the numbers will be strings
# it ill apply the functions map(int - this converts text to number,) = so it willl be [1,2]
#converts it all to a list


print("Your list:", numbers)


# options loop

while True: #infinity stones
    print("\nChoose an option:") #\n new line
    print("1 - Check duplicates")
    print("2 - Remove duplicates")
    print("3 - Add ")
    print("4 - Delete")
    print("5 - Show list")
    print("6 - Exit")

    choice = input("Your choice: ") # stores it all

 # menu decision
    if choice == "1":  # the double == means equal to
        print("Duplicates?", has_duplicates(numbers))

    elif choice == "2":
        numbers = remove_duplicates(numbers)
        print("Duplicates removed.")

    elif choice == "3":
        num = int(input("add: "))
        add_number(numbers, num)

    elif choice == "4":
        num = int(input("delete: "))
        delete_number(numbers, num)

    elif choice == "5":
        print("Current list:", numbers)

    elif choice == "6":
        print("Exit")
        break  # stop

    else: # if any other number
        print("Wrong")

# vylepšení
# make it more efficient - so for the program to sortt the numbers based on those who are the most common to ask