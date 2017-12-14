from datetime import datetime, timedelta
import logging
import requests
import os
import sys
import json
import pytz

import ec2_reaper
from ec2_reaper import reap

def _is_py3():
    return sys.version_info >= (3, 0)

log = logging.getLogger(__name__)

DEFAULT_SLACK_ENDPOINT = ''

MIN_AGE = os.environ.get('MIN_AGE', ec2_reaper.DEFAULT_MIN_AGE)
REGIONS = os.environ.get('REGIONS', ec2_reaper.DEFAULT_REGIONS)
REGIONS = REGIONS.split(' ') if isinstance(REGIONS, str) else REGIONS

strclasses = str if _is_py3() else (str, unicode)
TAG_MATCHER = os.environ.get('TAG_MATCHER', ec2_reaper.DEFAULT_TAG_MATCHER)
TAG_MATCHER = json.loads(TAG_MATCHER) if isinstance(TAG_MATCHER, strclasses) else TAG_MATCHER

SLACK_ENDPOINT = os.environ.get('SLACK_ENDPOINT', None)

DEBUG = os.environ.get('DEBUG', False)
if DEBUG:
    log.setLevel(logging.DEBUG)
    logging.getLogger('botocore').setLevel(logging.INFO)
    logging.getLogger('boto3').setLevel(logging.INFO)
else:
    log.setLevel(logging.INFO)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('boto3').setLevel(logging.WARNING)

# this is necessary because tz-aware dts aren't JSON serializable by default
class DateTimeJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

def _respond(body, error=True, headers=None, status_code=500):
    o = {'statusCode': status_code, 'body': body}
    if headers:
        o['headers'] = headers
    return json.dumps(o, cls=DateTimeJSONEncoder)

def _get_expires(launch_time, min_age=MIN_AGE):
    # if launch_time is naive, assume UTC
    if launch_time.tzinfo is None or launch_time.tzinfo.utcoffset(launch_time) is None:
        launch_time = launch_time.replace(tzinfo=pytz.utc)
    min_age_dt = datetime.now() - timedelta(seconds=min_age)
    min_age_dt = min_age_dt.replace(tzinfo=ec2_reaper.LOCAL_TZ)
    log.info('Comparing launch_time {} to min_age_dt {}'.format(launch_time, min_age_dt))
    return (launch_time - min_age_dt).seconds


def _notify(msg, attachments=[]):
    if not SLACK_ENDPOINT:
        log.warning('Slack endpoint not configured!')
        return -1

    data = {'text': msg, 'attachements': attachments}
    headers = {'Content-Type': 'application/json'}
    r = requests.post(SLACK_ENDPOINT, json=data, headers=headers)

    if r.status_code != 200:
        log.error('Slack notification failed: (HTTP {}) {}'.format(r.status_code, r.text))

    return r.status_code


def handler(event, context):
    log.info("starting lambda_ec2_reaper at " + str(datetime.now()))

    log.debug('Filter expression set: {}'.format(TAG_MATCHER))
    log.debug('Minimum age set to {} seconds'.format(MIN_AGE))
    if not REGIONS:
        log.debug('Searching all available regions.')
    else:
        log.debug('Searching the following regions: {}'.format(REGIONS))

    reaperlog = reap(TAG_MATCHER, min_age=MIN_AGE, regions=REGIONS)

    # notify slack if anything was reaped
    reaped = [i for i in reaperlog if i['reaped']]
    log.info('{} instances reaped out of {} matched in {} regions.'.format(
        len(reaped), len(reaperlog), len(REGIONS) if REGIONS else 'all'))
    if len(reaped) > 0:
        msg = "The following instances have been terminated."
        attachments = []
        for i in reaped:
            attachments.append({
                'title': i['id'],
                'title_link': 'https://{region}.console.aws.amazon.com/ec2/v2/home?region={region}#Instances:search={id}'.format(id=i['id'], region=i['region']),
                'fields': [
                    {'title': 'Launch Time', 'value': i['launch_time'], 'short': True},
                    {'title': 'Region', 'value': i['region'], 'short': True},
                    {'title': 'Tags', 'value': i['tags'], 'short': True},
                ]
            })
        _notify(msg, attachments)

    # notify slack if anything matches but isn't old enough to be reaped
    too_young = [i for i in reaperlog if i['tag_match'] and not i['age_match'] and not i['reaped']]
    if len(too_young) > 0:
        log.info('{} instances out of {} matched were too young to reap.'.format(
            len(too_young), len(reaperlog)))

        msg = '@channel *WARNING*: The following instances are active but do not have tags. If they are left running untagged, they will be _*terminated*_.'
        attachments = []
        for i in too_young:
            attachments.append({
                'title': i['id'],
                'title_link': 'https://{region}.console.aws.amazon.com/ec2/v2/home?region={region}#Instances:search={id}'.format(id=i['id'], region=i['region']),
                'fields': [
                    {'title': 'Launch Time', 'value': i['launch_time'], 'short': True},
                    {'title': 'Expires In', 'short': True,
                        'value': "{} secs".format(_get_expires(i['launch_time']))},
                    {'title': 'Region', 'value': i['region'], 'short': True},
                    {'title': 'Tags', 'value': i['tags'], 'short': True},
                ]
            })
        _notify(msg, attachments)

    return _respond(reaperlog, error=False, status_code=200)
