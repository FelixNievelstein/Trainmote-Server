

# TRAINMOTE SERVER #


## Install Trainmote server ##

First to install the Trainmote Module open the terminal and perform:

```
sudo pip3 install trainmote-module-felix-nievelstein-de
````
Next you have to activate I2C in your raspberry pi configurations. Herefore go to settings of your raspberry pi and select interfaces. Here activate the I2C interface.

Great you are now ready to start the trainmote server with:
```
sudo trainmote --autostart
````
If you use the option '--autostart' the trainmote server will start automatically on rasperry pi start.

# NOTE:
Project based on python3. Therefor you have to use pip3.
