def a():
    pass
def z():
    z = 0
a()
def b():
    pass
def a():
    z()
    b()
def z():
    z = 1   
a()
def a():
    pass
def b():
    z()
    a()
def z():
    z = 2
b()
def z():
    z = 3
def b():
    pass
def a():
    b()
a()
