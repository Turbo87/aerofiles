import os

from setuptools import find_packages, setup

GITHUB_URL = 'https://github.com/Turbo87/aerofiles/'


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(
    name='aerofiles',
    version='1.5.0',
    description='waypoint, task, tracklog readers and writers for aviation',
    long_description=read('README.rst'),
    url=GITHUB_URL,
    license='MIT',
    author='Tobias Bieniek',
    author_email='tobias.bieniek@gmx.de',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    packages=find_packages(exclude=['tests*']),
)
