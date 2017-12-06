#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ec2_reaper` package."""

import pytest
import boto3
import time

from moto import mock_ec2
from click.testing import CliRunner

from ec2_reaper import ec2_reaper
from ec2_reaper import cli


import logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)

logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string

@mock_ec2
def _launch_instances(tags=None):
    '''
    tags must be in `[{'Key':'somekey', 'Value': 'someval'}, ...]` format
    '''
    ami_id = 'ami-1234abcd'
    client = boto3.client('ec2', region_name='us-west-1')
    instance = client.run_instances(ImageId=ami_id, MinCount=1, MaxCount=1)['Instances'][0]

    log.debug('launching instance: {}'.format(instance))

    # bad_states = ['shutting-down', 'terminated', 'stopping', 'stopped']
    # s = 0
    # while instance['State']['Name'] != u'running':
    #     log.debug('Instance not alive yet (seconds waited: {}. state: {}), sleeping...'.format(s, instance['State']['Name']))
    #     time.sleep(0.5)
    #     s += 0.5
    #     if instance['State']['Name'] in bad_states:
    #         raise Exception('Test instance entered a bad state.')

    if tags:
        log.debug('creating tags: {}'.format(tags))
        instance.create_tags(Tags=tags)




def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' in help_result.output

@mock_ec2
def test_default_with_instances():
    ### test with mock instances and defaults
    runner = CliRunner()
    _launch_instances()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0

@mock_ec2
def test_default_without_instances():
    ### test with mock instances and defaults
    runner = CliRunner()
    # _launch_instances()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
