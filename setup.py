import os
import re

from setuptools import setup, find_packages

about = {}
with open("aerofiles/__about__.py") as fp:
    exec(fp.read(), about)


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


def read_markdown(*paths):
    content = read(*paths)

    # Change relative links to github links
    content = re.sub(r'\]\(([^(http)])',
                     '](' + about['__uri__'] + r'blob/master/\1', content)

    # Strip images
    content = re.sub(r'!\[([^\[\]\(\)]+)\]\([^\[\]\(\)]+\)', r'\1', content)

    # Convert to rST if pypandoc available
    try:
        import pypandoc
        return pypandoc.convert(content, 'rst', format='md')
    except (IOError, ImportError):
        return content


setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__summary__'],
    long_description=read_markdown('README.md'),
    url=about['__uri__'],
    license=about['__license__'],
    author=about['__author__'],
    author_email=about['__email__'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    packages=find_packages(exclude=['tests*']),
)
