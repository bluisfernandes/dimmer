import tkinter as tk
from configs import config
from utils import (read_actual_brightness, 
                   read_current_brightness_ddcutil, 
                   get_connected_monitors,
                   set_brightness_ddcutil,
                   set_brightness_brightnessctl,
                   on_slider_change,
                   update_brightness_main
                   )

# Throttle variables
UPDATE_INTERVAL = 0.1  # seconds
last_update_time = {}


# Function to create the brightness control window
def create_window():
    global window, link_sliders, label_dict, sliders, sliders_hardware, link_sliders2
    global label_transparency_value

    # Get the list of connected monitors
    global connected_monitors
    global main, second_monitor
    second_monitor = None
    connected_monitors = get_connected_monitors()

    # Create the main Tkinter window
    window = tk.Tk()
    window.title("Brightness Control")

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

    row = 0
    for monitor in connected_monitors:
        brightness = int(max(read_actual_brightness(ratio=1/1200), config.MIN_BRIGHTNESS * 100))
        tk.Label(window, text=f"{monitor} Brightness").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        
        slider = tk.Scale(window, from_=config.LINK_SLIDERS * 100, to=100, orient="horizontal", command=lambda val, m=monitor: on_slider_change(val,last_update_time, label_dict, sliders, link_sliders, m), showvalue=False, length=300)
        
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
        link_check = tk.Checkbutton(window, text="Link software", variable=link_sliders)
        link_check.grid(row=row, column=0, columnspan=1, pady=10)
        link_check2 = tk.Checkbutton(window, text="Link hardware", variable=link_sliders2)
        link_check2.grid(row=row, column=1, columnspan=1, pady=10)
        row += 1

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

# Create and show the window immediately
create_window()
