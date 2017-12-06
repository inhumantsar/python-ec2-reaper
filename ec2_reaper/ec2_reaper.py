# -*- coding: utf-8 -*-
import boto3
import logging
import pytz
import os
import datetime
import time

"""EC2 Reaper"""

# set up localtime for logging
LOCAL_TZ_NAME = os.environ.get('LOCAL_TZ_NAME', None)
if not LOCAL_TZ_NAME:
    LOCAL_TZ = pytz.timezone(time.tzname[time.localtime().tm_isdst])
    LOCAL_TZ_NAME = LOCAL_TZ.tzname(datetime.datetime.now())
else:
    LOCAL_TZ = pytz.timezone(LOCAL_TZ_NAME)

log = logging.getLogger()

def reap(tags, min_age=300, regions=None, debug=True):
    """reap - Terminate running instances matching tag requirements and a minimum age

    tags: List of dicts like `{'tag': 'sometag', include=['val1', ...], exclude=['val2', ...]}`
    min_age: Instance must be (int)N seconds old before it will be considered for termination. Default: 300
    regions: Stringy AWS region name or list of names to search. Searches all available regions by default.
    debug: If True, perform dry-run by skipping terminate API calls. Default: True

    Behaviour:
    - An instance is reaped if tag value is in the include list
    - An instance is ignored if tag value is in the exclude list
    - Exclude overrides Include
    - `['*']` will match any value except empty for tag
    - Empty lists will match empty and missing tags.
        - eg: `{tag='Name', include=[], exclude=['*']}` will reap any instance without a 'Name' tag.
    - Instances must match *all* tag conditions if multiple are specified.
    - Stopped instances are always ignored.
    """
    reaped = []

    regions = regions if regions else tuple(r['RegionName'] for r in boto3.client('ec2', region_name='us-east-1').describe_regions().get('Regions'))
    if isinstance(regions, str):
        regions = tuple(regions)

    old_log_level = None
    if debug and logging.getLevelName(log.level) != 'DEBUG':
        old_log_level = log.level
        log.setLevel(logging.DEBUG)

    for region in regions:
        ec2 = boto3.resource('ec2', region_name=region)
        instances = [i for i in ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])]
        log.debug('Found {} instances in {}'.format(len(instances), region))
        for i in instances:
            local_time = i.launch_time.astimezone(LOCAL_TZ)
            log.debug('Checking {}, launched at {} with tags: {}'.format(
                i.id, local_time, i.tags))
            ct, ca = (_check_tags(i.tags, tags), _check_age(i.launch_time, min_age))

            if ct and not ca:
                log.warning('The following instance is a match, but isn\'t old enough yet: {} (launched at {} with tags: {})'.format(i.id, local_time, i.tags))
                continue

            if ct and ca:
                msg = '(NO-OP) ' if debug else ''
                msg += 'Reaping instance {} launched at {} {}'.format(i.id, local_time, LOCAL_TZ_NAME)
                log.warning(msg)
                if not debug:
                    i.terminate()
                reaped.append(i)
                continue

    if old_log_level:
        log.setLevel(old_log_level)

def _check_tags(instance_tags, matching_tags):
    log.debug('Comparing instance tags {} to filters {}'.format(
    instance_tags, matching_tags))
    instance_tags = instance_tags if instance_tags else []
    for mt in matching_tags:
        # reap if `tag` is not present and excludes == ['*']
        # eg: {tag: Name, excludes: ['*']}. If it has a Name, don't reap it.
        if mt.get('excludes') == ['*'] and mt.get('tag') not in [i['Key'] for i in instance_tags]:
            log.debug('Tag "{}" not present; instance is reapable.')
            return True

        # check instance tags
        for it in instance_tags:
            if it.get('Key') != mt.get('tag'):
                continue

            # matching reapme tag exists and is not empty
            if mt.get('includes') == ['*'] and it.get('Value'):
                log.debug('Tag "{}" is present and `include` is wildcarded; instance is reapable.')
                return True

            # tag exists, matches a value in includes, doesn't match any excludes
            if it.get('Value') in mt.get('includes') and it.get('Value') not in mt.get('excludes'):
                log.debug('Tag "{}" present, its value is in `includes` and not in `excludes`; instance is reapable.')
                return True
    return False

def _check_age(launch_time, min_age):
    # get local timezone info to compare against utc
    min_age_dt = datetime.datetime.now() - datetime.timedelta(seconds=min_age)
    min_age_dt = min_age_dt.replace(tzinfo=LOCAL_TZ)
    if launch_time < min_age_dt:
        log.debug('')
        return True
    else:
        return False
