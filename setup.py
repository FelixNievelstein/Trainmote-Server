from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        check_call("apt-get install bluetooth libbluetooth-dev".split())
        check_call("mkdir content".split())
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        develop.run(self)

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        check_call("apt-get install bluetooth libbluetooth-dev".split())
        check_call("mkdir content".split())        
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        install.run(self)

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
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
    project_urls={
        "Source Code": "https://github.com/FelixNievelstein/Trainmote-Server",
    },
)