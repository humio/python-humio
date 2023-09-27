import requests
import json
from humiolib.WebCaller import WebCaller, WebStreamer
from humiolib.QueryJob import StaticQueryJob, LiveQueryJob
from humiolib.HumioExceptions import HumioConnectionException


class BaseHumioClient():
    """
    Base class for other client types, is not meant to be instantiated
    """

    def __init__(self, base_url):
        self.base_url = base_url
        self.webcaller = WebCaller(self.base_url)

    @classmethod
    def _from_saved_state(cls, state_dump):
        """
        Creates an instance of this class from a saved state

        :param state_dump: json string describing this object.
        :type state_dump: str

        :return: An instance of this class
        :rtype: BaseHumioClient
        """
        data = json.loads(state_dump)
        instance = cls(**data)
        return instance

    @staticmethod
    def _create_unstructured_data_object(messages, parser=None, fields=None, tags=None):
        """
        Creates a data object that can be sent to Humio's unstructured ingest endpoints

        :param messages: A list of event strings.
        :type messages: list(string)
        :param parser: A list of event strings.
        :type parser: string, optional
        :param fields: Fields that should be added to events after parsing
        :type fields: (dict(string->string)), optional
        :param tags: Tags to associate with the messages
        :type tags: (dict(string->string)), optional

        :return: A data object fit to be sent as unstructured ingest payload
        :rtype: dict
        """
        return dict(
            (k, v)
            for k, v in [
                ("messages", messages),
                ("type", parser),
                ("fields", fields),
                ("tags", tags),
            ]
            if v is not None
        )


