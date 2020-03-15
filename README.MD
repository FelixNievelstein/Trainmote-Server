

# TRAINMOTE SERVER #


## Install Trainmote server ##
- Install git 
- git clone
- mkdir content
- sudo pip3 install adafruit-circuitpython-ads1x15
- sudo apt-get install bluetooth libbluetooth-dev
- sudo python3 -m pip install pybluez
- pip3 install RPI.GPIO
- pip3 install adafruit-blinka
- Edit /lib/systemd/system/bluetooth.service and add '-C' after 'bluetoothd'. Reboot.

# NOTE:
Project based on python3. Always start project with python3. 
