import pytest
import vcr
import os
from humiolib import HumioClient, HumioIngestClient
from humiolib.HumioExceptions import HumioHTTPException

user_token = os.environ['HUMIO_USER_TOKEN'] if 'HUMIO_USER_TOKEN' in os.environ else "bogustoken"
ingest_token = os.environ['HUMIO_INGEST_TOKEN'] if 'HUMIO_INGEST_TOKEN' in os.environ else "bogustoken"

dirname = os.path.dirname(__file__)
cassettedir = os.path.join(dirname, 'cassettes/humioclient')

# HUMIOCLIENT TESTS
@pytest.fixture
def humioclient():
    client = HumioClient(
            base_url= "https://cloud.humio.com",
            repository= "sandbox",
            user_token=user_token,
        )
    return client


@pytest.fixture
def ingestclient():
    client = HumioIngestClient(
            base_url= "https://cloud.humio.com",
            ingest_token=ingest_token,
        )
    return client

@vcr.use_cassette(cassette_library_dir=cassettedir, filter_headers=['Authorization'])
def test_create_queryjob_success(humioclient):
    queryjob = humioclient.create_queryjob("timechart()")
    assert queryjob

@vcr.use_cassette(cassette_library_dir=cassettedir, filter_headers=['Authorization'])
def test_create_queryjob_incorrect_query_syntax(humioclient):
    with pytest.raises(HumioHTTPException):
        humioclient.create_queryjob("timechart(func=nowork)")

@vcr.use_cassette(cassette_library_dir=cassettedir, filter_headers=['Authorization'])
def test_streaming_query_success(humioclient):
    result = []
    for entry in humioclient.streaming_query("timechart()"):
        result.append(entry)
    assert len(result) != 0


@vcr.use_cassette(cassette_library_dir=cassettedir, filter_headers=['Authorization'])
def test_ingest_messages_on_humioclient_success(humioclient):
    messages = [
    "192.168.1.49 - user1 [02/Nov/2017:13:48:33 +0000] \"POST /humio/api/v1/ingest/elastic-bulk HTTP/1.1\" 200 0 \"-\" \"useragent\" 0.014 657 0.014",
    "192.168.1..21 - user2 [02/Nov/2017:13:49:09 +0000] \"POST /humio/api/v1/ingest/elastic-bulk HTTP/1.1\" 200 0 \"-\" \"useragent\" 0.013 565 0.013",
    ]

    response = humioclient.ingest_messages(messages)
    assert response == {}

@vcr.use_cassette(cassette_library_dir=cassettedir, filter_headers=['Authorization'])
def test_ingest_json_on_humioclient_success(humioclient):
    data = [
        {
            "tags": {
            "host": "server1",
            "source": "application.log",
            },
            "events": [
                {
                    "timestamp": "2020-03-23T00:00:00+00:00",
                    "attributes": {
                    "key1": "value1",
                    "key2": "value2"
                    }       
                }
            ]
        }
    ]

    response = humioclient.ingest_json_data(data)
    assert response == {}

@vcr.use_cassette(cassette_library_dir=cassettedir, filter_headers=['Authorization'])
def test_get_status(humioclient):
    response = humioclient.get_status()
    assert list(response.keys()) == ["status", "version"]


# INGEST CLIENT TESTS
@vcr.use_cassette(cassette_library_dir=cassettedir, filter_headers=['Authorization'])
def test_ingest_messages_on_ingestclient_ssuccess(ingestclient):
    messages = [
    "192.168.1.49 - user1 [02/Nov/2017:13:48:33 +0000] \"POST /humio/api/v1/ingest/elastic-bulk HTTP/1.1\" 200 0 \"-\" \"useragent\" 0.014 657 0.014",
    "192.168.1..21 - user2 [02/Nov/2017:13:49:09 +0000] \"POST /humio/api/v1/ingest/elastic-bulk HTTP/1.1\" 200 0 \"-\" \"useragent\" 0.013 565 0.013",
    ]

    response = ingestclient.ingest_messages(messages)
    assert response == {}

@vcr.use_cassette(cassette_library_dir=cassettedir, filter_headers=['Authorization'])
def test_ingest_json_on_ingestclient_success(ingestclient):
    data = [
        {
            "tags": {
            "host": "server1",
            "source": "application.log",
            },
            "events": [
                {
                    "timestamp": "2020-03-23T00:00:00+00:00",
                    "attributes": {
                    "key1": "value1",
                    "key2": "value2"
                    }       
                }
            ]
        }
    ]

    response = ingestclient.ingest_json_data(data)
    assert response == {}


