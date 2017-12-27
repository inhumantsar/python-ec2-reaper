# -*- coding: utf-8 -*-

"""Top-level package for EC2 Reaper."""

import sys

__author__ = """Shaun Martin"""
__email__ = 'shaun@samsite.ca'
__version__ = '0.1.8'

if sys.version_info >= (3, 0):
    from ec2_reaper.ec2_reaper import reap
    from ec2_reaper.ec2_reaper import DEFAULT_TAG_MATCHER
    from ec2_reaper.ec2_reaper import DEFAULT_MIN_AGE
    from ec2_reaper.ec2_reaper import DEFAULT_REGIONS
    from ec2_reaper.ec2_reaper import LOCAL_TZ
    from ec2_reaper import aws_lambda
else:
    from ec2_reaper import reap
    from ec2_reaper import DEFAULT_TAG_MATCHER
    from ec2_reaper import DEFAULT_MIN_AGE
    from ec2_reaper import DEFAULT_REGIONS
    from ec2_reaper import LOCAL_TZ
    import aws_lambda
