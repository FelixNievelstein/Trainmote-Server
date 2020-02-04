from setuptools import setup
import atexit
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info

def _post_install():
    print('POST INSTALL')
    from subprocess import call
    call('sudo apt-get install bluetooth libbluetooth-dev', shell=True)
    call('mkdir content', shell=True)

class CustomInstallCommand(install):
    def run(self):                    
        install.run(self)
        _post_install()

class CustomDevelopCommand(develop):
    def run(self):                    
        develop.run(self)
        _post_install()

class CustomEggInfoCommand(egg_info):
    def run(self):                    
        egg_info.run(self)
        _post_install()

setup(
    name='trainmote-module',
    version='0.2',
    description='Application to create a bluetooth server to control a model train environment',
    author='Felix Nievelstein',
    author_email='app@felix-nievelstein.de',
    packages=['trainmote-module'],   
    install_requires=[
        'adafruit-circuitpython-ads1x15',
        'pybluez',
        'RPI.GPIO',
        'adafruit-blinka'
    ],
    python_requires='>=3, <4',
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
        'egg_info': CustomEggInfoCommand
    },
    project_urls={
        "Source Code": "https://github.com/FelixNievelstein/Trainmote-Server",
    },
)