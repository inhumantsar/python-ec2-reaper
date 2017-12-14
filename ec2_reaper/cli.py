# -*- coding: utf-8 -*-

"""Console script for ec2_reaper."""

import click
import json
import logging
import botocore
import sys
from datetime import datetime

log = logging.getLogger()
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
log.addHandler(ch)


try:
    import ec2_reaper
except botocore.exceptions.NoCredentialsError as e:
    log.error('boto3 was unable to find any AWS credentials. Please run `aws configure`')
    sys.exit(1)

def _is_py3():
    return sys.version_info >= (3, 0)

@click.command()
@click.argument('tagfilterstr', type=click.STRING, default=json.dumps(ec2_reaper.DEFAULT_TAG_MATCHER))
@click.option('--min-age', '-m', 'min_age', default=ec2_reaper.DEFAULT_MIN_AGE, type=click.INT,
    help='Instance must be (int)N seconds old before it will be considered for termination. Default: 300')
@click.option('--dry-run', '-d', 'dry_run', is_flag=True,
    help='Enable debug output and skip terminations.')
@click.option('--regions', '-r', type=click.STRING, multiple=True, default=ec2_reaper.DEFAULT_REGIONS,
    help='One or more regions to search. Searches all available regions by default.')
def main(tagfilterstr, min_age, dry_run, regions):
    """ec2-reaper [--min-age <seconds>] [--region region-1 --region region-2 ...] [--dry-run] <JSON filter expression>

    Terminate running instances matching tag requirements and a minimum age

    Default filter: [{"tag": "Name", "includes": [], "excludes": ["*"]}]

    Filter Behaviour:
    - An instance is reaped if tag value is in the include list
    - An instance is ignored if tag value is in the exclude list
    - Exclude overrides Include
    - `['*']` will match any value except empty for tag
    - Empty lists will match empty and missing tags.
        - eg: `{tag='Name', include=[], exclude=['*']}` will reap any instance without a 'Name' tag.
    - Instances must match *all* tag conditions if multiple are specified.
    - Stopped instances are always ignored.
    """
    if dry_run:
        log.setLevel(logging.DEBUG)
        log.warning('Dry Run mode enabled.')
        log.debug('Verbose output enabled.')
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('boto3').setLevel(logging.WARNING)

    tagfilter = json.loads(tagfilterstr)

    log.debug('Filter expression set: {}'.format(tagfilter))
    log.debug('Minimum age set to {} seconds'.format(min_age))
    if not regions:
        log.debug('Searching all available regions.')
    else:
        regions = list(regions) if isinstance(regions, tuple) else regions
        regions = regions if isinstance(regions, list) else [regions]
        regions = [r.decode('utf-8') if not _is_py3() and \
                   isinstance(r, unicode) else r for r in regions]
        log.debug('Searching the following regions: {}'.format(regions))

    log.info('Started ec2-reaper at {}'.format(datetime.now()))
    reaplog = ec2_reaper.reap(tagfilter, min_age=min_age, debug=dry_run, regions=regions)
    log.info('{} instances reaped out of {} found in {} regions.'.format(
        len([i for i in reaplog if i['reaped']]), len(reaplog),
        len(regions) if regions else 'all'))

    if len(reaplog) > 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
