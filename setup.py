from setuptools import setup
from distutils.command.install import install
from subprocess import call

def _post_install():
    print('POST INSTALL')
    call('sudo apt-get install bluetooth libbluetooth-dev', shell=True)
        call('mkdir content', shell=True)


class new_install(install):
    def __init__(self, *args, **kwargs):
        super(new_install, self).__init__(*args, **kwargs)
        atexit.register(_post_install)

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
    cmdclass={'install': new_install},
    project_urls={
        "Source Code": "https://github.com/FelixNievelstein/Trainmote-Server",
    },
)