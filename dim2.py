from monitors import MonitorInt, MonitorExt
from queue import Jobs
import threading
import time

class Dimmer():
    def __init__(self):
        self.title='Control Brightness'
        self.monitors = []




a = MonitorInt()
a.read_actual_brightness()

b = MonitorExt()
b.read_actual_brightness()
print("##")
# for i in range(10):
#     a.on_set(1200 + i)

# print("##")
# for i in range(2):
#     b.on_set(50 + i)

# a.on_set(1200)

class Worker:
    def __init__(self, monitor, queue):
        self.monitor = monitor
        self.queue = queue
        self.is_alive = False
        self.thread = None

    def worker(self):
        while True: 
            value = self.queue.get()
            if value is None:
                break
            self.monitor.on_set(value)
            print(f"\tset {value} to {self.monitor.type}")

    
    def put_and_run(self, value):
        self.queue.put(value)

        if not self.thread or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.worker, args=())
            self.thread.start()
            print(f"created new thread for {value}")
        # else:
            # print(f"Add {value} to the existing one")



q = Jobs(1)
int = Worker(b, q)
for i in range(10):
    int.put_and_run(10 * i)
    time.sleep(2)

int.thread.join()




# def worker(a, q):
#     while True: 
#         value = q.get()
#         if value is None:
#             break
#         a.on_set(value)
#         print(f"set {value} to {a.type}")


# q = Jobs(1)
# for i in range(10):
#     q.put(i*10)

# t = threading.Thread(target=worker, args=(b, q))
# t.start()

# for i in range(100):
#     time.sleep(2)
#     print(f"add {i}")
#     q.put(i)

# for i in range(1188):
#     q.put(120000-i*100)