# GLOBAL "school noticeboard"
announcements = ["School starts at 8:00"]     # global variable

def ring_bell():                             # global function
    print("Bell rings!")

def class_period(student):
    # LOCAL "student notebook" (exists only during this class_period call)
    announcements = [f"{student}: bring calculator"]   # local variable (shadows global)
    
    def ring_bell():                         # local function (shadows global)
        print(f"{student}'s timer beeps (not the whole school)")

    print("Inside class_period:")
    print("  local announcements:", announcements)
    ring_bell()

print("Before class_period:")
print("  global announcements:", announcements)
ring_bell()

class_period("Ema")

print("After class_period:")
print("  global announcements:", announcements)
ring_bell()
