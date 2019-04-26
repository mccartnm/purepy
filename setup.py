from setuptools import find_packages
from distutils.core import setup

with open('README.md') as f:
    ld = f.read()

setup(
    name='purepy',
    version='1.0.0',
    packages=['purepy'],
    license='MIT',
    description='Minor utilites for developing pure virtual classes.',
    author='Michael McCartney',
    long_description=ld,
    long_description_content_type="text/markdown",
    url = 'https://github.com/mccartnm/purepy',
    author_email='mccartneyworks@gmail.com',
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
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=[],
)
