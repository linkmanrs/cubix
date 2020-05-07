import threading

def x(y, r):
    print(y)
    print(r)

e = threading.Thread(target=x, args=(88, 2))
e.start()