
Python Humio adapter
====================

User management examples (only for local on prem install)
------------------------

```python
from humio_api.humio_api import HumioApi

# Init the API
h = HumioApi(baseUrl='https://cloud.humio.com', dataspace='<YOUR_DATASPACE>',
             token='<YOUR_TOKEN>')

# Get all users
users = h.getUserList()

# Preety print users list
HumioApi.preetyPrintJson(users)

# Get user by email
user = h.getUserByEmail('some@email.com')

# Preety print user details
HumioApi.preetyPrintJson(user)

# Create user
api.createUser('some@email.com')
```

Data ingest examples
--------------------
```python
from humio_api.humio_api import HumioApi

# Init the API
h = HumioApi(baseUrl='https://cloud.humio.com', dataspace='<YOUR_DATASPACE>',
             token='<YOUR_TOKEN>')

# some test data
jsonDt=[
    {
        "tags": {
            "host": "server1",
            "source": "application.log"
        },
        "events": [
            {
                "timestamp": "2016-06-06T12:00:00+02:00",
                "attributes": {
                    "key1": "value1",
                    "key2": "value2"
                }
            },
            {
                "timestamp": "2016-06-06T12:00:01+02:00",
                "attributes": {
                    "key1": "value1"
                }
            }
        ]
    }
]

# Ingesting the data
h.ingestJsonData(jsonDt)
```

Query examples
--------------
```python
from humio_api.humio_api import HumioApi

# Init the API
h = HumioApi(baseUrl='https://cloud.humio.com', dataspace='<YOUR_DATASPACE>',
             token='<YOUR_TOKEN>')

# creating query
queryId = h.initQuery(queryString='timechart()')
# getting query result
res = h.getQueryResult(queryId)
# printing json
HumioApi.preetyPrintJson(res)
```
