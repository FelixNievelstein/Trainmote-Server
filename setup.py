import setuptools
import atexit
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from distutils.core import Extension, setup

with open("README.MD", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='trainmote-module_felix-nievelstein_de',
    version='0.2.93',
    description='Application to create a bluetooth server to control a model train environment',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/FelixNievelstein/Trainmote-Server",
    author='Felix Nievelstein',
    author_email='app@felix-nievelstein.de',
    package_dir={'': 'src'},
    #ext_modules=[Extension('bluetooth._bluetooth',
     #                libraries = ['bluetooth'],
      #               #extra_compile_args=['-O0'],
       #              sources = ['bluez/btmodule.c', 'bluez/btsdp.c'])],
    packages=['pkg_trainmote', 'pkg_trainmote.models'],
    package_data={
        "pkg_trainmote": ["scripts/*.sh"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux"
    ],
    install_requires=[
        'adafruit-circuitpython-ads1x15',
        'pybluez',
        'RPI.GPIO',
        'adafruit-blinka'
    ],
    entry_points={
        'console_scripts': [
            'trainmote = pkg_trainmote.bluetoothservice:main',
        ]
    },
    python_requires='>=3, <4',
    data_files=[('content/', [])]
)