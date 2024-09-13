from monitors import MonitorInt, MonitorExt, MonitorSoftware
import subprocess
import customtkinter

customtkinter.set_default_color_theme("blue")

class Dimmer():
    def __init__(self):
        self.title='Control Brightness'
        self.monitors = {}
        self.linked = True
        self.update_connection()
        self.brightnesses = {}
        self._initialize_brightness()
        
    def __repr__(self):
         return f"ClassDimmer: {self.title}, monitors: {self.monitors}"
    
    def update_connection(self):
        self._check_connection_primary()
        self._check_connection_second()
        self._check_connection_software(' eDP-1', type='internal')
        self._check_connection_software(' DP-1', type='external')

    def _check_connection_primary(self, display_name='intel'):
        command_list = "brightnessctl -l |grep "'backlight'"".split()
        result = subprocess.run(command_list, capture_output=True, text=True, check=True)
        if display_name in result.stdout:
             if display_name not in self.monitors:
                self.monitors[display_name] = MonitorInt(display_name)
        elif display_name in self.monitors:
            del self.monitors[display_name]
    
    def _check_connection_second(self, display_name='Display 1'):
        command_list = "ddcutil detect".split()
        result = subprocess.run(command_list, capture_output=True, text=True, check=True)
        name = str.lower(display_name)
        if display_name in result.stdout:
            if name not in self.monitors:
                self.monitors[name] = MonitorExt(name)
        elif name in self.monitors:
                del self.monitors[name]

    def _check_connection_software(self, display_name=' eDP-1',*args, **kwargs):
        command_list = "xrandr --listactivemonitors".split()
        result = subprocess.run(command_list, capture_output=True, text=True, check=True)
        name = str.lower(display_name)
        if display_name in result.stdout:
            if name not in self.monitors:
                self.monitors[name] = MonitorSoftware(display=''.join(display_name.split()), *args, **kwargs)
        elif name in self.monitors:
                del self.monitors[name]
    
    def _initialize_brightness(self):
        value = round(self.monitors['intel'].read() * 100)
        self.brightnesses['intel'] = value

    def link_update(self):
        if self.linked and len(self.monitors) >= 2:
            val=self.monitors['intel'].read()
            self.brightnesses['intel'] = round(val * 100)
            if self.monitors['display 1'].actual_brightness_100 != round(val * 100):
                self.monitors['display 1'].set(val)
                self.brightnesses['display 1'] = round(val * 100)
            return round(val * 100)

    def slider_set(self, value, monitor=None):
        if monitor:
            if isinstance(monitor,str):
                monitor = self.monitors.get(monitor)
            monitor.set(value)
            self.brightnesses.update({monitor.name :round(value*100)})
        elif self.linked is True:
            for _, monitor in self.monitors.items():
                monitor.set(value)
                self.brightnesses.update({monitor.name :value*100})
    
    def check_if_changed(self):
        value = self.monitors['intel'].read()
        value = round(value * 100)
        if self.brightnesses['intel'] != value:
            self.brightnesses['intel'] = value
            return value
        else:
            return None
    
    


class Gui(customtkinter.CTk):
    def __init__(self, dimmer):
        super().__init__()
        self.dimmer = dimmer
        self.title('Brightness Control')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)

        self.frame = ControlGui(self, self.dimmer, "backlight", name_int='intel', name_ext='display 1')
        self.frame.grid(row=0, column=0, padx=5, pady=5)

        self.frame2 = ControlGui(self, self.dimmer, "software", name_int=' edp-1', name_ext=' dp-1')
        self.frame2.grid(row=1, column=0, padx=5, pady=5)


