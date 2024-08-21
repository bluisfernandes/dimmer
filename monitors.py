import numpy as np
import time
import subprocess
from configs import config

class MonitorInt():
    def __init__(self, type='internal'):
        self.type = type
        self.command = 'brightnessctl'
        self.MAX_VALUE_BRIGHTNESS = 120000
        self.MIN_VALUE_BRIGHTNESS = 1200
        self.INTERVAL = 0.001
        self.changed = False
        
        # Value and time 
        self.actual_brightness_read = None
        self.actual_brightness_read_time = None
        self.old_brightness_read = None
        self.old_brightness_read_time = time.time()

        # reference, brightness [0,1]
        self.actual_brightness_1 = None
        self.brightness_last_set = None


    # Read current brightness from the system, updates actual_brightness_read and float
    def read_actual_brightness(self):
        range_vals = [self.MIN_VALUE_BRIGHTNESS, self.MAX_VALUE_BRIGHTNESS]
        target_vals = [0, 1.0]
        try:
            with open(config.ACTUAL_BRIGHTNESS_PATH, "r") as f:
                content = f.read()
                if content.strip():
                    val = int(float(content.strip()))
                    self.actual_brightness_read = int(val)
                    self.actual_brightness_1 = int(np.interp(val, range_vals, target_vals))
                    print(self.actual_brightness_read, val, range_vals, target_vals)
                    return val

        except FileNotFoundError:
            return self.MAX_VALUE  # Default value if unable to read


    # Sets brightness and updates variable value
    def set_brightness(self, value):
        if isinstance(value, float) and 0.0 <= value <= 1.0:
            target_vals = [self.MIN_VALUE_BRIGHTNESS, self.MAX_VALUE_BRIGHTNESS]
            range_vals= [0.0, 1.0]
            value = int(np.interp(value, range_vals, target_vals))
        if not self.MIN_VALUE_BRIGHTNESS <= value <= self.MAX_VALUE_BRIGHTNESS:
            print(f"Value out of bounds: {self.MIN_VALUE_BRIGHTNESS} <= {value=}' <= {self.MAX_VALUE_BRIGHTNESS}")
            return
        command_list = f"brightnessctl set {value}".split()
        subprocess.run(command_list, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.brightness_last_set = value
        print(command_list)


    # Checks if there are changes in reading
    def check_changes(self):
        if self.changed == False and self.old_brightness_read != self.actual_brightness_read:
            return True
        else:
            return False
    

    def should_set(self, value):
        return value != self.brightness_last_set
    

    def on_set(self, value):
        self.set_brightness(value)
        # if not self.should_set(value):
        #     return
        # self.actual_brightness_read_time = time.time()
        # if self.actual_brightness_read_time - self. old_brightness_read_time >= self.INTERVAL:
        #     self.old_brightness_read_time = self.actual_brightness_read_time
        #     self.set_brightness(value)
        # else:
        #     print('Wait', self. actual_brightness_read_time - self.old_brightness_read_time, 's.')



class MonitorExt(MonitorInt):
    def __init__(self, type='external', name='ddcutil'):
        super().__init__()
        self.type = type
        self.command = 'ddcutil'
        self.MAX_VALUE_BRIGHTNESS = 100
        self.MIN_VALUE_BRIGHTNESS = 0
        self.INTERVAL = 1


    # Read current brightness from the system, updates actual_brightness_read and float
    def read_actual_brightness(self):
        range_vals = [self.MIN_VALUE_BRIGHTNESS, self.MAX_VALUE_BRIGHTNESS]
        target_vals = [0, 1.0]
        try:
            # Execute the ddcutilcommand to get the current brightness
            command_list = "ddcutil --display 1 getvcp 10".split()
            result = subprocess.run(command_list, capture_output=True, text=True, check=True)
            val = None
            for line in result.stdout.splitlines():
                if 'Brightness' in line:
                    parts = line.split('=')
                    val = parts[1].split(',')[0].strip()
                    break
            self.actual_brightness_read = int(val)
            self.actual_brightness_1 = int(np.interp(val, range_vals, target_vals))
            print(self.actual_brightness_read, val, range_vals, target_vals)
            return val
        
        except subprocess.CalledProcessError as e:
            print(f"Error reading brightness: {e}")
            return None


    def set_brightness(self, value):
        if isinstance(value, float) and 0.0 <= value <= 1.0:
            target_vals = [self.MIN_VALUE_BRIGHTNESS, self.MAX_VALUE_BRIGHTNESS]
            range_vals= [0.0, 1.0]
            value = int(np.interp(value, range_vals, target_vals))
        elif not self.MIN_VALUE_BRIGHTNESS <= value <= self.MAX_VALUE_BRIGHTNESS:
            print(f"Value out of bounds: {self.MIN_VALUE_BRIGHTNESS} <= {value=}' <= {self.MAX_VALUE_BRIGHTNESS}")
            return
        command_list = f"ddcutil --display 1 setvcp 10 {value}".split()
        subprocess.run(command_list, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.brightness_last_set = value
        print(command_list)

print(config.TRANSPARENCY)