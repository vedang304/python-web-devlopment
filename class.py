for i in range(1,5,2):
    print (i,end=" for i in")
for i in range(10,0,-1):
    print(i,end=" ")
fruits =["apple","mango","banana"]
total = 0
prices=[30,20,80,40]
for fruit, price in zip(fruits,prices):
    total+=price
    print(fruit ,": Rs.",price)
print("total: Rs,",total)    