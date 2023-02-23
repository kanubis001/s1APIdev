def a(c):
    def b():
        print("a")
        c()
    return b
    
@a
def aa():
    print("b")
    
aa()