class ControlGui(customtkinter.CTkFrame):
    def __init__(self, parent, dimmer, function, name_int='intel', name_ext='display 1'):
        super().__init__(parent)
        self.dimmer = dimmer
        self.monitors = dimmer.monitors
        self.name_int = name_int
        self.name_ext = name_ext
        self.link = True
        self.monitor2_connected = self.name_ext in self.monitors
        self.monitor2_created = False
        self.min_scale = 0 if self.name_int == 'intel' else 20

        # Monitor 1
        if self.name_int in self.monitors.keys():
            self.name1 =customtkinter.CTkLabel(self, text=self.monitors[self.name_int].type, width=70, anchor='center')
            self.name1.grid(row=0, column=0)

            initial_value = self.dimmer.monitors[self.name_int].actual_brightness_100

            self.label1 = customtkinter.CTkLabel(self, text=initial_value, width=40, anchor="center")
            self.label1.grid(row=0, column=1)

            self.scale1 = customtkinter.CTkSlider(self, from_=self.min_scale, to=100, command= lambda val: self.on_slide(val, self.monitors[self.name_int], self.label1), number_of_steps=100-self.min_scale)
            self.scale1.set(initial_value)
            self.scale1.grid(row=0, column=2)

        # Function name
        self.function = customtkinter.CTkLabel(self, text=function, width=80, anchor="center")
        self.function.grid(row=0, column=3)

        self.switch2 = customtkinter.CTkSwitch(self, command=self.update_monitors, text="update")
        self.switch2.grid(row=1, column=4)

        if self.monitor2_connected:
            self.monitor2_create(self.monitors)
        

    def monitor2_create(self, monitors):
        # Monitor 2
        self.monitor2_connected = True
        if self.name_ext in monitors.keys():

            self.monitor2_created = True
            self.name2 =customtkinter.CTkLabel(self, text=monitors[self.name_ext].type, width=70, anchor='center')
            self.name2.grid(row=1, column=0)

            initial_value = self.dimmer.monitors[self.name_ext].actual_brightness_100

            self.label2 = customtkinter.CTkLabel(self, text=initial_value, width=40, anchor="center")
            self.label2.grid(row=1, column=1)

            self.scale2 = customtkinter.CTkSlider(self, from_=self.min_scale, to=100, command= lambda val: self.on_slide(val, monitors[self.name_ext], self.label2), number_of_steps=100-self.min_scale)
            self.scale2.set(initial_value)
            self.scale2.grid(row=1, column=2)
            
            # Link monitors
            switch_state = customtkinter.BooleanVar(value=self.link)
            self.switch = customtkinter.CTkSwitch(self, command=self.toggle_link, variable=switch_state, width=80, text="join")
            self.switch.grid(row=1, column=3)
            # Update GUI with correct layout
            self.link = not self.link
            self.toggle_link()

    def monitor2_hide(self):
        self.name2.grid_forget()
        self.label2.grid_forget()
        self.scale2.grid_forget()
        self.switch.grid_forget()

    def monitor2_show(self):
        self.name2.grid(row=1, column=0)
        self.label2.grid(row=1, column=1)
        self.scale2.grid(row=1, column=2)
        self.switch.grid(row=1, column=3)

    def on_slide(self, value, monitor, label):
        value = int(value)
        if self.link and self.monitor2_connected:
            self.label1.configure(text=value)
            self.label2.configure(text=value)
            self.scale2.set(value)
            # Update brightness of all monitors
            for monitor in self.monitors:
                if monitor in [self.name_int, self.name_ext]:
                    self.dimmer.slider_set(value/100, monitor)
        else:
            label.configure(text=value)
            # Update brightness of one monitors
            self.dimmer.slider_set(value/100, monitor)
    
    def toggle_link(self):
        self.link = not self.link
        if self.link:
            self.scale2.configure(state='disabled', button_color = ('gray40', '#AAB0B5'), progress_color='transparent')
            self.scale2.set(self.scale1.get())
            self.label2.grid_forget()
            # update brightness and label
            self.label2.configure(text=self.dimmer.link_update())
        else:
            self.scale2.configure(state='normal', button_color=('#3B8ED0', '#1F6AA5'), progress_color=('#3B8ED0', '#1F6AA5'))
            self.label2.grid(row=1, column=1)
    
    def toggle_monitor2_connection(self):
        if self.monitor2_created:
            self.monitor2_connected = not self.monitor2_connected
            if self.monitor2_connected:
                self.monitor2_show()
            else:
                self.monitor2_hide()
    
    def update_monitors(self):
        self.dimmer.update_connection()
        if self.name_ext in self.monitors:
            if not self.monitor2_created:
                self.monitor2_create(self.monitors)
            else:
                self.monitor2_show()
        else:
            if self.monitor2_created:
                self.monitor2_hide()

    
    def update_remote_values(self, time=0):
        value = self.dimmer.check_if_changed()
        if value is not None:
            self.on_slide(value, self.monitors[self.name_int], self.label1)
            self.scale1.set(value)
        self.after(time, lambda: gui.frame.update_remote_values(time=time))
        
           
d = Dimmer()
gui = Gui(d)
# read brightness changes made from computer and updates GUI
gui.after(3000, lambda: gui.frame.update_remote_values(time=200))
gui.mainloop()