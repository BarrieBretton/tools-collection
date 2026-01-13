import time
from multiprocessing import Process

def f(name):
    i = 0
    while(i<10):
        print(f"f({name}): {i}")
        i+=1

def g(name):
    i = 0
    while(i<10):
        print(f"g(@{name.upper()}): {i}")
        i+=1

if __name__ == "__main__":
    p1 = Process(target = f, args=('bob', ))
    p2 = Process(target = g, args=('bob', ))
    
    p1.start()
    p2.start()



