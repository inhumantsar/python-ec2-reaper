# -*- coding: utf-8 -*-

"""Top-level package for EC2 Reaper."""

import sys

__author__ = """Shaun Martin"""
__email__ = 'shaun@samsite.ca'
__version__ = '0.1.3'

if sys.version_info >= (3, 0):
    from ec2_reaper.ec2_reaper import reap
    from ec2_reaper.ec2_reaper import DEFAULT_TAG_MATCHER
else:
    from ec2_reaper import reap
    from ec2_reaper import DEFAULT_TAG_MATCHER
