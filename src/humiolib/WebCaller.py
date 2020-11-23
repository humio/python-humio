import requests
import functools
from humiolib.HumioExceptions import HumioConnectionException, HumioHTTPException, HumioTimeoutException, HumioConnectionDroppedException

HTTPError = requests.exceptions.HTTPError
ConnectionError = requests.exceptions.ConnectionError
TimeoutError = requests.exceptions.Timeout
ChunkingError = requests.exceptions.ChunkedEncodingError

class WebCaller:
    """
    Object used for abstracting calls to the Humio API
    """
    version_number_humio = "v1"

    def __init__(self, base_url):
        """
        :param base_url: URL of Humio instance.
        :type func: string
        """
        self.base_url = base_url
        self.rest_url = "{}/api/{}/".format(self.base_url, self.version_number_humio)
        self.graphql_url = "{}/graphql".format(self.base_url)


    def call_rest(self, verb, endpoint, headers=None, data=None, files=None, stream=False, **kwargs):
        """
        Call one of Humio's REST endpoints

        :param verb: Http verb
        :type verb: str
        :param endpoint: Called Humio endpoint
        :type endpoint: str
        :param headers: Http headers
        :type headers: dict, optional
        :param data: Post request body
        :type data: dict, optional
        :param files: Files to be posted
        :type files: dict, optional
        :param stream: Indicates whether a stream request should be made
        :type stream: bool, optional

        :return: Response to web request
        :rtype: Response Object
        """
        link = self.rest_url + endpoint
        return self._make_request(verb, link, headers, data, files, stream, **kwargs)

    def call_graphql(self, headers=None, data=None, **kwargs):
        """
        Call Humio's GraphQL endpoint

        :param headers: Http headers
        :type headers: dict, optional
        :param data: Post request body for GraphQL
        :type data: dict, optional

        :return: Response to web request
        :rtype: Response Object
        """
        return self._make_request("post", self.graphql_url, headers, data, **kwargs)
    
    def _make_request(self, verb, link, headers=None, data=None, files=None, stream=False, **kwargs):
        """
        Make a webrequest.
        By creating custom errors here, we ensure that calling code will not have to depend
        on the types of errors thrown by the httplibrary. Thus allowing us to more easily,
        switch out the library in the future.

        :param verb: Http verb
        :type verb: str
        :param endpoint: Called Humio endpoint
        :type endpoint: str
        :param headers: Http headers
        :type headers: dict, optional
        :param data: Post request body
        :type data: dict, optional
        :param files: Files to be posted
        :type files: dict, optional
        :param stream: Indicates whether a stream request should be made
        :type stream: bool, optional

        :return: Response to web request
        :rtype: Response Object
        """
        try:
            response = requests.request(
                verb, link, data=data, headers=headers, stream=stream, files=files, **kwargs
            )
            response.raise_for_status()
        except ConnectionError as e:
            raise HumioConnectionException(e) 
        except HTTPError as e:
            raise HumioHTTPException(e.response.text, e.response.status_code)
        except TimeoutError as e:
            raise HumioTimeoutException(e)
        
        return response

    @staticmethod
    def response_as_json(func):
        """
        Wrapper to take the raw requests responses and turn them into json

        :param func: Function to be wrapped.
        :type func: Function

        :return: Result of function, parsed into python objects from jso
        :rtype: dict
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            resp = func(*args, **kwargs)
            return resp.json()

        return wrapper


class WebStreamer():
    """
    Wrapper for a web request stream.
    Its main purpose is to catch errors during stream and raise them again as custom Humio exceptions.
    """
    def __init__(self, connection):
        """
        :param connection: Connection object created by http library.
        :type connection: Connection
        """
        self.connection = connection.iter_lines()
    
    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            return next(self.connection)
        # This error occurs during live queries, when data hasn't been streamed in a while
        except ChunkingError:
            raise HumioConnectionDroppedException("Connection to streaming socket was lost")