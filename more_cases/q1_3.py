x = 1
def add1(x):
    x = x+1
def add2(y):
    add1(y)
def add3(y):
    add2(y)
def add4(x):
    add3(x)
def add5(x):
    add4(x)
def add6(x):
    add5(x)
def add7(x):
    add6(x)
add7(x)