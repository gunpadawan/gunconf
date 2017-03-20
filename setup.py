from setuptools import setup, find_packages
from codecs import open
from os import path
import gunconf

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gunconf',
    version=gunconf.__version__,

    description='Configuration utility for Aimtrak gun',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/gunpadawan/gunconf',

    # Author details
    author='gunpadawan',
    author_email='',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],

    packages=find_packages(),

    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['evdev>=0.6.4',
                      'pyusb>=1.0.0',
                      'pgu>=0.18',
                      'pyudev>=0.21'],

    dependency_links = [
     "https://github.com/gunpadawan/pgu/tarball/master#egg=pgu-0.18",
    ],

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'gunconf': ['data/theme/res/*',
                    'data/theme/SD/*',
                    'data/theme/HD/*']
    },
)
