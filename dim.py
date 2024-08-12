import tkinter as tk
import subprocess
import json

# Hardcoded defaults
DEFAULT_CONFIG = {
    "brightness_screen_1": 100,
    "brightness_screen_2": 100,
    "link_sliders": False,
    "transparency": 90
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

# Function to set brightness using xrandr
def set_brightness(display, brightness):
    cmd = f"xrandr --output {display} --brightness {brightness}"
    subprocess.run(cmd, shell=True)
    print(cmd)

# Update brightness based on slider value
def update_brightness1(val):
    brightness = float(val) / 100
    set_brightness("eDP-1", brightness)  # Change eDP-1 to your primary display name
    if link_sliders.get():
        slider2.set(val)
    label1_value.config(text=val)

def update_brightness2(val):
    brightness = float(val) / 100
    set_brightness("DP-1", brightness)  # Changed to DP-1 for secondary display
    if link_sliders.get():
        slider1.set(val)
    label2_value.config(text=val)

# Function to update the transparency of the window
def update_transparency(val):
    alpha = float(val) / 100
    window.attributes("-alpha", alpha)
    label_transparency_value.config(text=val)

# Function to create the brightness control window
def create_window():
    global window, link_sliders, slider1, slider2
    global label1_value, label2_value, label_transparency_value

    # Create the main Tkinter window
    window = tk.Tk()
    window.title("Brightness Control")

    # Set a fixed size for the window
    window.geometry("300x100")
    
    # Prevent the window from being resized
    window.resizable(False, False)

    # Initialize Tkinter variables after root is created
    link_sliders = tk.BooleanVar(value=config['link_sliders'])

    # Create and configure sliders and controls
    tk.Label(window, text="Screen 1 Brightness").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    slider1 = tk.Scale(window, from_=0, to=100, orient="horizontal", command=update_brightness1, showvalue=False)
    slider1.set(config['brightness_screen_1'])  # Load from config
    slider1.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    # Custom label for showing slider value
    label1_value = tk.Label(window, text=str(config['brightness_screen_1']))
    label1_value.grid(row=0, column=2, padx=10, pady=5, sticky="w")

    tk.Label(window, text="Screen 2 Brightness").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    slider2 = tk.Scale(window, from_=0, to=100, orient="horizontal", command=update_brightness2, showvalue=False)
    slider2.set(config['brightness_screen_2'])  # Load from config
    slider2.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    # Custom label for showing slider value
    label2_value = tk.Label(window, text=str(config['brightness_screen_2']))
    label2_value.grid(row=1, column=2, padx=10, pady=5, sticky="w")

    # Create and pack the check button to link the sliders
    link_check = tk.Checkbutton(window, text="Link Sliders", variable=link_sliders)
    link_check.grid(row=2, column=0, columnspan=3, pady=10)

    # # Create and pack the transparency slider
    # tk.Label(window, text="Transparency").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    # transparency_slider = tk.Scale(window, from_=0, to=100, orient="horizontal", command=update_transparency, showvalue=False)
    # transparency_slider.set(config['transparency'])  # Load from config
    # transparency_slider.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

    # # Custom label for showing transparency value
    # label_transparency_value = tk.Label(window, text=str(config['transparency']))
    # label_transparency_value.grid(row=3, column=2, padx=10, pady=5, sticky="w")

    # Set the initial transparency
    window.attributes("-alpha", config['transparency'] / 100)

    # Adjust column weights to make sure sliders expand
    window.grid_columnconfigure(1, weight=1)

    # Start the Tkinter event loop
    window.mainloop()

# Create and show the window immediately
create_window()
