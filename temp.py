n = 0


def func(inp):
    global n

    n += 1

    if inp == 1:
        return 1

    result = 0
    for i in range(inp):
        n += 1
        result += result + func(inp - 1)

    return result


def fac(n):
    if n == 0:
        return 1
    return n * fac(n-1)


for i in range(1, 15):
    n = 0
    func(i)
    print(f'{i}\t{n}')  # \ti!*i: {fac(i)*i//2}')
