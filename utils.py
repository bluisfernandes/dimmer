from configs import config
import subprocess
import time
import threading

# Function to read current brightness from the system
def read_actual_brightness(ratio=1):
    try:
        with open(config.ACTUAL_BRIGHTNESS_PATH, "r") as f:
            content = f.read()
            if content.strip():
                val = int(float(content.strip()) * ratio)
                return val
    except FileNotFoundError:
        return 100  # Default value if unable to read
    
# Function to read current brightness from the external monitor with ddcutil
def read_current_brightness_ddcutil():
    try:
        # Execute the brightnessctl command to get the current brightness
        command_list = "ddcutil --display 1 getvcp 10".split()
        result = subprocess.run(command_list, capture_output=True, text=True, check=True)
        brightness = None
        for line in result.stdout.splitlines():
            if 'Brightness' in line:
                parts = line.split('=')
                brightness = parts[1].split(',')[0].strip()
                break

        return brightness
    except subprocess.CalledProcessError as e:
        print(f"Error reading brightness: {e}")
        return None
    
# Function to get the list of connected monitors
def get_connected_monitors():
    try:
        output = subprocess.check_output(['xrandr'], text=True)
        lines = output.split('\n')
        monitors = []
        for line in lines:
            if ' connected ' in line:
                monitor_name = line.split(' ')[0]
                monitors.append(monitor_name)
        return monitors
    except subprocess.CalledProcessError as e:
        print("Error running xrandr:", e)
        return []
    
# Function to set brightness using xrandr with throttling
def set_brightness(display, brightness, last_update_time):
    brightness = max(brightness, config.MIN_BRIGHTNESS)
    current_time = time.time()
    # print("###", current_time, last_update_time[display])
    if display not in last_update_time or (current_time - last_update_time[display]) >= config.UPDATE_INTERVAL:
        if display in config.DONT_CHANGE_SCREEN:
            return
        last_update_time[display] = current_time
        cmd_list = f"xrandr --output {display} --brightness {brightness}".split()
        subprocess.run(cmd_list)

# Function to set brightness with brightnessctl
def set_brightness_ddcutil(value, second_monitor, label_dict, last_update_time):
    """Sets the brightness using ddcutil."""
    def set_brightness_thread(value):
        try:
            if not isinstance(value, int) or value < 0 or value > 100:
                raise ValueError(f"Brightness value must be an integer between 0 and 100, not {value}, {type(value)}")
            
            brightness_str = f'{value}'
            command_list = f"ddcutil --display 1 setvcp 10 {brightness_str}".split()

            subprocess.run(command_list, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if second_monitor:
                label_dict['second'].config(text=value)

        except subprocess.CalledProcessError as e:
            print(f"Error setting brightness: {e}")
        except ValueError as ve:
            print(ve)
        finally:
            if second_monitor:
                label_dict['second'].config(text=value)
    
    current_time = time.time()
    if 'ddcutil' not in last_update_time or (current_time - last_update_time['ddcutil']) >= config.UPDATE_INTERVAL:

        last_update_time['ddcutil'] = current_time

        # Run the command in a separate thread
        threading.Thread(target=set_brightness_thread, args=(value,)).start()

# Function to set brightness with brightnessctl
def set_brightness_brightnessctl(value, second_monitor, label_dict, link_sliders2, last_update_time):
    """Sets the brightness using brightnessctl."""
    try:
        if not isinstance(value, int) or value < 1200 or value > 120000:
            raise ValueError(f"Brightness value must be an integer between 1200 and 120000, not {value}, {type(value)}")

        brightness_str = f'{value}'

        # Execute the brightnessctl command to set the brightness
        command_list = f"brightnessctl set {brightness_str}".split()
        subprocess.run(command_list, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if link_sliders2.get():
            set_brightness_ddcutil(int(value / 1200), second_monitor, label_dict, last_update_time)
    except subprocess.CalledProcessError as e:
        print(f"Error setting brightness: {e}")
    except ValueError as ve:
        print(ve)
    
    label_dict['main'].config(text=value)


# Update brightness based on slider value
def update_brightness(monitor, val,last_update_time,label_dict=dict()):
    brightness = float(val) / 100
    set_brightness(monitor, brightness, last_update_time)
    if monitor in label_dict and hasattr(label_dict[monitor], 'config'):
        label_dict[monitor].config(text=val)


# Function to handle slider change
def on_slider_change(val,last_update_time, label_dict, sliders, link_sliders, monitor=None):

    if link_sliders.get():
        synchronize_sliders(val, sliders, link_sliders)
    update_brightness(monitor, val,last_update_time, label_dict)


def update_brightness_main(window, label_dict, main, second_monitor, link_sliders2):
    def update_brightness_main_thread(main, second_monitor):
        """Periodically checks and updates the slider and label with the current brightness."""
        current_brightness = read_actual_brightness()
        if current_brightness is not None:
            main.set(current_brightness)
            label_dict['main'].config(text=f"{current_brightness}")
        
        if second_monitor:
            if link_sliders2.get():
                current_brightness = int(current_brightness / 1200)
            
            else:
                current_brightness = read_current_brightness_ddcutil()
            
            if current_brightness is not None:
                second_monitor.set(current_brightness)
                label_dict['second'].config(text=f"{current_brightness}")

    update_thread = threading.Thread(target=update_brightness_main_thread, args=(main, second_monitor))

    update_thread.start()

    window.after(1000, lambda: update_brightness_main(window, label_dict, main, second_monitor, link_sliders2))

    # Function to synchronize slider values when linking is enabled
def synchronize_sliders(val, sliders, link_sliders):
    # Avoid updating sliders if they are not linked
    if not link_sliders.get():
        return
    
    # Update all sliders except the one that triggered the change
    for slider in sliders:
        if slider.get() != int(val):
            slider.set(val)

