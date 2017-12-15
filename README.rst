==========
EC2 Reaper
==========


.. image:: https://img.shields.io/pypi/v/ec2-reaper.svg
        :target: https://pypi.python.org/pypi/ec2-reaper

.. image:: https://img.shields.io/travis/inhumantsar/python-ec2-reaper.svg
        :target: https://travis-ci.org/inhumantsar/python-ec2-reaper

.. image:: https://pyup.io/repos/github/inhumantsar/ec2_reaper/shield.svg
     :target: https://pyup.io/repos/github/inhumantsar/ec2_reaper/
     :alt: Updates


CLI & module for terminating instances that match tag and age requirements.


* Free software: BSD license
* Documentation: https://ec2-reaper.readthedocs.io.

Testing
---------

    docker run --rm -it -w /workspace -v $(pwd):/workspace python:2 /bin/bash
    $ pip install -r requirements.txt -r requirements_dev.txt
    $ tox -e py27

Features
---------

* TODO

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
