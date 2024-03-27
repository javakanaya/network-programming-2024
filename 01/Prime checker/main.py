def sieve_of_eratosthenes(n):
    primes = [True] * (n+1)
    primes[0] = primes[1] = False  # 0 and 1 are not primes

    p = 2
    while (p * p <= n):

        if primes[p] == True:
            for i in range(p * p, n+1, p):
                primes[i] = False
        p += 1

    return primes


def is_prime(n):
    if n <= 1:
        return False
    return sieve[n]


number = int(input())
sieve = sieve_of_eratosthenes(number)
if (is_prime(number)):
    print("Prime")
else:
    print("Not prime")
