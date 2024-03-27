my_dict = {}
n = int(input())
for _ in range(n):
    k, v = input().split(' ')
    my_dict[k] = v
x = input()
print(my_dict[x])
