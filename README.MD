

# TRAINMOTE SERVER #


## Install Trainmote server ##

First to install the Trainmote Module open the terminal and perform:

```
sudo pip3 install trainmote-module-felix-nievelstein-de
````

Next you have to setup the bluetooth settings of your raspberry pi. To do this, run the following command to open the editor nano.
```
sudo nano /lib/systemd/system/bluetooth.service
```
Now add '-C' after 'ExecStart=/usr/lib/bluetooth/bluetoothd' and restart the raspberry pi.

Great you are now ready to start the trainmote server with_
```
sudo trainmote
````

# NOTE:
Project based on python3. Therefor you have to use pip3.
