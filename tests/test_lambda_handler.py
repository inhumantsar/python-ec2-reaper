import logging
import json
import sys
from datetime import datetime, timedelta

from ec2_reaper import aws_lambda
from ec2_reaper import LOCAL_TZ

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.INFO)
logging.getLogger('boto3').setLevel(logging.INFO)

if sys.version_info >= (3, 0):
    from unittest.mock import patch
else:
    from mock import patch

# when no results, handler should have called reap, *not* called (slack) notify,
# and should have returned a happy response json obj,
@patch.object(aws_lambda, 'reap')
@patch.object(aws_lambda, '_notify')
def test_reap_no_results(mock_notify, mock_reap):
    mock_reap.return_value = []
    r = json.loads(aws_lambda.handler({}, {}))

    mock_notify.assert_not_called()
    mock_reap.assert_called_once()
    assert r['statusCode'] == 200
    assert r['body'] == []

# with pos and neg results, handler should have called reap,
# called (slack) notify, and should have returned a happy response json obj with
# a body which contains all found instances and N reaped and N not reaped
@patch.object(aws_lambda, 'reap')
@patch.object(aws_lambda, '_notify')
def test_reap_2neg_1pos(mock_notify, mock_reap):
    match_time = datetime.now() - timedelta(seconds=500)
    nomatch_time = datetime.now()
    mock_reap_results =  [
        {'id': 'i-11111111', 'tag_match': True, 'age_match': False, 'tags': [],
         'launch_time': nomatch_time, 'reaped': False, 'region': 'us-east-1'},
        {'id': 'i-22222222', 'tag_match': False, 'age_match': True,
         'tags': [{'Key': 'Name', 'Value': 'somename'}],
         'launch_time': match_time, 'reaped': False, 'region': 'us-east-1'},
        {'id': 'i-11111111', 'tag_match': True, 'age_match': True, 'tags': [],
         'launch_time': match_time, 'reaped': True, 'region': 'us-east-1'},
    ]
    mock_reap.return_value = mock_reap_results
    r = json.loads(aws_lambda.handler({}, {}))

    mock_notify.assert_called()
    mock_reap.assert_called_once()
    assert r['statusCode'] == 200
    assert r['body'] == json.loads(json.dumps(mock_reap_results, cls=aws_lambda.DateTimeJSONEncoder))
