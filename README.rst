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

AWS Permissions
~~~~~~~~~~~~~~~

Ensure your user or instance profile has the following permissions prior to running:

* ec2:TerminateInstances
* ec2:DescribeInstances
* ec2:DescribeRegions
* ec2:DescribeTags


Tag Matchers
~~~~~~~~~~~~

Matchers let you specify tag names, values to match (includes), and values to ignore (excludes). Wildcards can be used to either match all values (includes) or to match empty/non-existant tags (excludes).

This is the default tag matcher and it will match anything that lacks a *Name* tag:

.. code-block:: yaml

    [{"tag": "Name", "includes": [], "excludes": ["*"]}]

To terminate any instance named "cirunner", the filter would look like so:

.. code-block:: yaml

    [{"tag": "Name", "includes": ["cirunner"], "excludes": []}]


Python
~~~~~~

.. code-block:: python

    reap(tags=None, min_age=DEFAULT_MIN_AGE, regions=DEFAULT_REGIONS, debug=True)


* tags: List of dicts like :code:`{'tag': 'sometag', include=['val1', ...], exclude=['val2', ...]}`
* min_age: Instance must be (int)N seconds old before it will be considered for termination. Default: 300
* regions: Stringy AWS region name or list of names to search. Searches all available regions by default.
* debug: If True, perform dry-run by skipping terminate API calls. Default: True

Returns a list of dicts with instance that partially matches and their reap status.
eg: :code:`[{'id': i.id, 'tag_match': True, 'age_match': False, 'tags': i.tags, 'launch_time': i.launch_time, 'reaped': False, 'region': i.region}]`


CLI
~~~

.. code-block::

    ec2-reaper [--min-age <seconds>] [--region region-1 --region region-2 ...] [--dry-run] <tag matcher>

* *--dry-run* will enable debug output and prevent the reaper from actually terminating anything.
* The *Tag Matcher* has to be specified as a quoted JSON string.


AWS Lambda
~~~~~~~~~~

A stock handler is included with the module, so very little is needed to deploy it to AWS Lambda. Here's an example using the Serverless_ framework.

serverless.yml

.. code-block:: yaml
   :linenos:
   :caption: serverless.yml

    service: ec2-reaper

    frameworkVersion: ">=1.2.0 <2.0.0"

    provider:
      name: aws
      runtime: python3.6
      stage: prod
      region: us-west-2
      memorySize: 128
      timeout: 300
      environment:
        # enable debug logging and live NO-OP testing. default: true
        DEBUG: false

        # instances will not be terminated unless they are MIN_AGE seconds old
        # MIN_AGE: 300                      # default: 300

        # search *only* the specified regions. space separated string.
        # REGIONS: 'us-east-1 us-west-2'    # default: all regions

        # specify tag names, values to match (includes), and values to ignore (excludes)
        # wildcards can be used to either match all values (includes) or to
        # match empty/non-existant tags (excludes).
        # default: matches any instance that has an empty/non-existant Name tag.
        # TAG_MATCHER: '[{"tag": "Name", "includes": [], "excludes": ["*"]}]'

        # the function can report on instances terminated and instances which
        # match tag-wise but are too young to Slack. it uses the webhook defaults, so
        # be sure to configure it to your desired channel, bot name, etc.
        # default: no slack endpoint, no notifications
        SLACK_ENDPOINT: https://hooks.slack.com/services/M00...

      iamRoleStatements:
        # the function only needs a few specific permissions.
        - Effect: Allow
          Action:
            - ec2:TerminateInstances
            - ec2:DescribeInstances
            - ec2:DescribeRegions
            - ec2:DescribeTags
          Resource: "*"

    functions:
      cron:
        handler: handler.run
        events:
          # Invoke Lambda function every 15th minute from Mon-Fri
          - schedule: cron(0/15 * ? * MON-FRI *)


    plugins:
      # takes care of bundling python requirements for us.
      - serverless-python-requirements

handler.py

.. code-block:: python
   :linenos:
   :caption: handler.py

    import ec2_reaper

    def run(event, context):
        return ec2_reaper.aws_lambda.handler(event, context)


requirements.txt

.. code-block::
   :caption: requirements.txt

   ec2-reaper>=0.1.8


Deploy

.. code-block::

    sudo npm install -g serverless
    cd /path/to/lambda-reaper-repo
    serverless deploy



Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _Serverless: https://serverless.com/
