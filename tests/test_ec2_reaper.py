#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ec2_reaper` package."""

import pytest
import boto3
import sys
import time
from datetime import datetime, timedelta

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
    client = boto3.client('ec2', region_name='us-west-2')
    params = {'ImageId': ami_id, 'MinCount': 1, 'MaxCount': 1}
    if tags:
        params['TagSpecifications'] = [{'ResourceType': 'instance', 'Tags': tags}]
    instance = client.run_instances(**params)['Instances'][0]

    instance['State']['Code'] = 16
    instance['State']['Name'] = 'running'

    instance = boto3.resource('ec2', region_name='us-west-2').Instance(instance[u'InstanceId'])
    if tags:
        log.debug('creating tags: {}'.format(tags))
        instance.create_tags(Tags=tags)

    log.debug('launched instance: {}'.format(instance))


def test_cli_help():
    """Test the CLI Help."""
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' in help_result.output

@mock_ec2
def test_cli_min_age():
    ### test with mock instances and defaults
    runner = CliRunner()
    _launch_instances()
    time.sleep(6)
    result = runner.invoke(cli.main, ['-d', '--min-age', '5'])
    assert result.exit_code == 0

@mock_ec2
def test_cli_tagstr():
    ### test with mock instances and defaults
    runner = CliRunner()
    _launch_instances(tags=[{'Key': 'Name', 'Value': 'somename'}])
    time.sleep(6)
    result = runner.invoke(cli.main, ['-d', '--min-age', '5', '[{"tag": "Name", "includes": ["somename"], "excludes": []}]'])
    assert result.exit_code == 0

@mock_ec2
def test_cli_allregions():
    """Test the CLI Help."""
    runner = CliRunner()
    runner = CliRunner()
    _launch_instances(tags=[{'Key': 'Name', 'Value': 'somename'}])
    time.sleep(6)
    result = runner.invoke(cli.main, ['-d', '--min-age', '5'])
    assert result.exit_code == 0

@mock_ec2
def test_cli_oneregion():
    """Test the CLI Help."""
    runner = CliRunner()
    _launch_instances(tags=[{'Key': 'Name', 'Value': 'somename'}])
    time.sleep(6)
    # instance launches into us-west-2
    result = runner.invoke(cli.main, ['-d', '--min-age', '5', '-r', 'us-east-1'])
    assert result.exit_code > 0

@mock_ec2
def test_cli_tworegions():
    """Test the CLI Help."""
    runner = CliRunner()
    _launch_instances(tags=[{'Key': 'Name', 'Value': 'somename'}])
    time.sleep(6)
    result = runner.invoke(cli.main, ['-d', '--min-age', '5', '-r', 'us-east-1', '-r', 'us-west-2'])
    assert result.exit_code == 0

@mock_ec2
def test_nomatch_tag_nomatch_age():
    ### test with mock instances and defaults
    _launch_instances(tags=[{'Key':'Name', 'Value': 'somename'}])
    reaperlog = ec2_reaper.reap()
    assert len(reaperlog) == 0

@mock_ec2
def test_match_tag_nomatch_age():
    ### test with mock instances and defaults
    _launch_instances()
    reaperlog = ec2_reaper.reap()
    assert len(reaperlog) == 1
    assert reaperlog[0]['tag_match']
    assert not reaperlog[0]['age_match']
    assert not reaperlog[0]['reaped']

@mock_ec2
def test_match_tag_includes():
    ### test with mock instances and defaults
    _launch_instances(tags=[{'Key':'Name', 'Value': 'somename'}])
    reaperlog = ec2_reaper.reap(tags=[{'tag':'Name', 'includes': ['somename'], 'excludes': ['*']}])
    assert len(reaperlog) == 1
    assert reaperlog[0]['tag_match']
    assert not reaperlog[0]['age_match']
    assert not reaperlog[0]['reaped']

@mock_ec2
def test_nomatch_tag_excludes():
    ### test with mock instances and defaults
    _launch_instances(tags=[{'Key':'Name', 'Value': 'somename'}])
    time.sleep(6)
    reaperlog = ec2_reaper.reap(min_age=5, tags=[{'tag':'Name',
                                                  'includes': ['nothingotmatch'],
                                                  'excludes': ['somename']}])
    assert len(reaperlog) == 1
    assert not reaperlog[0]['tag_match']
    assert reaperlog[0]['age_match']
    assert not reaperlog[0]['reaped']

@mock_ec2
def test_nomatch_tag_match_age():
    ### test with mock instances and defaults
    _launch_instances(tags=[{'Key':'Name', 'Value': 'somename'}])
    time.sleep(6)
    reaperlog = ec2_reaper.reap(min_age=5)
    assert len(reaperlog) == 1
    assert not reaperlog[0]['tag_match']
    assert reaperlog[0]['age_match']
    assert not reaperlog[0]['reaped']

@mock_ec2
def test_match_tag_match_age():
    ### test with mock instances and defaults
    _launch_instances()
    time.sleep(6)
    reaperlog = ec2_reaper.reap(min_age=5)
    assert len(reaperlog) == 1
    assert reaperlog[0]['tag_match']
    assert reaperlog[0]['age_match']
    assert reaperlog[0]['reaped']
