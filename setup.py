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
    author='Michael McCartney',
    long_description=ld,
    keywords=[
        'preprocess',
        'functions',
        'pure',
        'virtual',
        'metaclass',
        'abstract'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developments',
        'Topic :: Software Development :: Utility',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    install_requires=[],
)
