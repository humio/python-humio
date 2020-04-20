import pytest
import vcr
import os
from humiolib import HumioClient
from humiolib.HumioExceptions import HumioQueryJobExhaustedException

user_token = os.environ['HUMIO_USER_TOKEN'] if 'HUMIO_USER_TOKEN' in os.environ else "bogustoken"
ingest_token = os.environ['HUMIO_INGEST_TOKEN'] if 'HUMIO_INGEST_TOKEN' in os.environ else "bogustoken"

dirname = os.path.dirname(__file__)
cassettedir = os.path.join(dirname, 'cassettes/queryjob/')

@pytest.fixture
def humioclient():
    client = HumioClient(
            base_url= "https://cloud.humio.com",
            repository= "sandbox",
            user_token=user_token,
        )
    return client

# STATIC QUERY JOB TESTS
@vcr.use_cassette(cassette_library_dir=cassettedir, filter_headers=['Authorization'])
def test_poll_until_done_static_queryjob_aggregate_query(humioclient):
    queryjob = humioclient.create_queryjob("timechart()", is_live=False)
    
    events = []
    for pollResult in queryjob.poll_until_done():
        events.extend(pollResult.events)
    
    assert len(events) != 0


@vcr.use_cassette(cassette_library_dir=cassettedir, filter_headers=['Authorization'])
def test_poll_until_done_static_queryjob_non_aggregate_query(humioclient):
    queryjob = humioclient.create_queryjob("", is_live=False)
    
    events = []
    for pollResult in queryjob.poll_until_done():
        events.extend(pollResult.events)
    
    assert len(events) != 0


@vcr.use_cassette(cassette_library_dir=cassettedir, filter_headers=['Authorization'])
def test_poll_until_done_static_queryjob_after_fully_polled_fail(humioclient):
    queryjob = humioclient.create_queryjob("timechart()", is_live=False)
    
    events = []
    for pollResult in queryjob.poll_until_done():
        events.extend(pollResult.events)

    with pytest.raises(HumioQueryJobExhaustedException):
        for pollResult in queryjob.poll_until_done():
            events.extend(pollResult.events)


# LIVE QUERY JOB TESTS
@vcr.use_cassette(cassette_library_dir=cassettedir, filter_headers=['Authorization'])
def test_poll_until_done_live_queryjob_aggregate_query(humioclient):
    queryjob = humioclient.create_queryjob("timechart()", is_live=True)
    
    events = []
    for poll_events in queryjob.poll().events:
        events.extend(poll_events)
    
    assert len(events) != 0

@vcr.use_cassette(cassette_library_dir=cassettedir, filter_headers=['Authorization'])
def test_poll_until_done_live_queryjob_non_aggregate_query(humioclient):
    queryjob = humioclient.create_queryjob("", is_live=True)
    
    events = []
    for poll_events in queryjob.poll().events:
        events.extend(poll_events)
    
    assert len(events) != 0

@vcr.use_cassette(cassette_library_dir=cassettedir, filter_headers=['Authorization'])
def test_poll_until_done_live_queryjob_poll_after_done_success(humioclient):
    queryjob = humioclient.create_queryjob("timechart()", is_live=True)
    
    first_poll_events = []
    for poll_events in queryjob.poll().events:
        first_poll_events.extend(poll_events)

    second_poll_events = []
    for poll_events in queryjob.poll().events:
        second_poll_events.extend(poll_events)
        
    assert len(second_poll_events) != 0