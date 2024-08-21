import time

class Jobs:
    def __init__(self, n=0):
        self.queue = []
        self.n = n
        self.pending = False
    
    def __repr__(self):
        return f"Maximum Jobs= {self.n}| n queue= {self.n_queue()} | {self.queue}"
    
    def n_queue(self):
        return len(self.queue)
    
    def update_pending(self):
        self.pending = False if self.n_queue() == 0 else True
    
    def put(self, job):
        if not self.pending:
            self.pending = True
        if self.n_queue() < self.n or self.n_queue() == 0 or self.n == 0:
            self.queue.append(job)
        else:
            self.queue = self.queue[1::]
            self.queue.append(job)
        self.update_pending()
    
    def get(self, timeout=0):
        def get_timeout(timeout=0):
            start_time = time.time()

            while time.time() - start_time <= timeout:
                if self.queue:
                    break


        if self.n_queue() == 0 and timeout != 0:
            get_timeout(timeout)

        if self.n_queue():
            # print(self.n_queue())
            job = self.queue.pop()
            self.update_pending()
            return job
    
    def show(self):
        print(self.queue)
    