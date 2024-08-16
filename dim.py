import tkinter as tk
import threading
from configs import config
from PIL import Image, ImageDraw
from pystray import MenuItem as item
import pystray
import math
from utils import (read_actual_brightness, 
                   read_current_brightness_ddcutil, 
                   get_connected_monitors,
                   set_brightness_ddcutil,
                   set_brightness_brightnessctl,
                   on_slider_change,
                   update_brightness_main
                   )

# Tkinter window (GUI)
class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Brightness Control")
        self.is_open = True

    def open(self):
        if not self.is_open:
            self.root.deiconify()
            self.is_open = True

    def close(self):
        if self.is_open:
            self.root.withdraw()
            self.is_open = False

# Callback functions for tray menu
def on_open(icon, item):
    app.open()

def on_close(icon, item):
    app.close()

def on_quit(icon, item):
    # Open the app GUI to avoid runtimeError with thread.
    app.open()
    icon.stop()
    window.quit()

# Setup tray menu
menu = (
    item('Open GUI', on_open),
    item('Close GUI', on_close),
    item('Quit', on_quit)
)

# Create the brightness GUI
def create_window():
    global window, app
    # Throttle variables
    last_update_time = {}    
    second_monitor = None
    connected_monitors = get_connected_monitors()

    # Create the main Tkinter window
    window = tk.Tk()
    app = MyApp(window)
    window.protocol("WM_DELETE_WINDOW", app.close)
    # window.title("Brightness Control")

    # Set a fixed size for the window
    window.geometry("350x180")
    
    # Prevent the window from being resized
    window.resizable(False, False)
    window.attributes("-topmost", True)

    # Initialize Tkinter variables 
    link_sliders = tk.BooleanVar(value=config.LINK_SLIDERS)
    link_sliders2 = tk.BooleanVar(value=config.LINK_SLIDERS2)
    label_dict = {}
    sliders = []
    sliders_hardware = []
    initial_brightness = config.MAX_BRIGHTNESS * 100

    # Scales via software
    row = 0
    for monitor in connected_monitors:
        tk.Label(window, text=f"{monitor} Brightness").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        
        slider = tk.Scale(window, from_=config.LINK_SLIDERS * 100, to=100, orient="horizontal", command=lambda val, m=monitor: on_slider_change(val,last_update_time, label_dict, sliders, link_sliders, m), showvalue=False, length=300)
        
        slider.set(initial_brightness)  # Load from system
        slider.grid(row=row, column=1, padx=10, pady=5, sticky="ew")

        # Custom label for showing slider value with fixed width and monospaced font
        label = tk.Label(window, text=str(initial_brightness), font=("Courier", 10), width=5, anchor="w")
        label.grid(row=row, column=2, padx=10, pady=5, sticky="w")
        label_dict[monitor] = label

        sliders.append(slider)

        row += 1

    # Create and pack the check button to link the sliders
    if len(connected_monitors) > 1:
        link_check = tk.Checkbutton(window, text="Link software", variable=link_sliders)
        link_check.grid(row=row, column=0, columnspan=1, pady=10)
        link_check2 = tk.Checkbutton(window, text="Link hardware", variable=link_sliders2)
        link_check2.grid(row=row, column=1, columnspan=1, pady=10)
        row += 1


    # Scales via hardware
    tk.Label(window, text="main monitor").grid(row=row, column=0, padx=10, pady=5, sticky="w")
    main = tk.Scale(window, from_=1200, to=120000, orient="horizontal", command=lambda val: set_brightness_brightnessctl(int(val), second_monitor, label_dict, link_sliders2, last_update_time), showvalue=False, length=300)
    main.set(read_actual_brightness())  # Load from system
    main.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
    sliders_hardware.append(main)

    # Custom label for showing slider value
    label = tk.Label(window, text=str(read_actual_brightness()), font=("Courier", 10), width=5, anchor="w")
    label.grid(row=row, column=2, padx=10, pady=5, sticky="w")
    label_dict['main'] = label
    row += 1

    if len(connected_monitors) >1:
        tk.Label(window, text="second monitor").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        second_monitor = tk.Scale(window, from_=0, to=100, orient="horizontal", command=lambda val: set_brightness_ddcutil(int(val),second_monitor, label_dict, last_update_time), showvalue=False, length=300)
        current_brightness = read_current_brightness_ddcutil()
        second_monitor.set(current_brightness)  # Load from system
        second_monitor.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        sliders_hardware.append(second_monitor)

        # Custom label for showing slider value
        label = tk.Label(window, text=str(current_brightness), font=("Courier", 10), width=5, anchor="w")
        label.grid(row=row, column=2, padx=10, pady=5, sticky="w")
        label_dict['second'] = label


    # Set the initial transparency
    window.after(100, lambda: window.attributes("-alpha", config.TRANSPARENCY / 100))

    # Adjust column weights to make sure sliders expand
    window.grid_columnconfigure(1, weight=1)
    
    # Start the periodic brightness update
    update_brightness_main(window, label_dict, main, second_monitor, link_sliders2)

    # Start the Tkinter event loop
    window.mainloop()

# Function to create a simple image for the tray icon
def create_image(color):
    width = 64
    height = 64
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.rectangle((0, 0, width, height), fill=color)
    return image

def create_image(color):
    width = 64
    height = 64
    image = Image.new('RGBA', (width, height), (173, 216, 230, 255))  # Light blue background
    dc = ImageDraw.Draw(image)
    
    # Draw the circle in the middle
    circle_radius = 12
    circle_center = (width // 2, height // 2)
    dc.ellipse(
        (circle_center[0] - circle_radius, circle_center[1] - circle_radius,
         circle_center[0] + circle_radius, circle_center[1] + circle_radius),
        fill="black"
    )
    
    # Draw the sun rays
    num_rays = 8
    ray_length = 25
    for i in range(num_rays):
        angle = 360 / num_rays * i
        x_end = circle_center[0] + ray_length * math.cos(math.radians(angle))
        y_end = circle_center[1] + ray_length * math.sin(math.radians(angle))
        dc.line([circle_center, (x_end, y_end)], fill="black", width=6)
    
    return image

# Function to set up the tray icon
def setup(icon):
    icon.visible = True
    
# Create and run the tray icon in a separate thread
icon = pystray.Icon("brightness_icon", create_image((255, 0, 0, 255)), menu=menu)
threading.Thread(target=icon.run, args=(setup,)).start()

# Start the Tkinter app in the main thread
create_window()
