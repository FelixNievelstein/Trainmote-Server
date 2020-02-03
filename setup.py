from setuptools import setup

setup(
    name='trainmote-module',
    packages=['trainmote-module'],   
    install_requires=[
        'adafruit-circuitpython-ads1x15',
        'pybluez',
        'RPI.GPIO',
        'adafruit-blinka'
    ]
)