from setuptools import find_packages
from distutils.core import setup

with open('README.md') as f:
    ld = f.read()

setup(
    name='purepy',
    version='0.8.0',
    packages=find_packages(),
    license='MIT',
    description='Minor utilites for developing pure virtual classes.',
    long_description=ld,
    install_requires=[],
)
