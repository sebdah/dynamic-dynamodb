""" Setup script for PyPI """
from setuptools import setup, find_packages


setup(name='dynamic-dynamodb',
    version='0.3.0-SNAPSHOT',
    license='Apache License, Version 2.0',
    description='Automatic provisioning for AWS DynamoDB tables',
    author='Sebastian Dahlgren',
    author_email='sebastian.dahlgren@gmail.com',
    url='http://sebdah.github.com/dynamic-dynamodb/',
    keywords="dynamodb aws provisioning amazon web services",
    platforms=['Any'],
    py_modules=['dynamic_dynamodb'],
    packages=find_packages('dynamic_dynamodb'),
    include_package_data=True,
    zip_safe=False,
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
            'dynamic-dynamodb = dynamic_dynamodb.main:main',
        ]
    }
)
