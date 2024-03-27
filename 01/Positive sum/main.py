n = int(input())
sum = 0
for _ in range(n):
    ni = int(input())
    if ni < 0:
        continue
    else:
        sum += ni

print(sum)
