import tkinter as tk
import subprocess
import json
import time

# Hardcoded defaults
DEFAULT_CONFIG = {
    "dont_change_screen" : [],
    "link_sliders": False,
    "transparency": 87,
    "actual_brightness_path": "/sys/class/backlight/intel_backlight/actual_brightness",
    "min_brightness": 0.20,
    "max_brightness": 1.00
}

# Function to load and merge configurations
def load_config():
    try:
        with open("user_config.json", "r") as f:
            user_config = json.load(f)
    except FileNotFoundError:
        user_config = {}

    # Merge user config over default config
    config = {**DEFAULT_CONFIG, **user_config}
    return config

# Load the configuration
config = load_config()

config["min_brightness"] =min(config["min_brightness"], config["max_brightness"]) 

# Throttle variables
UPDATE_INTERVAL = 0.1  # seconds
last_update_time = {}

# Function to read current brightness from the system
def read_actual_brightness():
    try:
        with open(config['actual_brightness_path'], "r") as f:
            content = f.read()
            if content.strip():
                val = int(float(content.strip()) / 1200)
                return val
    except FileNotFoundError:
        return 100  # Default value if unable to read

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
def set_brightness(display, brightness):
    brightness = max(brightness, config["min_brightness"])
    current_time = time.time()
    if display not in last_update_time or (current_time - last_update_time[display]) >= UPDATE_INTERVAL:
        if display in config["dont_change_screen"]:
            return
        last_update_time[display] = current_time
        cmd = f"xrandr --output {display} --brightness {brightness}"
        subprocess.run(cmd, shell=True)
        print(cmd)

# Update brightness based on slider value
def update_brightness(monitor, val):
    brightness = float(val) / 100
    set_brightness(monitor, brightness)
    label_dict[monitor].config(text=val)

# Function to synchronize slider values when linking is enabled
def synchronize_sliders(val):
    # Avoid updating sliders if they are not linked
    if not link_sliders.get():
        return
    
    # Update all sliders except the one that triggered the change
    for slider in sliders:
        if slider.get() != int(val):
            slider.set(val)

# Function to handle slider change
def on_slider_change(val, monitor=None):
    if link_sliders.get():
        synchronize_sliders(val)
    update_brightness(monitor, val)

# Function to create the brightness control window
def create_window():
    global window, link_sliders, label_dict, sliders
    global label_transparency_value

    # Get the list of connected monitors
    global connected_monitors
    connected_monitors = get_connected_monitors()

    # Create the main Tkinter window
    window = tk.Tk()
    window.title("Brightness Control")

    # Set a fixed size for the window
    window.geometry("350x130")
    
    # Prevent the window from being resized
    window.resizable(False, False)
    window.attributes("-topmost", True)

    # Initialize Tkinter variables 
    link_sliders = tk.BooleanVar(value=config['link_sliders'])
    label_dict = {}
    sliders = []

    row = 0
    for monitor in connected_monitors:
        brightness = int(max(read_actual_brightness(), config["min_brightness"] * 100))
        tk.Label(window, text=f"{monitor} Brightness").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        slider = tk.Scale(window, from_=config["min_brightness"] * 100, to=100, orient="horizontal", command=lambda val, m=monitor: on_slider_change(val, m), showvalue=False, length=300)
        slider.set(brightness)  # Load from system
        slider.grid(row=row, column=1, padx=10, pady=5, sticky="ew")

        # Custom label for showing slider value with fixed width and monospaced font
        label = tk.Label(window, text=str(brightness), font=("Courier", 10), width=5, anchor="w")
        label.grid(row=row, column=2, padx=10, pady=5, sticky="w")
        label_dict[monitor] = label

        sliders.append(slider)

        row += 1

    # Create and pack the check button to link the sliders
    if len(connected_monitors) > 1:
        link_check = tk.Checkbutton(window, text="Link Sliders", variable=link_sliders)
        link_check.grid(row=row, column=0, columnspan=3, pady=10)
        row += 1

    # Set the initial transparency
    window.after(100, lambda: window.attributes("-alpha", config['transparency'] / 100))

    # Adjust column weights to make sure sliders expand
    window.grid_columnconfigure(1, weight=1)
    
    # Start the Tkinter event loop
    window.mainloop()

# Create and show the window immediately
create_window()
