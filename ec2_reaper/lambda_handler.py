from datetime import datetime, timedelta
import logging
import ec2_reaper
import requests

logger = logging.getLogger(__name__)

DEFAULT_SLACK_ENDPOINT = ''

REGIONS = os.environ.get('REGIONS', ec2_reaper.DEFAULT_REGIONS)
REGIONS = REGIONS.split(' ') if isinstance(REGIONS, str) else REGIONS
MIN_AGE = os.environ.get('MIN_AGE', ec2_reaper.DEFAULT_MIN_AGE)
TAG_MATCHER = json.loads(
    os.environ.get('TAG_MATCHER', ec2_reaper.DEFAULT_TAG_MATCHER))

SLACK_ENDPOINT = os.environ.get('SLACK_ENDPOINT', None)

DEBUG = os.environ.get('DEBUG', False)
if DEBUG:
    logger.setLevel(logging.DEBUG)
    logging.getLogger('botocore').setLevel(logging.INFO)
    logging.getLogger('boto3').setLevel(logging.INFO)
else:
    logger.setLevel(logging.INFO)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('boto3').setLevel(logging.WARNING)


def _is_py3():
    return sys.version_info >= (3, 0)

def _get_expires(launch_time, min_age=MIN_AGE):
    min_age_dt = datetime.datetime.now() - datetime.timedelta(seconds=min_age)
    min_age_dt = min_age_dt.replace(tzinfo=ec2_reaper.LOCAL_TZ)
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


def run(event, context):
    logger.info("starting lambda_ec2_reaper at " + str(datetime.now()))

    log.debug('Filter expression set: {}'.format(tagfilter))
    log.debug('Minimum age set to {} seconds'.format(min_age))
    if not regions:
        log.debug('Searching all available regions.')
    else:
        log.debug('Searching the following regions: {}'.format(regions))

    reaperlog = ec2_reaper.reap(TAG_MATCHER, min_age=MIN_AGE, regions=REGIONS)

    # notify slack if anything was reaped
    reaped = [i for i in reaperlog if i['reaped']]
    log.info('{} instances reaped out of {} matched in {} regions.'.format(
        len(reaped), len(reaperlog), len(REGIONS) if REGIONS else 'all'))
    if len(reaped) > 0:
        msg = "The following instances have been terminated."
        attachments = []
        for i in too_young:
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
                    {'title': 'Expires In', short=True,
                        'value': "{} secs".format(_get_expires(i['launch_time']))},
                    {'title': 'Region', 'value': i['region'], 'short': True},
                    {'title': 'Tags', 'value': i['tags'], 'short': True},
                ]
            })
        _notify(msg, attachments)
