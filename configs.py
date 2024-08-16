import json

# Hardcoded defaults
DEFAULT_CONFIG = {
    "dont_change_screen" : [],
    "link_sliders": False,
    "link_sliders2": True,
    "transparency": 87,
    "actual_brightness_path": "/sys/class/backlight/intel_backlight/actual_brightness",
    "min_brightness": 0.20,
    "max_brightness": 1.00
}

class Config:
    def __init__(self):
        self.load_config()
        
    # Function to load and merge configurations
    def load_config(self):
        try:
            with open("user_config.json", "r") as f:
                user_config = json.load(f)
        except FileNotFoundError:
            user_config = {}

        # Merge user config over default config
        config = {**DEFAULT_CONFIG, **user_config}
        config["min_brightness"] =min(config["min_brightness"], config["max_brightness"]) 

        for k,v in config.items():
            setattr(self, k.upper(), v)
        

# Load the configuration
config = Config()


