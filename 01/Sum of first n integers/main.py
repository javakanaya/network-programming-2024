n = int(input())
if n >= 0:
    sum_of_n = (n * (n + 1)) // 2
else:
    sum_of_n = (-n * (-n + 1)) // 2
    sum_of_n *= -1
print(sum_of_n)
