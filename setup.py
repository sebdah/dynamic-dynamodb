""" Setup script for PyPI """
from setuptools import setup


setup(
    name='dynamic-dynamodb',
    version='1.6.0',
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
    install_requires=[
        'boto >= 2.6.0',
        'requests >= 0.14.1'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)
