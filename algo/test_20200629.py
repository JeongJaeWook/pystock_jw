#List, Dick 팁!
ddd = [1,2,3,4,5]

s1 = ddd
s2 = ddd

print("s1 %s" %s1)
print("s2 %s" %s2)

del s1[0]

print("s1 %s" %s1)
print("s2 %s" %s2)

#같은 주소값을 공유하기 때문에 동시에 적용이 된다!!