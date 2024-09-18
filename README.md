GUI to control monitor brightness in Linux. Capable of adjusting the brightness of both laptop and external monitors. It uses software (`xrandr`) and hardware (`ddcutil`) for control.
It's possible to synk the backlight brightness changes.

## Requirements
`sudo apt install brightnessctl`

`sudo chmod u+s /usr/bin/brightnessctl`


`sudo apt install ddcutil`

`ddcutil detect`


### Autostart
`cp dimmer.desktop ~/.config/autostart/dimmer.desktop`


## Errors
### Running program
Error: Namespace AyatanaAppIndicator3 not available:
    `export PYSTRAY_BACKEND=gtk`


### `ddcutil`

The EACCES(13): Permission denied errors indicate that your user does not have permission to access the /dev/i2c-* devices, which are needed for tools like `ddcutil` to communicate with the monitor.

Steps to resolve the permission issue:
Check if your user is in the i2c group:

- First, check if the i2c group exists on your system:

    `getent group i2c`
- If the group exists, add your user to the i2c group:

    `sudo usermod -aG i2c $USER`

- After adding yourself to the group, log out and log back in or reboot your system.
If the i2c group does not exist:

    You can create the i2c group and then add yourself to it:

    `sudo groupadd i2c`

    `sudo usermod -aG i2c $USER`

- Then, set the correct permissions for the /dev/i2c-* devices:

    `sudo chown root:i2c /dev/i2c-*`

    `sudo chmod 660 /dev/i2c-*`
***
