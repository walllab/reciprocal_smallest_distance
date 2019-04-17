
# try using distribute or setuptools or distutils.
try:
    import distribute_setup
    distribute_setup.use_setuptools()
except:
    pass

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import sys
import re

# parse version from package/module without importing or evaluating the code
with open('rsd/rsd.py') as fh:
    for line in fh:
        m = re.search(r"^__version__ = '(?P<version>[^']+)'$", line)
        if m:
            version = m.group('version')
            break

if sys.version_info <= (2, 6):
    sys.stderr.write("ERROR: rsd requires Python Version 2.7 or above...exiting.\n")
    sys.exit(1)

setup(
    name = "reciprocal_smallest_distance",
    version = version,
    author = "Todd F. DeLuca, Dennis P. Wall",
    author_email = "todd_deluca@hms.harvard.edu",
    description = "Reciprocal Smallest Distance (RSD) finds pairwise orthologous genes using global sequence alignment and maximum likelihood evolutionary distance estimates.",
    license = "MIT",
    keywords = "genome ortholog algorithm",
    platforms = "Posix; MacOS X",
    url = "https://github.com/todddeluca/reciprocal_smallest_distance",   # project home page, if any
    download_url = "https://github.com/todddeluca/reciprocal_smallest_distance/downloads",
    scripts = ['bin/rsd_search', 'bin/rsd_format', 'bin/rsd_blast'],
    packages = ['rsd'],
    package_data = {
        'rsd': ['*.ctl', '*.dat'],
        },
    test_suite='tests.test_search.TestSearch',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        ],
    )