class HumioClient(BaseHumioClient):
    """
    A Humio client that gives full access to the underlying API.
    While this client can be used for ingesting data,
    we recommend using the HumioIngestClient made exclusivly for ingestion.
    """

    def __init__(
        self,
        repository,
        user_token,
        base_url="http://localhost:3000",
    ):
        """
        :param repository: Repository associated with client
        :type repository: str
        :param user_token: User token to get access to repository
        :type user_token: str
        :param base_url: Url of Humio instance
        :type repository: str
        """
        super().__init__(base_url)
        self.repository = repository
        self.user_token = user_token

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

    @property
    def _state(self):
        """
        :return: State of all field variables
        :rtype: dict
        """
        return json.dumps(
            {
                "user_token": self.user_token,
                "repository": self.repository,
                "base_url": self.base_url,
            }
        )

    def _streaming_query(
        self,
        query_string,
        start=None,
        end=None,
        is_live=None,
        timezone_offset_minutes=None,
        arguments=None,
        raw_data=None,
        media_type="application/x-ndjson",
        **kwargs
    ):
        """
        Method wrapped by streaming_query to perform a Humio streaming Query.

        :return: An iterable that contains query results from stream as raw strings
        :rtype: Webstreamer
        """

        if raw_data is None:
            raw_data = {}

        endpoint = "dataspaces/{}/query".format(self.repository)

        headers = self._default_user_headers
        headers["Accept"] = media_type
        headers.update(kwargs.pop("headers", {}))

        data = dict(
            (k, v)
            for k, v in [
                ("queryString", query_string),
                ("start", start),
                ("end", end),
                ("isLive", is_live),
                ("timeZoneOffsetMinutes", timezone_offset_minutes),
                ("arguments", arguments),
            ]
            if v is not None
        )

        data.update(raw_data)

        connection = self.webcaller.call_rest(
            "post", endpoint, data=json.dumps(data), headers=headers, stream=True, **kwargs
        )

        return WebStreamer(connection)

    # Wrap method to be pythonic
    def streaming_query(
        self,
        query_string,
        start=None,
        end=None,
        is_live=None,
        timezone_offset_minutes=None,
        arguments=None,
        raw_data=None,
        **kwargs
    ):
        """
        Humio Query type that opens up a streaming socket connection to Humio.
        This is the preferred way to do static queries with large result sizes.
        It can be used for live queries, but not that if data is not passed back from
        Humio for a while, the connection will be lost, resulting in an error.

        :param query_string: Humio query
        :type query_string: str
        :param start: Starting time of query
        :type start: Union[int, str], optional
        :param end: Ending time of query
        :type end: Union[int, str], optional
        :param is_live: Ending time of query
        :type is_live: bool, optional
        :param timezone_offset_minutes: Timezone offset in minutes
        :type timezone_offset_minutes: int, optional
        :param argument: Arguments specified in query
        :type argument: dict(string->string), optional
        :param raw_data: Additional arguments to add to POST body under other keys
        :type raw_data: dict(string->string), optional

        :return: A generator that returns query results as python objects
        :rtype: Generator
        """

        media_type = "application/x-ndjson"
        encoding = "utf-8"

        res = self._streaming_query(
            query_string=query_string,
            start=start,
            end=end,
            is_live=is_live,
            timezone_offset_minutes=timezone_offset_minutes,
            arguments=arguments,
            media_type=media_type,
            raw_data=raw_data,
            **kwargs
        )

        for event in res:
            yield json.loads(event.decode(encoding))

    def create_queryjob(
        self,
        query_string,
        start=None,
        end=None,
        is_live=None,
        timezone_offset_minutes=None,
        arguments=None,
        raw_data=None,
        **kwargs
    ):
        """
        Creates a queryjob on Humio, which executes asynchronously of the calling code.
        The returned QueryJob instance can be used to get the query results at a later time.
        Queryjobs are good to use for live queries, or static queries that return smaller
        amounts of data.

        :param query_string: Humio query
        :type query_string: str
        :param start: Starting time of query
        :type start: Union[int, str], optional
        :param end: Ending time of query
        :type end: Union[int, str], optional
        :param is_live: Ending time of query
        :type is_live: bool, optional
        :param is_live: Timezone offset in minutes
        :type is_live: int, optional
        :param argument: Arguments specified in query
        :type argument: dict(string->string), optional
        :param raw_data: Additional arguments to add to POST body under other keys
        :type raw_data: dict(string->string), optional

        :return:  An instance that grants access to the created queryjob and associated results
        :rtype: QueryJob
        """

        endpoint = "dataspaces/{}/queryjobs".format(self.repository)

        headers = self._default_user_headers
        headers.update(kwargs.pop("headers", {}))

        data = dict(
            (k, v)
            for k, v in [
                ("queryString", query_string),
                ("start", start),
                ("end", end),
                ("isLive", is_live),
                ("timeZoneOffsetMinutes", timezone_offset_minutes),
                ("arguments", arguments),
            ]
            if v is not None
        )

        if raw_data is not None:
            data.update(raw_data)

        query_id = self.webcaller.call_rest(
            "post", endpoint, data=json.dumps(data), headers=headers, **kwargs
        ).json()['id']

        if is_live:
            return LiveQueryJob(query_id, self.base_url, self.repository, self.user_token)
        else:
            return StaticQueryJob(query_id, self.base_url, self.repository, self.user_token)

    def _ingest_json_data(self, json_elements=None, **kwargs):
        """
        Ingest structured json data to repository.
        Structure of ingested data is discussed in: https://docs.humio.com/reference/api/ingest/#structured-data

        :param messages: A list of event strings.
        :type messages: list(string), optional
        :param parser:  Name of parser to use on messages.
        :type parser: string, optional
        :param fields:  Fields that should be added to events after parsing.
        :type fields: dict(string->string), optional
        :param tags:  Tags to associate with the messages.
        :type tags: dict(string->string), optional

        :return: Response to web request as json string
        :rtype: str
        """

        if json_elements is None:
            json_elements = []

        headers = self._default_user_headers
        headers.update(kwargs.pop("headers", {}))

        endpoint = "dataspaces/{}/ingest".format(self.repository)

        return self.webcaller.call_rest(
            "post", endpoint, data=json.dumps(json_elements), headers=headers, **kwargs
        )

    # Wrap method to be pythonic
    ingest_json_data = WebCaller.response_as_json(_ingest_json_data)

    def _ingest_messages(
        self, messages=None, parser=None, fields=None, tags=None, **kwargs
    ):
        """
        Ingest unstructred messages to repository.
        Structure of ingested data is discussed in: https://docs.humio.com/reference/api/ingest/#parser

        :param messages: A list of event strings.
        :type messages: list(string), optional
        :param parser:  Name of parser to use on messages.
        :type parser: string, optional
        :param fields:  Fields that should be added to events after parsing.
        :type fields: dict(string->string), optional
        :param tags:  Tags to associate with the messages.
        :type tags: dict(string->string), optional

        :return: Response to web request as json string
        :rtype: str
        """
        if messages is None:
            messages = []

        headers = self._default_user_headers
        headers.update(kwargs.pop("headers", {}))

        endpoint = "dataspaces/{}/ingest-messages".format(self.repository)

        obj = self._create_unstructured_data_object(
            messages, parser=parser, fields=fields, tags=tags
        )

        return self.webcaller.call_rest(
            "post", endpoint, data=json.dumps([obj]), headers=headers, **kwargs
        )

    # Wrap method to be pythonic
    ingest_messages = WebCaller.response_as_json(_ingest_messages)

    # status
    def _get_status(self, **kwargs):
        """
        Gets status of Humio instance

        :return: Response to web request as json string
        :rtype: str
        """
        endpoint = "status"
        return self.webcaller.call_rest("get", endpoint, **kwargs)

    # Wrap method to be pythonic
    get_status = WebCaller.response_as_json(_get_status)

    # user management
    def _get_users(self):
        """
        Gets users registered to Humio instance

        :return: Response to web request as json string
        :rtype: str
        """
        endpoint = "users"
        return self.webcaller.call_rest("get", endpoint, headers=self._default_user_headers)

    # Wrap method to be pythonic
    get_users = WebCaller.response_as_json(_get_users)

    def get_user_by_email(self, email):
        """
        Get a user associated with Humio instance by email

        :param email: Email of queried user
        :type email: str

        :return: Response to web request as json string
        :rtype: str
        """
        user_list = self.get_users()
        for user in user_list:
            if email == user["email"]:
                return user
        return None

    def _create_user(self, email, isRoot=False):
        """
        Create user on Humio instance. Method is idempotent

        :param email: Email of user to create
        :type email: str
        :param isRoot: Indicates whether user should be root
        :type isRoot: bool, optional

        :return: Response to web request as json string
        :rtype: str
        """

        endpoint = "users"

        data = {"email": email, "isRoot": isRoot}

        return self.webcaller.call_rest(
            "post", endpoint, data=json.dumps(data), headers=self._default_user_headers
        )

    # Wrap method to be pythonic
    create_user = WebCaller.response_as_json(_create_user)

    def _delete_user_by_id(self, user_id):
        """
        Delete user from Humio instance.

        :param user_id: Id of user to delete.
        :type user_id: string

        :return: Response to web request as json string
        :rtype: str
        """

        link = "users/{}".format(user_id)

        return self.webcaller.call_rest("delete", link, headers=self._default_user_headers)

    # Wrap method to be pythonic
    delete_user_by_id = WebCaller.response_as_json(_delete_user_by_id)

    def delete_user_by_email(self, email):
        """
        Delete user by email.

        :param email: Email of user to delete.
        :type email: string

        :return: Response to web request as json string
        :rtype: str
        """
        for user in self.get_users():
            if email == user["email"]:
                return self.delete_user_by_id(user["userID"])
        return None

    # organizations
    def _list_organizations(self):
        """
        List organizations.

        :return: Response to web request as json string
        :rtype: str
        """

        headers = self._default_user_headers
        request = {
            "query": "query {organizations{id, name, description}}",
            "variables": None,
        }

        return self.webcaller.call_graphql(headers=headers, data=json.dumps(request))

    # Wrap method to be pythonic
    def list_organizations(self):
        resp = self._list_organizations()
        return resp.json()["data"]["organizations"]

    def _create_organization(self, name, description):
        """
        Create new organiztion.

        :param name: Name of organization.
        :type name: string
        :param description: Description of organization.
        :type description: string

        :return: Response to web request as json string
        :rtype: str
        """

        headers = self._default_user_headers
        request = {
            "query": "mutation($name: String!, $description: String!){createOrganization(name: $name, description: $description){organization{id}}}",
            "variables": {"name": name, "description": description},
        }
        return self.webcaller.call_graphql(headers=headers, data=json.dumps(request))

    # Wrap method to be pythonic
    def create_organization(self, name, description):
        resp = self._create_organization(name, description)
        return resp.json()["data"]

    # files API
    def _upload_file(self, filepath):
        """
        Upload file to repository

        :param filepath: Path to file.
        :type filepath: string

        :return: Response to web request
        :rtype: Response Object
        """

        endpoint = "dataspaces/{}/files".format(self.repository)
        headers = {"Authorization": "Bearer {}".format(self.user_token)}  # Not using default headers as files are sent
        with open(filepath, "rb") as f:
            return self.webcaller.call_rest("post", endpoint, files={"file": f}, headers=headers)

    # Wrap method to be pythonic
    # The uploaded files endpoint currently doesn't return JSON, thus this function doesn't attempt to cast to json.
    def upload_file(self, filepath):
        return self._upload_file(filepath)

    def _create_file(self, file_name):
        """
        Create new file.

        :param file_name: Name of file
        :type file_name: string

        :return: Response to web request
        :rtype: Response Object
        """

        headers = self._default_user_headers
        request = {
            "query": "mutation($fileName : String!, $repo : String!){newFile(fileName: $fileName, name: $repo){nameAndPath { name, path}}}",
            "variables": {"fileName": file_name, "repo": self.repository},
        }
        return self.webcaller.call_graphql(headers=headers, data=json.dumps(request))

    def create_file(self, file_name):
        """
        Create new file.

        :param file_name: Name of file
        :type file_name: string

        :return: Response data to web request as json string
        :rtype: str
        """

        resp = self._create_file(file_name)
        return resp.json()["data"]

    def _list_files(self):
        """
        List uploaded files on repository

        :return: Response to web request
        :rtype: Response Object
        """

        headers = self._default_user_headers
        request = {
            "query": "query {{searchDomain(name: {}){{files {{nameAndPath {{path, name}} }} }} }}".format(
                json.dumps(self.repository)
            ),
            "variables": None,
        }
        return self.webcaller.call_graphql(headers=headers, data=json.dumps(request))

    def list_files(self):
        """
        List uploaded files on repository

        :return: Response to web request as json string
        :rtype: str
        """

        resp = self._list_files()
        return resp.json()["data"]["searchDomain"]["files"]

    def _get_file_content(self, file_name, offset, limit, filter_string=None):
        """
        Get the contents of a file

        :param file_name: Name of file.
        :type name: string

        :param offset: Starting index to replace the old rows with the updated ones.
        :type offset: int

        :param limit: Used to find when to stop replacing rows, by adding the limit to the offset
        :type limit: int

        :param filter_string: Used to apply a filter string
        :type filter_string: string, optional

        :return: Response to web request
        :rtype: Response Object
        """

        headers = self._default_user_headers

        if filter_string is not None:
            request = {
                "query": "query {{"
                            "getFileContent(name: {}, fileName: \"{}\", offset: {}, limit: {}, filterString: \"{}\") {{ "
                                "totalLinesCount, limit, offset, headers, lines}} "
                            "}}".format(json.dumps(self.repository), file_name, offset, limit, filter_string),
                "variables": None,
            }
        else:
            request = {
                "query": "query {{"
                            "getFileContent(name: {}, fileName: \"{}\", offset: {}, limit: {}) {{ "
                                "totalLinesCount, limit, offset, headers, lines}} "
                            "}}".format(json.dumps(self.repository), file_name, offset, limit),
                "variables": None,
            }

        return self.webcaller.call_graphql(headers=headers, data=json.dumps(request))

    def get_file_content(self, filename, offset=0, limit=200, filter_string=None):
        """
        Get the contents of a file

        :param file_name: Name of file.
        :type name: string

        :param offset: Starting index to replace the old rows with the updated ones.
        :type offset: int

        :param limit: Used to find when to stop replacing rows, by adding the limit to the offset
        :type limit: int

        :param filter_string: Used to apply a filter string
        :type filter_string: string, optional

        :return: Response to web request as json string
        :rtype: str
        """

        resp = self._get_file_content(filename, offset=offset, limit=limit, filter_string=filter_string)
        return resp.json()["data"]

    def _get_file(self, file_name):
        """
        Get specific file on repository

        :param file_name: Name of file to get.
        :type file_name: string

        :return: Response to web request as json string
        :rtype: Response Object
        """
        endpoint = "dataspaces/{}/files/{}".format(self.repository, file_name)
        headers = {"Authorization": "Bearer {}".format(self.user_token)}  # Not using default headers as files are sent
        return self.webcaller.call_rest("get", endpoint, headers=headers)

    def get_file(self, file_name, encoding=None):
        """
        Get specific file on repository

        :param file_name: Name of file to get.
        :type file_name: string

        :return: Response to web request as json string
        :rtype: str
        """
        resp = self._get_file(file_name)
        raw_data = resp.content
        if encoding is None:
            return raw_data
        else:
            return raw_data.decode("utf-8")

    def _delete_file(self, file_name):
        """
        Delete an existing file.

        :param file_name: Name of file
        :type file_name: string

        :return: Response to web request
        :rtype: Response Object
        """

        headers = self._default_user_headers
        request = {
            "query": "mutation($fileName : String!, $repo : String!){removeFile(fileName: $fileName, name: $repo){ __typename}}",
            "variables": {"fileName": file_name, "repo": self.repository},
        }
        return self.webcaller.call_graphql(headers=headers, data=json.dumps(request))

    def delete_file(self, file_name):
        """
        Delete an existing file.

        :param file_name: Name of file
        :type file_name: string

        :return: Response to web request as json string
        :rtype: str
        """

        resp = self._delete_file(file_name)
        return resp.json()["data"]

    def _update_file_contents(self, file_name, file_headers, changed_rows, column_changes=[], offset=0, limit=200):
        """
        Add contents to a file

        :param file_name: Name of file
        :type file_name: string

        :param file_headers: Headers of the file
        :type file_headers: list

        :param changed_rows: Rows within the offset and limit to overwrite existing rows
        :type changed_rows: list

        :param column_changes: Column changes that will be applied to all rows in the file
        :type column_changes: list, optional

        :param offset: Starting index to replace the old rows with the updated ones.
        :type offset: int, optional

        :param limit: Used to find when to stop adding rows, by adding the limit to the offset
        :type limit: int, optional

        :return: Response data to web request
        :rtype: Response Object
        """

        headers = self._default_user_headers
        request = {
            "query": "mutation ($fileName: String!, $name: String!, $changedRows: [[String!]!]!, $headers: [String!]!, $columnChanges: [ColumnChange!]!, $limit: Int, $offset: Int) {updateFile(limit: $limit, offset: $offset, fileName: $fileName, name: $name, changedRows: $changedRows, headers: $headers, columnChanges: $columnChanges) {offset, limit, totalLinesCount, headers, lines, nameAndPath {name, path } } }",
            "variables": {"name": self.repository, "fileName": file_name, "changedRows": changed_rows,
                          "headers": file_headers,
                          "columnChanges": column_changes, "offset": offset, "limit": limit}
        }

        return self.webcaller.call_graphql(headers=headers, data=json.dumps(request))

    def add_file_contents(self, file_name, file_headers, changed_rows, column_changes=[], offset=0, limit=200):
        """
        Add contents to a file

        :param file_name: Name of file
        :type file_name: string

        :param file_headers: Headers of the file
        :type file_headers: list

        :param changed_rows: Rows within the offset and limit to overwrite existing rows
        :type changed_rows: list

        :param column_changes: Column changes that will be applied to all rows in the file
        :type column_changes: list, optional

        :param offset: Starting index to replace the old rows with the updated ones.
        :type offset: int, optional

        :param limit: Used to determine when to stop replacing rows, by adding the limit to the offset
        :type limit: int, optional

        :return: Response data to web request as json string
        :rtype: str
        """

        resp = self._update_file_contents(file_name, file_headers, changed_rows, column_changes, offset, limit)
        return resp.json()["data"]

    def remove_file_contents(self, file_name, offset=0, limit=200):
        """
        Remove contents of a file

        :param file_name: Name of file
        :type file_name: string

        :param offset: Starting index to replace the old rows with the updated ones.
        :type offset: int, optional

        :param limit: Used to find when to stop replacing rows, by adding the limit to the offset
        :type limit: int, optional

        :return: Response data to web request as json string
        :rtype: str
        """

        resp = self._update_file_contents(file_name, file_headers=[], offset=offset, limit=limit, changed_rows=[],
                                          column_changes=[])
        return resp.json()["data"]

    def _create_saved_query(self, query_name, query_string):
        """
        Create new saved query in the current repository.

        :param query_name: Name of saved query
        :type query_name: string

        :param query_string: Saved query content
        :type query_string: string

        :return: Response to web request
        :rtype: Response Object
        """

        headers = self._default_user_headers
        request = {
            "query": "mutation($input : CreateSavedQueryInput!){createSavedQuery(input: $input){savedQuery{id, name}}}",
            "variables": {"input": {"name": query_name, "viewName": self.repository, "queryString": query_string}},
        }
        return self.webcaller.call_graphql(headers=headers, data=json.dumps(request))

    def create_saved_query(self, query_name, query_string):
        """
        Create new saved query in the current repository.

        :param query_name: Name of saved query
        :type query_name: string

        :param query_string: Saved query content
        :type query_string: string

        :return: Response data to web request as json string
        :rtype: str
        """

        resp = self._create_saved_query(query_name, query_string)
        return resp.json()["data"]

    def _list_saved_queries(self):
        """
        List saved queries on repository

        :return: Response to web request
        :rtype: Response Object
        """

        headers = self._default_user_headers
        request = {
            "query": "query {{repository(name: {}){{savedQueries {{ id, name, displayName, query {{queryString}} }} }} }}".format(
                json.dumps(self.repository)
            ),
            "variables": None,
        }
        return self.webcaller.call_graphql(headers=headers, data=json.dumps(request))

    def list_saved_queries(self):
        """
        List saved queries on repository

        :return: Response to web request as json string
        :rtype: str
        """

        resp = self._list_saved_queries()
        return resp.json()["data"]["repository"]["savedQueries"]

    def _update_saved_query(self, query_id, updated_query_name,  updated_query_string):
        """
        Update the saved query with the given id in the current repository.

        :param query_id: ID of saved query to update
        :type query_id: string

        :param updated_query_name: Updated name of saved query
        :type updated_query_name: string

        :param updated_query_string: Updated content of the saved query
        :type updated_query_string: string

        :return: Response to web request
        :rtype: Response Object
        """

        headers = self._default_user_headers
        request = {
            "query": "mutation($input : UpdateSavedQueryInput!){updateSavedQuery(input: $input){savedQuery{id, name}}}",
            "variables": {"input": {"id": query_id, "name": updated_query_name, "viewName": self.repository, "queryString": updated_query_string}},
        }
        return self.webcaller.call_graphql(headers=headers, data=json.dumps(request))

    def update_saved_query(self, query_id, updated_query_name,  updated_query_string):
        """
        Update the saved query with the given id in the current repository.

        :param query_id: ID of saved query to update
        :type query_id: string

        :param updated_query_name: Updated name of saved query
        :type updated_query_name: string

        :param updated_query_string: Updated content of the saved query
        :type updated_query_string: string

        :return: Response data to web request as json string
        :rtype: str
        """

        resp = self._update_saved_query(query_id, updated_query_name, updated_query_string)
        return resp.json()["data"]

    def _delete_saved_query(self, query_id):
        """
        Delete the saved query with the given id from the current repository.

        :param query_id: ID of saved query to update
        :type query_id: string

        :return: Response to web request
        :rtype: Response Object
        """

        headers = self._default_user_headers
        request = {
            "query": "mutation($input : DeleteSavedQueryInput!){deleteSavedQuery(input: $input){savedQuery{id, name}}}",
            "variables": {"input": {"id": query_id, "viewName": self.repository}},
        }
        return self.webcaller.call_graphql(headers=headers, data=json.dumps(request))

    def delete_saved_query(self, query_id):
        """
        Delete the saved query with the given id from the current repository.

        :param query_id: ID of saved query to update
        :type query_id: string

        :return: Response data to web request as json string
        :rtype: str
        """

        resp = self._delete_saved_query(query_id)
        return resp.json()["data"]

