from setuptools import setup

setup(
    name='trainmote-module',
    packages=['trainmote-module'],
    entry_points={
        'console_scripts' : [
            'startTrainmote = trainmote-module.bluetoothservice',
        ]
    },
    install_requires=[
        'adafruit-circuitpython-ads1x15',
        'bluetooth libbluetooth-dev',
        'pybluez',
        'RPI.GPIO',
        'adafruit-blinka'
    ]
)