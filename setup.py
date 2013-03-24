"""
Setup script for PyPi
"""
from setuptools import setup, find_packages


setup(name='dynamic-dynamodb',
    version='0.1.0',
    license='Apache License, Version 2.0',
    description='Automatic provisioning for AWS DynamoDB tables',
    author='Sebastian Dahlgren',
    author_email='sebastian.dahlgren@gmail.com',
    url='http://sebdah.github.com/dynamic-dynamodb/',
    keywords="dynamodb aws provisioning amazon web services",
    platforms=['Any'],
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    install_requires=[
        'boto >= 2.6.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],
    entry_points={
        'console_scripts': [
            'dynamic-dynamodb = dynamic_dynamodb.dynamic_dynamodb:main',
        ]
    }
)
