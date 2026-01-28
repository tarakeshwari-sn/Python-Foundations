a = list(map(int, input("Enter numbers separated by space: ").split()))

res = list(filter(lambda num: num % 2 == 0, a))
print("Even Numbers are ",res)
