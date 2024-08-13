import tkinter as tk
import subprocess
import json
import time

# Hardcoded defaults
DEFAULT_CONFIG = {
    "brightness_screen_1": 100,
    "brightness_screen_2": 100,
    "link_sliders": False,
    "transparency": 60
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

# Throttle variables
last_update_time = {}
update_interval = 0.1  # seconds

# Function to read current brightness from the system
def read_brightness(monitor):
    try:
        with open(f"/sys/class/backlight/intel_backlight/actual_brightness", "r") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return 1200  # Default value if unable to read

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
    current_time = time.time()
    if display not in last_update_time or (current_time - last_update_time[display]) >= update_interval:
        last_update_time[display] = current_time
        cmd = f"xrandr --output {display} --brightness {brightness}"
        subprocess.run(cmd, shell=True)
        print(cmd)

# Update brightness based on slider value
def update_brightness(monitor, val):
    brightness = float(val) / 100
    set_brightness(monitor, brightness)
    label_dict[monitor].config(text=val)

# # Function to update the transparency of the window
# def update_transparency(val):
#     alpha = float(val) / 100
#     window.attributes("-alpha", alpha)
#     label_transparency_value.config(text=val)

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
        tk.Label(window, text=f"{monitor} Brightness").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        slider = tk.Scale(window, from_=0, to=100, orient="horizontal", command=lambda val, m=monitor: on_slider_change(val, m), showvalue=False, length=300)
        slider.set(read_brightness(monitor))  # Load from system
        slider.grid(row=row, column=1, padx=10, pady=5, sticky="ew")

        # Custom label for showing slider value with fixed width and monospaced font
        label = tk.Label(window, text=str(read_brightness(monitor)), font=("Courier", 10), width=5, anchor="w")
        label.grid(row=row, column=2, padx=10, pady=5, sticky="w")
        label_dict[monitor] = label

        sliders.append(slider)

        row += 1

    # Create and pack the check button to link the sliders
    if len(connected_monitors) > 1:
        link_check = tk.Checkbutton(window, text="Link Sliders", variable=link_sliders)
        link_check.grid(row=row, column=0, columnspan=3, pady=10)
        row += 1

    # # Create and pack the transparency slider
    # tk.Label(window, text="Transparency").grid(row=row, column=0, padx=10, pady=5, sticky="w")
    # transparency_slider = tk.Scale(window, from_=0, to=100, orient="horizontal", command=update_transparency, showvalue=False, length=300)
    # transparency_slider.set(config['transparency'])  # Load from config
    # transparency_slider.grid(row=row, column=1, padx=10, pady=5, sticky="ew")

    # # Custom label for showing transparency value with fixed width and monospaced font
    # label_transparency_value = tk.Label(window, text=str(config['transparency']), font=("Courier", 10), width=5, anchor="w")
    # label_transparency_value.grid(row=row, column=2, padx=10, pady=5, sticky="w")

    # Set the initial transparency
    window.after(100, lambda: window.attributes("-alpha", config['transparency'] / 100))

    # Adjust column weights to make sure sliders expand
    window.grid_columnconfigure(1, weight=1)

    # Start the Tkinter event loop
    window.mainloop()

# Create and show the window immediately
create_window()
