import os
import re

from setuptools import setup

GITHUB_URL = 'https://github.com/Turbo87/aerofiles/'


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


def read_markdown(*paths):
    content = read(*paths)

    # Change relative links to github links
    content = re.sub(r'\]\(([^(http)])',
                     '](' + GITHUB_URL + r'blob/master/\1', content)

    # Strip images
    content = re.sub(r'!\[([^\[\]\(\)]+)\]\([^\[\]\(\)]+\)', r'\1', content)

    # Convert to rST if pypandoc available
    try:
        import pypandoc
        return pypandoc.convert(content, 'rst', format='md')
    except (IOError, ImportError):
        return content


setup(
    name='aerofiles',
    version='0.1.0',
    description=(
        'waypoint, task and tracklog file readers and writers for aviators'
    ),
    long_description=read_markdown('README.md'),
    url=GITHUB_URL,
    license='MIT',
    author='Tobias Bieniek',
    author_email='tobias.bieniek@gmx.de',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    packages=['aerofiles'],
)
