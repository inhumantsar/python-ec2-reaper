# -*- coding: utf-8 -*-

"""Top-level package for EC2 Reaper."""

import sys

__author__ = """Shaun Martin"""
__email__ = 'shaun@samsite.ca'
__version__ = '0.1.3'

if sys.version_info >= (3, 0):
    import ec2_reaper
else:
    from ec2_reaper import reap
