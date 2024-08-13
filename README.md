sudo apt install brightnessctl
sudo chmod u+s /usr/bin/brightnessctl                         07:45:25


sudo apt install ddcutil

ddcutil detect

**
The EACCES(13): Permission denied errors indicate that your user does not have permission to access the /dev/i2c-* devices, which are needed for tools like ddcutil to communicate with the monitor.

Steps to resolve the permission issue:
Check if your user is in the i2c group:

First, check if the i2c group exists on your system:
bash
Copy code
getent group i2c
If the group exists, add your user to the i2c group:
bash
Copy code
sudo usermod -aG i2c $USER
After adding yourself to the group, log out and log back in or reboot your system.
If the i2c group does not exist:

You can create the i2c group and then add yourself to it:
bash
Copy code
sudo groupadd i2c
sudo usermod -aG i2c $USER
Then, set the correct permissions for the /dev/i2c-* devices:
bash
Copy code
sudo chown root:i2c /dev/i2c-*
sudo chmod 660 /dev/i2c-*
***


ddcutil --display 1 getvcp 10
ddcutil --display 1 setvcp 10 70
