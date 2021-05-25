from functools import reduce

def test(a,b):
  print(a,b)
  return a+b

reduce(test, [ 1 , 3, 5, 6, 2, ])

print(sum([ 1 , 3, 5, 6, 2, ]))