from __future__ import with_statement

import os.path
import sys
import warnings
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from github_distutils import (__author__, __email__, __license__,
                              __url__, __version__, commands)


requires = []

if sys.version_info < (2, 6, 0):
    requires.append('simplejson')


def readme():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
            return f.read()
    except (IOError, OSError):
        return ''


warnings.warn('''
This project is abandoned, and we recommend not to use this anymore. \
Because PyPI and pip disallows to download package distributions \
from other than official PyPI for security reasons.\
''', DeprecationWarning)


setup(name='github-distutils',
      description='Distribute/setuptools/distutils command for GitHub. '
                  'You can use GitHub downloads instead of PyPI downloads '
                  'for release.',
      version=__version__,
      long_description=readme(),
      py_modules=['github_distutils'],
      zip_safe=True,
      author=__author__,
      author_email=__email__,
      url=__url__,
      license=__license__,
      install_requires=requires,
      setup_requires=requires,
      cmdclass=commands,
      entry_points={'distutils.commands': [
          'github_upload = github_distutils:github_upload'
      ]},
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Framework :: Setuptools Plugin',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'Topic :: System :: Software Distribution'
      ])
