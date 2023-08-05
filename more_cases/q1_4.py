x = 1
def add3(x):
    add1(x)

def add2(x):
    x = x - 7

def add1(x):
    x = x+1

add3(x)

def add1(x):
    x = 7
    add2(x)

def add2(x):
    x = x - 5

add3(x)