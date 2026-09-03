import random
def radixSort(arr):
    maxOrder = len(str(max(arr)))
    for u in range(maxOrder):
        print("u -> " + str(u))
        
        try:
            bucketsOld = buckets
        except:
            bucketsOld = []
            bucketsOld = [[] for _ in range(10)]
            bucketsOld[0].extend(arr)
        print("buckets Old:" + str(bucketsOld))
        
        buckets = [[] for _ in range(10)]
        
        for rlist in bucketsOld:
            print("rlist Len -> " + str(len(rlist)))
            print("rlist -> " + str(rlist))
            if len(rlist) != 0:
                for e in rlist:
                    digit = (e // (10 ** u)) % 10
                    buckets[digit].append(e)
                    print("e -> " + str(e) + " pos -> " + str(digit))

                    
    return sum(buckets,[])
    
tList = [random.randint(0,1000) for _ in range(20)]
print(tList)


    
print(radixSort(tList))
        
        

            