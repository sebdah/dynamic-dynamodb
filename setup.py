""" Setup script for PyPI """
import os
import sys
from setuptools import setup
from ConfigParser import SafeConfigParser

settings = SafeConfigParser()
settings.read(os.path.realpath('dynamic_dynamodb/dynamic-dynamodb.conf'))


def return_requires():
    install_requires = [
        'boto >= 2.29.1',
        'requests >= 0.14.1',
        'logutils >= 0.3.3',
        'retrying >= 1.3.3'
    ]
    if sys.version_info < (2, 7):
        install_requires.append('argparse >= 1.4.0')
        install_requires.append('ordereddict >= 1.1')
    return install_requires

setup(
    name='dynamic-dynamodb',
    version=settings.get('general', 'version'),
    license='Apache License, Version 2.0',
    description='Automatic provisioning for AWS DynamoDB tables',
    author='Sebastian Dahlgren',
    author_email='sebastian.dahlgren@gmail.com',
    url='http://sebdah.github.com/dynamic-dynamodb/',
    keywords="dynamodb aws provisioning amazon web services",
    platforms=['Any'],
    packages=['dynamic_dynamodb'],
    scripts=['dynamic-dynamodb'],
    include_package_data=True,
    zip_safe=False,
    install_requires=return_requires(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)
