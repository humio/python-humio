import requests
import time
from humiolib.HumioExceptions import HumioQueryJobExhaustedException, HumioHTTPException, HumioQueryJobExpiredException
from humiolib.WebCaller import WebCaller

class PollResult():
    """
    Result of polling segments of queryjob results.
    We choose to return these clusters of data, rather than just a list of events,
    as the metadata returned changes between polls.
    """
    def __init__(self, events, metadata):
        self.events = events
        self.metadata = metadata
    

class BaseQueryJob():
    """
    Base QueryJob class, not meant to be instantiated.
    This class and its children manage access to queryjobs created on a Humio instance,
    they are mainly used for extracting results from queryjobs.
    """
    def __init__(self, query_id, base_url, repository, user_token):
        """
        Parameters:
        query_id (string): Id of queryjob
        base_url (string): Url of Humio instance
        repository (string): Repository being queried
        user_token (string): Token used to access resource
        """
        self.query_id = query_id
        self.segment_is_done = False
        self.segment_is_cancelled = False
        self.more_segments_can_be_polled = True
        self.time_at_last_poll = 0
        self.wait_time_until_next_poll = 0
        self.base_url = base_url
        self.repository = repository
        self.user_token = user_token
        self.webcaller = WebCaller(self.base_url)

    @property
    def _default_user_headers(self):
        """ 
        :return: Default headers used for web requests
        :rtype: dict
        """
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.user_token),
        }


    def _wait_till_next_poll(self):
        """
        A potentially blocking operation, that waits until the queryjob may be polled again.
        This will always pass on the first poll to the queryjob.
        """
        time_since_last_poll = time.time() - self.time_at_last_poll
        if(time_since_last_poll < self.wait_time_until_next_poll):
            time.sleep((self.wait_time_until_next_poll - time_since_last_poll) / 1000.0) 

    def _fetch_next_segment(self, link, headers, **kwargs):
        """
        Polls the queryjob for the next segment of data. 
        May block, if the queryjob is not ready to be polled again.

        :param link: url to access queryjob.
        :type link: str
        :param headers: headers used for web request.
        :type headers: list(dict)

        :return: A data object that contains events of the polled segment and metadata about the poll
        :rtype: PollResult
        """
        self._wait_till_next_poll()
        
        try:
            response =  self.webcaller.call_rest("get", link, headers=headers, **kwargs).json()
        except HumioHTTPException as e:
            # In the case that the queryjob has expired, a custom exception is thrown.
            # The calling code must itself decide how to respond to the error.
            # It has been considered whether this instance should simply restart the queryjob automatically,
            # but that would require the calling code to handle cases where
            # a queryjob restart returns previously received query results.
            if e.status_code == 404:
                raise HumioQueryJobExpiredException(e.message)
            else:
                raise e

        self.wait_time_until_next_poll = response["metaData"]["pollAfter"]
        self.segment_is_done = response["done"] 
        self.segment_is_cancelled = response["cancelled"]
        self.time_at_last_poll = time.time()

        return PollResult(response["events"], response["metaData"])

    def _is_streaming_query(self, metadata):
        """
        Checks whether the query is a streaming query and not an aggregate

        :param metaData: query response metadata.
        :type metadata: dict

        :return: Answer to whether query is of type streaming
        :rtype: Bool
        """
        return not metadata["isAggregate"]

    def poll(self, **kwargs):
        """
        Polls the queryjob for the next segment of data, and handles edge cases for data polled

        :return: A data object that contains events of the polled segment and metadata about the poll
        :rtype: PollResult
        """
        link = "dataspaces/{}/queryjobs/{}".format(self.repository, self.query_id)

        headers = self._default_user_headers
        headers.update(kwargs.pop("headers", {}))

        poll_result = self._fetch_next_segment(link, headers, **kwargs)
        while not self.segment_is_done: # In case the segment hasn't been completed, we poll until is is
            poll_result = self._fetch_next_segment(link, headers, **kwargs)
    
        if self._is_streaming_query(poll_result.metadata):
            self.more_segments_can_be_polled = poll_result.metadata["extraData"]["hasMoreEvents"] == 'true'
        else: # is aggregate query
            self.more_segments_can_be_polled = False

        return poll_result


class StaticQueryJob(BaseQueryJob):
    """
    Manages a static queryjob
    """
    def __init__(self, query_id, base_url, repository, user_token):
        """
        :param query_id: Id of queryjob.
        :type query_id: str
        :param base_url: Url of Humio instance.
        :type base_url: str
        :param repository:  Repository being queried.
        :type repository: str
        :param user_token: Token used to access resource.
        :type user_token: str
        """
        super().__init__(query_id, base_url, repository, user_token)

    def poll(self, **kwargs):
        """
        Polls next segment of result

        :return: A data object that contains events of the polled segment and metadata about the poll
        :rtype: PollResult
        """
        if not self.more_segments_can_be_polled:
            raise HumioQueryJobExhaustedException()
        
        return super().poll(**kwargs)

    def poll_until_done(self, **kwargs):
        """
        Create generator for yielding poll results

        :return: A generator for query results
        :rtype: Generator
        """

        yield self.poll(**kwargs)
        while self.more_segments_can_be_polled:
            yield self.poll(**kwargs)


class LiveQueryJob(BaseQueryJob):
    """
    Manages a live queryjob
    """
    def __init__(self, query_id, base_url, repository, user_token):
        """
        :param query_id: Id of queryjob.
        :type query_id: str
        :param base_url: Url of Humio instance.
        :type base_url: str
        :param repository:  Repository being queried.
        :type repository: str
        :param user_token: Token used to access resource.
        :type user_token: str
        """
        super().__init__(query_id, base_url, repository, user_token)
    
    def __del__(self):
        """
        Delete queryjob, when this object is deconstructed.
        As live queryjobs are kept around for 1 hours after last query,
        it'd be best to delete them when not in use.
        """
        try:
            headers = self._default_user_headers
            endpoint = "dataspaces/{}/queryjobs/{}".format(self.repository, self.query_id)
            self.webcaller.call_rest("delete", endpoint, headers)
        except HumioHTTPException: # If the queryjob doesn't exists anymore, we don't want to halt on the exception
            pass 