class HumioIngestClient(BaseHumioClient):
    """
    A Humio client that is used exclusivly for ingesting data
    """

    def __init__(
        self,
        ingest_token,
        base_url="http://localhost:3000",
    ):
        """
        :param ingest_token: Ingest token to access ingest.
        :type ingest_token: string
        :param base_url: Url of Humio instance.
        :type base_url: string
        """
        super().__init__(base_url)
        self.ingest_token = ingest_token
        self.webcaller = WebCaller(self.base_url)

    @property
    def _default_ingest_headers(self):
        """
        :return: Default headers used for web requests
        :rtype: dict
        """

        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.ingest_token),
        }

    @property
    def _state(self):
        """
        :return: State of all field variables
        :rtype: dict
        """

        return json.dumps(
            {
                "base_url": self.base_url,
                "ingest_token": self.ingest_token,
            }
        )

    def _ingest_json_data(self, json_elements=None, **kwargs):
        """
        Ingest structured json data to repository.
        Structure of ingested data is discussed in: https://docs.humio.com/reference/api/ingest/#structured-data

        :param json_elements: Structured data that can be parsed to a json string.
        :type json_elements: str

        :return: Response to web request as json string
        :rtype: str
        """

        if json_elements is None:
            json_elements = []

        headers = self._default_ingest_headers
        headers.update(kwargs.pop("headers", {}))

        endpoint = "ingest/humio-structured"

        return self.webcaller.call_rest(
            "post", endpoint, data=json.dumps(json_elements), headers=headers, **kwargs
        )

    # Wrap method to be pythonic
    ingest_json_data = WebCaller.response_as_json(_ingest_json_data)

    def _ingest_messages(
        self, messages=None, parser=None, fields=None, tags=None, **kwargs
    ):
        """
        Ingest unstructred messages to repository.
        Structure of ingested data is discussed in: https://docs.humio.com/reference/api/ingest/#parser

        :param messages: A list of event strings.
        :type messages: list(string), optional
        :param parser:  Name of parser to use on messages.
        :type parser: string, optional
        :param fields:  Fields that should be added to events after parsing.
        :type fields: dict(string->string), optional
        :param tags:  Tags to associate with the messages.
        :type tags: dict(string->string), optional

        :return: Response to web request as json string
        :rtype: str
        """

        if messages is None:
            messages = []

        headers = self._default_ingest_headers
        headers.update(kwargs.pop("headers", {}))

        endpoint = "ingest/humio-unstructured"

        obj = self._create_unstructured_data_object(
            messages, parser=parser, fields=fields, tags=tags
        )

        return self.webcaller.call_rest("post", endpoint, data=json.dumps([obj]), headers=headers)

    # Wrap method to be pythonic
    ingest_messages = WebCaller.response_as_json(_ingest_messages)
