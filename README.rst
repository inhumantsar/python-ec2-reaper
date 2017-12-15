==========
EC2 Reaper
==========


.. image:: https://img.shields.io/pypi/v/ec2-reaper.svg
        :target: https://pypi.python.org/pypi/ec2-reaper

.. image:: https://img.shields.io/travis/inhumantsar/python-ec2-reaper.svg
        :target: https://travis-ci.org/inhumantsar/python-ec2-reaper

.. image:: https://pyup.io/repos/github/inhumantsar/python-ec2-reaper/shield.svg
     :target: https://pyup.io/repos/github/inhumantsar/python-ec2-reaper/
     :alt: Updates


CLI & module for terminating instances that match tag and age requirements.

Features
---------

* Searches all (or specified) regions for instances.
* Matches instances against a tag pattern.
* Allows instances a grace period before termination.
* Can be used as a Python module, CLI application, or an AWS Lambda function

Usage
---------

Tag Matchers
~~~~~~~~~~~~

`[{"tag": "Name", "includes": [], "excludes": ["*"]}]`

This is the default tag matcher and it will match anything that lacks a `Name` tag.

To terminate any instance named "cirunner", the filter would look like so:

`[{"tag": "Name", "includes": ["cirunner"], "excludes": []}]`

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
