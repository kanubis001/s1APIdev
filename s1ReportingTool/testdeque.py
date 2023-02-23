from collections import deque

dq=deque()

def atesta():
    print("a")
    
def btesta():
    print("b")
    
dq[0]=atesta
dq.append(btesta)

dq.pop