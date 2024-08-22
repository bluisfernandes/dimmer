from monitors import MonitorInt, MonitorExt
import subprocess

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

    def slider_set(self, value, monitor=None):
        if monitor:
            if isinstance(monitor,str):
                monitor = self.monitors.get(monitor)
            monitor.set(value)
        elif self.linked is True:
            for _, monitor in self.monitors.items():
                monitor.set(value)