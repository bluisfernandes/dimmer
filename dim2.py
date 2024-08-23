from monitors import MonitorInt, MonitorExt
import subprocess
import customtkinter

customtkinter.set_default_color_theme("blue")

class Dimmer():
    def __init__(self):
        self.title='Control Brightness'
        self.monitors = {}
        self.linked = True
        self.update_connection()
    
    def __repr__(self):
         return f"ClassDimmer: {self.title}, monitors: {self.monitors}"
    
    def update_connection(self):
        self._check_connection_primary()
        self._check_connection_second()

    def _check_connection_primary(self, display_name='intel'):
        command_list = "brightnessctl -l |grep "'backlight'"".split()
        result = subprocess.run(command_list, capture_output=True, text=True, check=True)
        if display_name in result.stdout:
             if display_name not in self.monitors:
                self.monitors[display_name] = MonitorInt()
        elif display_name in self.monitors:
            del self.monitors[display_name]
    
    def _check_connection_second(self, display_name='Display 1'):
        command_list = "ddcutil detect".split()
        result = subprocess.run(command_list, capture_output=True, text=True, check=True)
        name = str.lower(display_name)
        if display_name in result.stdout:
            if name not in self.monitors:
                self.monitors[name] = MonitorExt()
        elif name in self.monitors:
                del self.monitors[name]
    
    def link_update(self):
        if self.linked and len(self.monitors) >= 2:
            val=self.monitors['intel'].read()
            print(round(val * 100), end='')
            if self.monitors['display 1'].actual_brightness_100 != round(val * 100):
                self.monitors['display 1'].set(val)
            return round(val * 100)

    def slider_set(self, value, monitor=None):
        if monitor:
            if isinstance(monitor,str):
                monitor = self.monitors.get(monitor)
            monitor.set(value)
        elif self.linked is True:
            for _, monitor in self.monitors.items():
                monitor.set(value)


class Gui(customtkinter.CTk):
    def __init__(self, dimmer):
        super().__init__()
        self.dimmer = dimmer
        self.title('Brightness Control')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)

        self.frame = ControlGui(self, self.dimmer, "backlight")
        self.frame.grid(row=0, column=0, padx=5, pady=5)

        self.frame2 = ControlGui(self, self.dimmer, "software")
        self.frame2.grid(row=1, column=0, padx=5, pady=5)


class ControlGui(customtkinter.CTkFrame):
    def __init__(self, parent, dimmer, function):
        super().__init__(parent)
        self.dimmer = dimmer
        self.monitors = dimmer.monitors
        self.link = False
        self.monitor2_connected = True
        self.monitor2_created = False

        if self.monitor2_connected:
            self.monitor2_create(self.monitors)

        # Monitor 1
        if 'intel' in self.monitors.keys():
            self.name1 =customtkinter.CTkLabel(self, text=self.monitors['intel'].type, width=70, anchor='center')
            self.name1.grid(row=0, column=0)

            initial_value = self.dimmer.monitors['intel'].actual_brightness_100

            self.label1 = customtkinter.CTkLabel(self, text=initial_value, width=40, anchor="center")
            self.label1.grid(row=0, column=1)

            self.scale1 = customtkinter.CTkSlider(self, to=100, command= lambda val: self.on_slide(val, self.monitors['intel'], self.label1), number_of_steps=100)
            self.scale1.set(initial_value)
            self.scale1.grid(row=0, column=2)

        # Function name
        self.function = customtkinter.CTkLabel(self, text=function, width=80, anchor="center")
        self.function.grid(row=0, column=3)

        self.switch2 = customtkinter.CTkSwitch(self, command=self.toggle_monitor2_connection, text="Connected")
        self.switch2.grid(row=1, column=4)
        

    def monitor2_create(self, monitors):
        # Monitor 2
        if 'display 1' in monitors.keys():

            self.monitor2_created = True
            self.name2 =customtkinter.CTkLabel(self, text=monitors['display 1'].type, width=70, anchor='center')
            self.name2.grid(row=1, column=0)

            initial_value = self.dimmer.monitors['display 1'].actual_brightness_100

            self.label2 = customtkinter.CTkLabel(self, text=initial_value, width=40, anchor="center")
            self.label2.grid(row=1, column=1)

            self.scale2 = customtkinter.CTkSlider(self, to=100, command= lambda val: self.on_slide(val, monitors['display 1'], self.label2), number_of_steps=100)
            self.scale2.set(initial_value)
            self.scale2.grid(row=1, column=2)
            
            # Link monitors
            self.switch = customtkinter.CTkSwitch(self, command=self.toggle_link, width=80, text="join")
            self.switch.grid(row=1, column=3)
    
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
        print(value, type(value), monitor.type)
        if self.link and self.monitor2_connected:
            self.label1.configure(text=value)
            self.label2.configure(text=value)
            self.scale2.set(value)
            # Update brightness of all monitors
            self.dimmer.slider_set(value/100)
        else:
            label.configure(text=value)
            # Update brightness of one monitors
            self.dimmer.slider_set(value/100, monitor)
    
    def toggle_link(self):
        self.link = not self.link
        print(self.link)
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
            print(self.monitor2_connected)
            if self.monitor2_connected:
                self.monitor2_show()
            else:
                self.monitor2_hide()
           


d = Dimmer()
gui = Gui(d)
gui.mainloop()