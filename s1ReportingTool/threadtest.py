from threading import *
import time


def producer():
    time.sleep(3)
    print("Producer thread producing items:")
    print("Producer thread notification")
    time.sleep(3)
    event.set()


def consumer():
    print("Consumer thread waiting")
    event.wait()
    print("Consumer thread consuming items")


event = Event()
t1 = Thread(target=producer)
t2 = Thread(target=consumer)
t1.start()
t2.start()
