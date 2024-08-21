import numpy as np
import time
import subprocess
from configs import config
import threading


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


class MonitorInt():
    def __init__(self, type='internal'):
        self.type = type
        self.command = 'brightnessctl'
        self.MAX_VALUE_BRIGHTNESS = 120000
        self.MIN_VALUE_BRIGHTNESS = 1200
        self.INTERVAL = 0.001
        self.changed = False
                
        # Value and time 
        self.actual_brightness_read_time = None # DELETE
        self.old_brightness_read = None
        self.old_brightness_read_time = time.time() # DELETE

        # reference, brightness [0,1]
        self.actual_brightness_read = None
        self.actual_brightness_1 = None
        self.actual_brightness_100 = None

        # queues, jobs and workers to threads
        self.queue = Jobs(1)
        self.thread = None
    
    def _convert_int_to_float(self, value):
        range_vals = [self.MIN_VALUE_BRIGHTNESS, self.MAX_VALUE_BRIGHTNESS]
        target_vals = [0, 1.0]
        res = float(np.interp(value, range_vals, target_vals))
        return res
    
    def _convert_float_to_int(self, value):
        range_vals = [0, 1.0]
        target_vals = [self.MIN_VALUE_BRIGHTNESS, self.MAX_VALUE_BRIGHTNESS]
        return round(np.interp(value, range_vals, target_vals))

    # Read current brightness from the system, updates actual_brightness_read and float
    def read_actual_brightness(self, actual=False):
        self.actual_brightness_read = self._get_command()
        self.actual_brightness_1 = self._convert_int_to_float(self.actual_brightness_read)
        self.actual_brightness_100 = round(self.actual_brightness_1 * 100)
        return self.actual_brightness_read if actual else self.actual_brightness_1

    def _get_command(self):
        try:
            with open(config.ACTUAL_BRIGHTNESS_PATH, "r") as f:
                content = f.read()
                if content.strip():
                    return int(content.strip())

        except FileNotFoundError:
            return None


    # Command to set brightness
    def _set_command(self, value):
        command_list = f"brightnessctl set {value}".split()
        return command_list
    

    # Sets brightness and updates variable value
    def set_brightness(self, value):
        if isinstance(value, float) and 0.0 <= value <= 1.0:
            value = self._convert_float_to_int(value)
        if not self.MIN_VALUE_BRIGHTNESS <= value <= self.MAX_VALUE_BRIGHTNESS:
            print(f"Value out of bounds: {self.MIN_VALUE_BRIGHTNESS} <= {value=}' <= {self.MAX_VALUE_BRIGHTNESS}")
            return
        
        self.queue.put(value)

        if not self.thread or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._worker, args=())
            self.thread.start()
            print(f"created new thread for {value}")
        
        self.actual_brightness_1 = self._convert_int_to_float(value)
        self.actual_brightness_100 = round(self.actual_brightness_1 * 100)


    # Checks if there are changes in reading
    def _check_changes(self):
        if self.changed == False and self.old_brightness_read != self.actual_brightness_read:
            return True
        else:
            return False


    def _worker(self):
        while True: 
            value = self.queue.get()
            if value is None:
                break
            command_list = self._set_command(value)
            subprocess.run(command_list, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(command_list) 
            print(f"\tset {value} to {self.type}")
    


class MonitorExt(MonitorInt):
    def __init__(self, type='external', name='ddcutil'):
        super().__init__()
        self.type = type
        self.command = 'ddcutil'
        self.MAX_VALUE_BRIGHTNESS = 100
        self.MIN_VALUE_BRIGHTNESS = 0
        self.INTERVAL = 1

    
    def _get_command(self):
        try:
             # Execute the ddcutil command to get the current brightness
            command_list = "ddcutil --display 1 getvcp 10".split()
            result = subprocess.run(command_list, capture_output=True, text=True, check=True)
            val = None
            for line in result.stdout.splitlines():
                if 'Brightness' in line:
                    parts = line.split('=')
                    val = int(parts[1].split(',')[0].strip())
                    break
            return val

        except subprocess.CalledProcessError as e:
            print(f"Error reading brightness: {e}")
            return None
    

    def _set_command(self, value):
        command_list = f"ddcutil --display 1 setvcp 10 {value}".split()
        return command_list