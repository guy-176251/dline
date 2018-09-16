# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='dline',
    version='2.0.0',
    description='A feature-rich terminal discord client',
    long_description=readme,
    author='Nat Osaka',
    author_email='natthetupper@gmail.com',
    url='https://github.com/NatTupper/dline',
    license=license,
    packages=[
        'dline', 'dline.client', 'dline.commands',
        'dline.input', 'dline.ui', 'dline.utils'
    ],
    entry_points={
        'console_scripts': ['dline=dline.__main__:main']
    },
    include_package_data=True,
    zip_safe=False
)
