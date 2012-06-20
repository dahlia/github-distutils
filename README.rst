github-distutils
================

Intro
-----

Distribute_/setuptools_/distutils_ command for GitHub_. You can use
GitHub downloads instead of PyPI_ downloads for release.

To use this, follow the instruction.

.. _Distribute: http://packages.python.org/distribute/
.. _setuptools: http://pypi.python.org/pypi/setuptools
.. _distutils: http://docs.python.org/library/distutils.html
.. _GitHub: https://github.com/
.. _PyPI: http://pypi.python.org/


Instruction
-----------

First of all your software must be packaged within the standard distribution
way: use distutils_, Distribute_ or setuptools_.  This package contains
an extension command for that.

Then, add this package into ``setup_requires`` parameter of your ``setup()``
configuration (of ``setup.py`` script)::

    setup(name='YourPackageName',
          version='1.2.3',
          ...,
          setup_requires=['github-distutils >= 0.1.0'])

Now there will be ``github_upload`` command for your ``setup.py``::

    $ python setup.py github_upload --help
    Common commands: (see '--help-commands' for more)

    ...

    Options for 'github_upload' command:
      --repository (-R)  GitHub repository name e.g. user/reponame
      --username (-u)    GitHub username
      --password (-p)    GitHub password

    ...

If ``-u``/``--username`` and ``-p``/``--password`` are not present, it will
shows the prompt.  ``-R``/``--repository`` is required.


Upload
------

Upload is very easy::

    $ python setup.py sdist github_upload -R user/reponame register

By explained:

``sdist``
    Makes the source distribution file.  If your package name is
    ``YourPackageName`` and its version is ``1.2.3``, and then its file name
    becomes ``YourPackageName-1.2.3.tar.gz``.

``github_upload -R user/reponame``
    Uploads the built source distribution file into your GitHub repository.
    It does not mean that it will be version-controlled, but it will be simply
    uploaded to its downloads page.

``register``
    Using the GitHub download URL registers the package of this version
    into PyPI.
    The URL of PyPI page will be http://pypi.python.org/YourPackageName/1.2.3


Defaulting options
------------------

You can make default values for these options by specifying in the ``setup.cfg``
configuration file.  For example, if you want to default ``--repository``,
make ``setup.cfg`` file like (hyphens becomes underscores)::

    [upload]
    repository = user/reponame

You can make a shorthand alias as well::

    [aliases]
    release = sdist github_upload register


Author and license
------------------

It is distributed under Public Domain.  Just do what you want to do with this.
Written by `Hong Minhee`__.

You can checkout the source code from its `GitHub repository`__::

    $ git clone git://github.com/dahlia/github-distutils.git

If you found a bug, please report it to the `issue tracker`__.

__ http://dahlia.kr/
__ https://github.com/dahlia/github-distutils
__ https://github.com/dahlia/github-distutils/issues


For Bitbucket users
-------------------

Use bitbucket-distutils_ which is a package by the same author
if you are using Bitbucket instead of GitHub.

.. _bitbucket-distutils: https://bitbucket.org/dahlia/bitbucket-distutils


Changelog
---------

Version 0.1.1
'''''''''''''

Released on June 20, 2012.  Beta version.

- Allow upper cases for GitHub repository names.
  [`#1`__ by Xavier Barbosa]
- Windows compatibility: fixed ``UnicodeDecodeError`` for uploads.

__ https://github.com/dahlia/github-distutils/pull/1


Version 0.1.0
'''''''''''''

Released on May 27, 2012.  First alpha version.
